# sumiller-service/main.py
import os
import json
import logging
from typing import Dict, List, Any, Optional, AsyncGenerator
from datetime import datetime
from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import StreamingResponse
from pydantic import BaseModel
import httpx
from pathlib import Path
import vertexai
from vertexai.generative_models import GenerativeModel

from query_filter import filter_and_classify_query, CATEGORY_RESPONSES, load_prompt_from_file
from memory import SumillerMemory
from migrate_db import migrate_database

# --- INICIALIZACIÓN DE VERTEX AI ---
logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
logger = logging.getLogger(__name__)

# La autenticación es automática en Cloud Run
PROJECT_ID = os.getenv("GCP_PROJECT")
LOCATION = os.getenv("GCP_REGION", "europe-west1")
vertexai.init(project=PROJECT_ID, location=LOCATION)

# Cargar el modelo de IA para generación
generation_model = GenerativeModel("gemini-2.0-flash")

# Configuración del servicio
SEARCH_SERVICE_URL = os.getenv("SEARCH_SERVICE_URL")
app = FastAPI(title="Sumiller Service V2 (Vertex AI)")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

# Ejecutar migración de base de datos al inicio
try:
    migrate_database()
    logger.info("✅ Migración de base de datos completada")
except Exception as e:
    logger.error(f"❌ Error en migración de base de datos: {e}")

memory = SumillerMemory()

class ConversationMessage(BaseModel):
    role: str
    content: str

class QueryRequest(BaseModel):
    query: str
    user_id: Optional[str] = None
    user_name: Optional[str] = None
    conversation_history: List[ConversationMessage] = []

# --- Lógica de Streaming con Vertex AI ---
async def search_wines(query: str) -> List[Dict]:
    if not SEARCH_SERVICE_URL: return []
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{SEARCH_SERVICE_URL}/search", json={"query": query}, timeout=10.0)
            return response.json().get("wines", []) if response.status_code == 200 else []
    except Exception as e:
        logger.error(f"Error buscando vinos: {e}")
        return []

async def generate_streaming_response(query: str, wines: List[Dict], context: Dict, conversation_history: List[ConversationMessage], category: str = None) -> AsyncGenerator[str, None]:
    # Usar prompt específico según la categoría
    if category == "SECRET_MESSAGE":
        base_prompt = load_prompt_from_file("secret_message_generation.txt")
    elif category == "OFF_TOPIC":
        base_prompt = load_prompt_from_file("off_topic_response.txt")
    else:
        base_prompt = load_prompt_from_file("sumiller_generacion.txt")
    
    # Adaptar el historial para el modelo Gemini
    history = [f"{msg.role}: {msg.content}" for msg in conversation_history[-8:]]
    history_str = "\n".join(history)
    
    wines_str = f"Vinos encontrados:\n{json.dumps(wines, indent=2, ensure_ascii=False)}" if wines else "No se encontraron vinos específicos."
    
    # Para mensajes secretos, incluir información específica
    if category == "SECRET_MESSAGE":
        # El destinatario SIEMPRE es Vicky, el remitente es quien hace la consulta
        sender_name = context.get('sender_name', 'Tu sumiller')
        sender_first_name = sender_name.split()[0] if sender_name else "Tu sumiller"
        
        full_prompt = f"""{base_prompt}

INFORMACIÓN DEL MENSAJE:
- Destinatario: Vicky (SIEMPRE)
- Remitente: {sender_first_name}
- Consulta original: {query}

CONTEXTO ADICIONAL:
{json.dumps(context, ensure_ascii=False)}

HISTORIAL RECIENTE:
{history_str}

Genera un mensaje secreto ÚNICO y ORIGINAL usando las instrucciones anteriores.
"""
    else:
        full_prompt = f"""{base_prompt}

CONTEXTO DEL USUARIO:
{json.dumps(context, ensure_ascii=False)}

HISTORIAL DE CONVERSACIÓN:
{history_str}

CONSULTA ACTUAL:
{query}

VINOS ENCONTRADOS (si aplica):
{wines_str}

RESPUESTA:
"""
    
    try:
        # --- LLAMADA DE STREAMING A VERTEX AI ---
        stream = await generation_model.generate_content_async(full_prompt, stream=True)
        async for chunk in stream:
            yield chunk.text
    except Exception as e:
        logger.error(f"Error en el streaming de Vertex AI: {e}")
        yield "Parece que he tenido un problema conectando con mi sabiduría vinícola."

# --- Endpoints de la API ---
@app.post("/query")
async def query(request: QueryRequest):
    classification = await filter_and_classify_query(request.query)
    category = classification.get("category", "OFF_TOPIC")

    async def stream_generator():
        full_response = ""
        wines = []
        
        # Para SECRET_MESSAGE y OFF_TOPIC, siempre generar dinámicamente
        if category in CATEGORY_RESPONSES and category not in ["SECRET_MESSAGE", "OFF_TOPIC"]:
            response_content = CATEGORY_RESPONSES[category]
            yield response_content
            full_response = response_content
        else:
            if classification.get("should_use_rag"):
                wines = await search_wines(request.query)
            
            user_context = await memory.get_user_context(request.user_id)
            
            # Añadir información del usuario al contexto para mensajes secretos
            if category == "SECRET_MESSAGE" and request.user_name:
                user_context['sender_name'] = request.user_name
            
            async for chunk in generate_streaming_response(request.query, wines, user_context, request.conversation_history, category):
                yield chunk
                full_response += chunk
        
        await memory.save_conversation(
            user_id=request.user_id,
            query=request.query,
            response=full_response,
            wines_recommended=wines,
            user_name=request.user_name
        )
    return StreamingResponse(stream_generator(), media_type="text/plain; charset=utf-8")

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "Sumiller Service V2 (Vertex AI)", "timestamp": datetime.now().isoformat()}

