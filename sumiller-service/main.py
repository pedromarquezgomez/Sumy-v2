# sumiller-service/main.py
import os
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import httpx
from openai import AsyncOpenAI
from dotenv import load_dotenv
from pathlib import Path

from query_filter import filter_and_classify_query, CATEGORY_RESPONSES, load_prompt_from_file
from memory import SumillerMemory

load_dotenv()

# Configuración
logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
logger = logging.getLogger(__name__)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
SEARCH_SERVICE_URL = os.getenv("SEARCH_SERVICE_URL")

openai_client = AsyncOpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None
app = FastAPI(title="Sumiller Service V2")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

# Inicializar memoria
memory = SumillerMemory()

def load_secret_message_context() -> Dict[str, Any]:
    """Carga el contexto para mensajes secretos desde el archivo de configuración."""
    context = {}
    try:
        context_file = Path(__file__).parent / "prompts" / "secret_message_context.txt"
        with open(context_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                if '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()
                    
                    # Convertir valores booleanos
                    if value.lower() == 'true':
                        value = True
                    elif value.lower() == 'false':
                        value = False
                    # Convertir valores numéricos
                    elif value.isdigit():
                        value = int(value)
                    elif value.replace('.', '').isdigit():
                        value = float(value)
                    # Convertir listas
                    elif ',' in value:
                        value = [v.strip() for v in value.split(',')]
                    
                    context[key] = value
        
        logger.info(f"✅ Contexto de mensajes secretos cargado: {len(context)} configuraciones")
        return context
    except Exception as e:
        logger.error(f"Error cargando contexto de mensajes secretos: {e}")
        return {}

# --- Modelos de Pydantic ---
class ConversationMessage(BaseModel):
    role: str  # "user" o "assistant"
    content: str
    timestamp: Optional[str] = None

class QueryRequest(BaseModel):
    query: str
    user_id: Optional[str] = None  # Google Auth ID
    user_name: Optional[str] = None  # Nombre del usuario
    conversation_history: List[ConversationMessage] = []
    user_preferences: Dict[str, Any] = {}

class SumillerResponse(BaseModel):
    response: str
    wines_recommended: List[Dict[str, Any]] = []
    query_category: str
    used_rag: bool

# --- Funciones de Lógica ---
async def search_wines(openai_client: AsyncOpenAI, query: str) -> List[Dict]:
    """Busca vinos relevantes usando el servicio de búsqueda."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{SEARCH_SERVICE_URL}/search",
                json={"query": query}
            )
            if response.status_code == 200:
                return response.json()
            return []
    except Exception as e:
        logger.error(f"Error buscando vinos: {e}")
        return []

async def generate_sumiller_response(query: str, wines: List[Dict], context: Dict, category: str, conversation_history: List[ConversationMessage], user_name: Optional[str] = None) -> str:
    base_prompt = load_prompt_from_file("sumiller_generacion.txt")
    if not openai_client or not base_prompt:
        return "Lo siento, estoy teniendo problemas para generar una respuesta en este momento."

    # Logging para depuración
    logger.info(f"📝 Generando respuesta para: '{query}'")
    logger.info(f"📚 Historial recibido: {len(conversation_history)} mensajes")
    for i, msg in enumerate(conversation_history):
        logger.info(f"  {i+1}. [{msg.role}]: {msg.content[:50]}...")

    # Construir mensajes para OpenAI con historial completo
    messages = [
        {"role": "system", "content": base_prompt}
    ]
    
    # Añadir historial de conversación previo (máximo últimos 8 mensajes)
    if conversation_history:
        logger.info(f"🔄 Añadiendo {len(conversation_history[-8:])} mensajes de historial a OpenAI")
        for msg in conversation_history[-8:]:  # Últimos 8 mensajes para mantener contexto
            messages.append({
                "role": msg.role,  # "user" o "assistant"
                "content": msg.content
            })
    else:
        logger.info("🆕 Primera interacción - sin historial previo")
    
    # Construir contexto adicional
    context_parts = []
    if context.get("user_preferences"):
        context_parts.append(f"Preferencias del usuario: {json.dumps(context['user_preferences'], ensure_ascii=False)}")
    
    # Construir mensaje actual
    if category == "SECRET_MESSAGE":
        secret_context = load_secret_message_context()
        # Añadir solo el primer nombre del remitente al contexto
        if user_name:
            primer_nombre = user_name.split()[0]
            secret_context["SENDER_NAME"] = primer_nombre
        context_parts.append(f"Contexto de mensaje secreto: {json.dumps(secret_context, ensure_ascii=False)}")
        current_message = f'Consulta de mensaje secreto: "{query}"'
    elif category == "WINE_THEORY":
        current_message = f'Consulta sobre teoría: "{query}"'
    else: # WINE_SEARCH
        wines_str = f"Vinos encontrados:\n{json.dumps(wines, indent=2, ensure_ascii=False)}" if wines else "No se encontraron vinos específicos en la base de datos."
        current_message = f'Consulta: "{query}"\n\n{wines_str}'
    
    if context_parts:
        current_message += f"\n\nContexto adicional:\n{chr(10).join(context_parts)}"
    
    # Añadir el mensaje actual del usuario
    messages.append({
        "role": "user",
        "content": current_message
    })
    
    logger.info(f"💬 Enviando {len(messages)} mensajes a OpenAI (sistema + {len(messages)-2} historial + 1 actual)")
    
    try:
        response = await openai_client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=messages,
            temperature=0.7,
            max_tokens=600
        )
        result = response.choices[0].message.content.strip()
        logger.info(f"✅ Respuesta generada: {len(result)} caracteres")
        return result
    except Exception as e:
        logger.error(f"Error generando respuesta con IA: {e}")
        return "Parece que he tenido un problema conectando con mi sabiduría vinícola. ¿Podemos intentarlo de nuevo?"

# --- Endpoints de la API ---
@app.post("/query")
async def query(request: QueryRequest):
    """Endpoint principal para procesar consultas."""
    try:
        # Obtener contexto del usuario
        user_context = await memory.get_user_context(request.user_id)
        
        # Clasificar la consulta
        classification = await filter_and_classify_query(openai_client, request.query)
        logger.info(f"Categoría detectada: {classification['category']} (confianza: {classification['confidence']})")
        
        # Si es GREETING, usar respuesta directa
        if classification["category"] == "GREETING":
            return {
                "response": CATEGORY_RESPONSES[classification["category"]],
                "category": classification["category"],
                "wines": [],
                "user_context": user_context
            }
        
        # Para OFF_TOPIC, WINE_SEARCH, WINE_THEORY y SECRET_MESSAGE, usar generación de IA
        wines = []
        if classification["should_use_rag"]:
            wines = await search_wines(openai_client, request.query)
            logger.info(f"Vinos encontrados: {len(wines)}")
        
        # Generar respuesta
        response = await generate_sumiller_response(
            request.query,
            wines,
            user_context,
            classification["category"],
            request.conversation_history,
            request.user_name
        )
        
        # Guardar en memoria
        await memory.save_conversation(
            user_id=request.user_id,
            query=request.query,
            response=response,
            wines_recommended=wines,
            session_id=request.user_id,  # Usar user_id como session_id
            user_name=request.user_name
        )
        
        return {
            "response": response,
            "category": classification["category"],
            "wines": wines,
            "user_context": user_context
        }
        
    except Exception as e:
        logger.error(f"Error procesando consulta: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health_check():
    """Endpoint de health check para verificar que el servicio está activo."""
    return {"status": "healthy", "service": "Sumiller Service V2", "timestamp": datetime.now().isoformat()}
