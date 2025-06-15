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

    def _load_initial_data(self):
        """Carga la base de conocimiento inicial desde un archivo JSON."""
        vinos_path = Path(__file__).parent / "knowledge_base" / "vinos.json"
        if not vinos_path.exists():
            logger.warning(f"No se encontró el archivo de conocimiento en {vinos_path}")
            return
            
        logger.info(f"Cargando base de conocimiento desde {vinos_path}...")
        with open(vinos_path, 'r', encoding='utf-8') as f:
            vinos = json.load(f)
        
        ids_to_add, docs_to_add, metas_to_add = [], [], []
        existing_ids = set(self.collection.get(include=[])['ids'])

        for i, vino in enumerate(vinos):
            doc_id = f"vino_{i}_{vino.get('name', 'unknown').replace(' ', '_').lower()}"
            if doc_id not in existing_ids:
                # Estrategia de chunking mejorada con más campos
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
                
                ids_to_add.append(doc_id)
                docs_to_add.append(content)
                metas_to_add.append(vino)

        if ids_to_add:
            self.collection.add(ids=ids_to_add, documents=docs_to_add, metadatas=metas_to_add)
            logger.info(f"✅ Añadidos {len(ids_to_add)} nuevos vinos. Total en DB: {self.collection.count()}")
        else:
            logger.info("✅ La base de conocimiento ya estaba actualizada.")


    def search(self, query: str, max_results: int = 3) -> List[Dict]:
        """Realiza una búsqueda semántica en la colección."""
        query_embedding = self.model.encode(query).tolist()
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=max_results,
            include=["metadatas", "distances"]
        )
        
        formatted_results = []
        if results and results.get('ids')[0]:
            for metadata, distance in zip(results['metadatas'][0], results['distances'][0]):
                search_result = metadata
                search_result['relevance_score'] = 1 - distance
                formatted_results.append(search_result)
        
        return formatted_results

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
