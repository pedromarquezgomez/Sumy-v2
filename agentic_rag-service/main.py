import os
import json
import logging
from typing import List, Dict, Any
from fastapi import FastAPI, Body, HTTPException
from pydantic import BaseModel
import chromadb
from sentence_transformers import SentenceTransformer
from pathlib import Path

# Configuración
logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
logger = logging.getLogger(__name__)

# Modelos Pydantic
class QueryRequest(BaseModel):
    query: str
    max_results: int = 3

class RAGService:
    """Servicio RAG que gestiona embeddings y búsqueda semántica."""
    def __init__(self):
        logger.info("Inicializando RAG Service...")
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.client = chromadb.EphemeralClient()
        self.collection = self.client.get_or_create_collection(
            name="wine_knowledge_v2",
            metadata={"hnsw:space": "cosine"}
        )
        self._load_initial_data()

    def _process_enology_simple(self, text_path: Path):
        """Procesa el texto de maestría enológica con estrategia simple por párrafos."""
        logger.info(f"📖 Procesando maestría enológica desde {text_path}...")
        
        try:
            with open(text_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Dividir por párrafos dobles (estrategia más simple)
            paragraphs = content.split('\n\n')
            
            ids_to_add, docs_to_add, metas_to_add = [], [], []
            existing_ids = set(self.collection.get(include=[])['ids'])
            
            chunk_count = 0
            for paragraph in paragraphs:
                paragraph = paragraph.strip()
                
                # Solo procesar párrafos con contenido sustancial
                if len(paragraph) > 100:  # Mínimo 100 caracteres
                    chunk_id = f"enologia_paragraph_{chunk_count}"
                    
                    if chunk_id not in existing_ids:
                        # Si el párrafo es muy largo (>800 chars), dividirlo por oraciones
                        if len(paragraph) > 800:
                            sentences = paragraph.replace('. ', '.\n').split('\n')
                            current_text = ""
                            
                            for sentence in sentences:
                                sentence = sentence.strip()
                                if len(current_text + sentence) > 800 and current_text:
                                    # Guardar chunk actual
                                    sub_chunk_id = f"enologia_paragraph_{chunk_count}_part"
                                    metadata = {
                                        'type': 'knowledge',
                                        'category': 'enologia',
                                        'chunk_type': 'paragraph_split',
                                        'estimated_chars': len(current_text)
                                    }
                                    
                                    ids_to_add.append(sub_chunk_id)
                                    docs_to_add.append(current_text.strip())
                                    metas_to_add.append(metadata)
                                    
                                    chunk_count += 1
                                    current_text = sentence + " "
                                else:
                                    current_text += sentence + " "
                            
                            # Añadir último fragmento si existe
                            if current_text.strip():
                                sub_chunk_id = f"enologia_paragraph_{chunk_count}_final"
                                metadata = {
                                    'type': 'knowledge',
                                    'category': 'enologia', 
                                    'chunk_type': 'paragraph_final',
                                    'estimated_chars': len(current_text)
                                }
                                
                                ids_to_add.append(sub_chunk_id)
                                docs_to_add.append(current_text.strip())
                                metas_to_add.append(metadata)
                                chunk_count += 1
                        else:
                            # Párrafo normal, añadir directamente
                            metadata = {
                                'type': 'knowledge',
                                'category': 'enologia',
                                'chunk_type': 'paragraph',
                                'estimated_chars': len(paragraph)
                            }
                            
                            ids_to_add.append(chunk_id)
                            docs_to_add.append(paragraph)
                            metas_to_add.append(metadata)
                            chunk_count += 1
            
            # Añadir todos los chunks a la colección
            if ids_to_add:
                self.collection.add(ids=ids_to_add, documents=docs_to_add, metadatas=metas_to_add)
                logger.info(f"✅ Añadidos {len(ids_to_add)} chunks de conocimiento enológico")
            else:
                logger.info("✅ El conocimiento enológico ya estaba cargado")
                
        except Exception as e:
            logger.error(f"❌ Error procesando maestría enológica: {e}")
            logger.info("🔄 Continuando sin conocimiento enológico")

    def _semantic_chunk(self, section: Dict, max_tokens: int = 1000, overlap: int = 75) -> List[Dict]:
        """Divide una sección en chunks semánticos manteniendo contexto."""
        content = section['content']
        
        # Dividir por párrafos para mantener coherencia semántica
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
        
        chunks = []
        current_chunk = ""
        current_tokens = 0
        
        # Estimar tokens (aproximadamente 4 caracteres por token)
        def estimate_tokens(text):
            return len(text) // 4
        
        for paragraph in paragraphs:
            para_tokens = estimate_tokens(paragraph)
            
            # Si el párrafo solo excede el límite, dividirlo por oraciones
            if para_tokens > max_tokens:
                sentences = re.split(r'[.!?]+\s+', paragraph)
                for sentence in sentences:
                    sentence = sentence.strip()
                    if not sentence:
                        continue
                        
                    sent_tokens = estimate_tokens(sentence)
                    
                    if current_tokens + sent_tokens > max_tokens and current_chunk:
                        # Guardar chunk actual
                        chunks.append({
                            'content': current_chunk.strip(),
                            'tokens': current_tokens
                        })
                        current_chunk = sentence + ". "
                        current_tokens = sent_tokens
                    else:
                        current_chunk += sentence + ". "
                        current_tokens += sent_tokens
            
            # Si agregar este párrafo excede el límite
            elif current_tokens + para_tokens > max_tokens and current_chunk:
                # Guardar chunk actual
                chunks.append({
                    'content': current_chunk.strip(),
                    'tokens': current_tokens
                })
                current_chunk = paragraph + "\n\n"
                current_tokens = para_tokens
            else:
                current_chunk += paragraph + "\n\n"
                current_tokens += para_tokens
        
        # Añadir último chunk si existe
        if current_chunk.strip():
            chunks.append({
                'content': current_chunk.strip(),
                'tokens': current_tokens
            })
        
        # Añadir metadatos de sección a cada chunk
        for chunk in chunks:
            chunk.update({
                'section_id': section['id'],
                'main_title': section['main_title'],
                'sub_title': section['sub_title'],
                'full_title': section['full_title']
            })
        
        return chunks

    def _extract_topic_keywords(self, content: str) -> List[str]:
        """Extrae palabras clave principales del contenido."""
        # Palabras clave comunes del dominio enológico
        wine_keywords = [
            'sumiller', 'sommelier', 'maridaje', 'cata', 'vino', 'bodega', 'uva', 'variedad',
            'terruño', 'terroir', 'acidez', 'taninos', 'crianza', 'fermentación', 'barrica',
            'degustación', 'aroma', 'sabor', 'textura', 'servicio', 'temperatura', 'copa',
            'decantación', 'añada', 'cosecha', 'vendimia', 'enólogo', 'vinificación',
            'equilibrio', 'intensidad', 'complementariedad', 'contraste', 'grasa', 'proteína'
        ]
        
        content_lower = content.lower()
        found_keywords = []
        
        for keyword in wine_keywords:
            if keyword in content_lower:
                found_keywords.append(keyword)
        
        return found_keywords[:5]  # Máximo 5 keywords principales

    def _process_enology_text(self, text_path: Path):
        """Procesa el texto de maestría enológica con chunking semántico."""
        logger.info(f"Procesando texto de maestría enológica desde {text_path}...")
        
        with open(text_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extraer secciones del documento
        sections = self._extract_sections_from_enology_text(content)
        logger.info(f"Extraídas {len(sections)} secciones del documento")
        
        ids_to_add, docs_to_add, metas_to_add = [], [], []
        existing_ids = set(self.collection.get(include=[])['ids'])
        
        for section in sections:
            # Crear chunks semánticos para cada sección
            chunks = self._semantic_chunk(section, max_tokens=1000, overlap=75)
            
            for i, chunk in enumerate(chunks):
                chunk_id = f"enologia_{section['id'].replace('.', '_')}_{i}"
                
                if chunk_id not in existing_ids:
                    # Preparar contenido del chunk con contexto
                    chunk_content = f"Sección {section['id']}: {chunk['full_title']}\n\n{chunk['content']}"
                    
                    # Extraer keywords
                    keywords = self._extract_topic_keywords(chunk['content'])
                    
                    # Metadatos ricos
                    metadata = {
                        'type': 'knowledge',
                        'category': 'enologia',
                        'section_id': section['id'],
                        'section_title': section['main_title'],
                        'subsection_title': section['sub_title'],
                        'chunk_index': i,
                        'keywords': keywords,
                        'estimated_tokens': chunk['tokens']
                    }
                    
                    ids_to_add.append(chunk_id)
                    docs_to_add.append(chunk_content)
                    metas_to_add.append(metadata)
        
        if ids_to_add:
            self.collection.add(ids=ids_to_add, documents=docs_to_add, metadatas=metas_to_add)
            logger.info(f"✅ Añadidos {len(ids_to_add)} chunks de conocimiento enológico")
        else:
            logger.info("✅ El conocimiento enológico ya estaba cargado")

    def _load_initial_data(self):
        """Carga la base de conocimiento inicial desde archivos JSON y texto."""
        # Cargar vinos desde JSON
        vinos_path = Path(__file__).parent / "knowledge_base" / "vinos.json"
        if vinos_path.exists():
            logger.info(f"Cargando base de vinos desde {vinos_path}...")
            with open(vinos_path, 'r', encoding='utf-8') as f:
                vinos = json.load(f)
            
            ids_to_add, docs_to_add, metas_to_add = [], [], []
            existing_ids = set(self.collection.get(include=[])['ids'])

            for i, vino in enumerate(vinos):
                doc_id = f"vino_{i}_{vino.get('name', 'unknown').replace(' ', '_').lower()}"
                if doc_id not in existing_ids:
                    # Estrategia de chunking para vinos (una entidad por chunk)
                    content_parts = [
                        f"Vino: {vino.get('name')}",
                        f"Tipo: {vino.get('type')}",
                        f"Bodega: {vino.get('winery')}",
                        f"Región: {vino.get('region')}",
                        f"Uva: {vino.get('grape')}",
                        f"Graduación: {vino.get('alcohol')}%",
                        f"Temperatura de servicio: {vino.get('temperature')}",
                        f"Crianza: {vino.get('crianza')}" if vino.get('crianza') else None,
                        f"Precio: {vino.get('price')}€",
                        f"Puntuación: {vino.get('rating')}/100",
                        f"Maridaje: {vino.get('pairing')}",
                        f"Descripción: {vino.get('description')}"
                    ]
                    
                    # Filtrar partes vacías y unir
                    content = ". ".join([part for part in content_parts if part and str(part) != "None"])
                    content += "."
                    
                    # Añadir marcador de tipo para distinguir en metadatos
                    vino['type_content'] = 'wine'
                    
                    ids_to_add.append(doc_id)
                    docs_to_add.append(content)
                    metas_to_add.append(vino)

            if ids_to_add:
                self.collection.add(ids=ids_to_add, documents=docs_to_add, metadatas=metas_to_add)
                logger.info(f"✅ Añadidos {len(ids_to_add)} nuevos vinos")
        
        # Cargar conocimiento enológico desde texto con estrategia simple
        enology_path = Path(__file__).parent / "knowledge_base" / "maestria_enologica.txt"
        if enology_path.exists():
            self._process_enology_simple(enology_path)
        else:
            logger.warning(f"No se encontró el archivo de maestría enológica en {enology_path}")
        
        total_docs = self.collection.count()
        logger.info(f"✅ Base de conocimiento cargada. Total documentos: {total_docs}")

    def search(self, query: str, max_results: int = 3) -> List[Dict]:
        """Realiza una búsqueda semántica en la colección con filtros inteligentes."""
        
        # Detectar si la consulta es sobre conocimiento general o vinos específicos
        knowledge_keywords = [
            'qué es', 'cómo', 'por qué', 'cuándo', 'dónde', 'principios', 'técnica', 'método',
            'sumiller', 'maridaje', 'cata', 'servicio', 'proceso', 'historia', 'definición'
        ]
        
        wine_type_filters = {
            'tinto': 'Tinto', 'blanco': 'Blanco', 'rosado': 'Rosado',
            'champagne': 'Champagne', 'cava': 'Cava', 'fino': 'Fino',
            'manzanilla': 'Manzanilla', 'amontillado': 'Amontillado', 'oloroso': 'Oloroso'
        }
        
        query_lower = query.lower()
        
        # Determinar el tipo de búsqueda
        is_knowledge_query = any(keyword in query_lower for keyword in knowledge_keywords)
        wine_type_filter = None
        
        # Buscar tipo específico de vino en la consulta
        for keyword, wine_type in wine_type_filters.items():
            if keyword in query_lower:
                wine_type_filter = wine_type
                break
        
        query_embedding = self.model.encode(query).tolist()
        
        # Aplicar filtros según el tipo de consulta
        if is_knowledge_query:
            logger.info(f"🧠 Búsqueda de conocimiento: {query}")
            # Priorizar chunks de conocimiento
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=max_results * 2,
                include=["metadatas", "distances"],
                where={"type": "knowledge"}
            )
        elif wine_type_filter:
            logger.info(f"🍷 Búsqueda filtrada por tipo de vino: {wine_type_filter}")
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=max_results * 2,
                include=["metadatas", "distances"],
                where={"type": wine_type_filter}
            )
        else:
            # Búsqueda general sin filtros
            logger.info(f"🔍 Búsqueda general: {query}")
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=max_results,
                include=["metadatas", "distances"]
            )
        
        formatted_results = []
        if results and results.get('ids')[0]:
            for metadata, distance in zip(results['metadatas'][0], results['distances'][0]):
                search_result = metadata.copy()
                search_result['relevance_score'] = 1 - distance
                formatted_results.append(search_result)
        
        # Limitar a los resultados solicitados
        return formatted_results[:max_results]

# Inicialización del servicio
app = FastAPI(title="Agentic RAG Service", version="1.0.0")
rag_service = RAGService()

@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy", "service": "agentic-rag"}

@app.get("/debug/chunks")
async def debug_chunks(limit: int = 5):
    """Debug endpoint para ver chunks."""
    try:
        results = rag_service.collection.get(limit=limit, include=['documents', 'metadatas'])
        return {
            "total_chunks": len(results['ids']),
            "sample_chunks": [
                {
                    "id": results['ids'][i],
                    "content": results['documents'][i],
                    "metadata": results['metadatas'][i] if results['metadatas'] else None
                }
                for i in range(min(limit, len(results['ids'])))
            ]
        }
    except Exception as e:
        logger.error(f"Error en debug_chunks: {e}")
        return {"error": str(e)}

@app.post("/search")
def search_endpoint(request: QueryRequest = Body(...)):
    """Endpoint para realizar búsquedas semánticas."""
    try:
        results = rag_service.search(request.query, request.max_results)
        return {"wines": results}
    except Exception as e:
        logger.error(f"Error en el endpoint de búsqueda RAG: {e}")
        raise HTTPException(status_code=500, detail=str(e))
