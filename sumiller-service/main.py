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

from memory import SumillerMemory
from query_filter import filter_and_classify_query, CATEGORY_RESPONSES, load_prompt_from_file

load_dotenv()

# Configuración
logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
logger = logging.getLogger(__name__)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
SEARCH_SERVICE_URL = os.getenv("SEARCH_SERVICE_URL")

openai_client = AsyncOpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None
memory = SumillerMemory()
app = FastAPI(title="Sumiller Service V2")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

# --- Modelos de Pydantic ---
class QueryRequest(BaseModel):
    query: str
    user_id: str = "default_user"

class SumillerResponse(BaseModel):
    response: str
    wines_recommended: List[Dict[str, Any]] = []
    query_category: str
    used_rag: bool

class WineRatingRequest(BaseModel):
    wine_name: str
    rating: int = Field(..., ge=1, le=5) # Valida que el rating esté entre 1 y 5
    notes: Optional[str] = ""
    user_id: str = "default_user"

class PreferencesRequest(BaseModel):
    preferences: Dict[str, Any]
    user_id: str = "default_user"

# --- Funciones de Lógica ---
async def generate_sumiller_response(query: str, wines: List[Dict], context: Dict, category: str) -> str:
    base_prompt = load_prompt_from_file("sumiller_generacion.txt")
    if not openai_client or not base_prompt:
        return "Lo siento, estoy teniendo problemas para generar una respuesta en este momento."

    context_str = f"Contexto del usuario: {json.dumps(context, indent=2, ensure_ascii=False)}"
    
    if category == "WINE_THEORY":
        system_prompt = base_prompt + "\nTu tarea actual es explicar un concepto de sumillería de forma clara y educativa."
        user_content = f'Consulta sobre teoría: "{query}"\n{context_str}'
    else: # WINE_SEARCH
        system_prompt = base_prompt + "\nTu tarea actual es analizar la consulta del usuario y los vinos encontrados para dar una recomendación personalizada."
        wines_str = f"Vinos encontrados:\n{json.dumps(wines, indent=2, ensure_ascii=False)}" if wines else "No se encontraron vinos específicos."
        user_content = f'Consulta: "{query}"\n\n{wines_str}\n\n{context_str}'
    
    try:
        response = await openai_client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content}
            ],
            temperature=0.5,
            max_tokens=500
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"Error generando respuesta con IA: {e}")
        return "Parece que he tenido un problema conectando con mi sabiduría vinícola. ¿Podemos intentarlo de nuevo?"

# --- Endpoints de la API ---
@app.post("/query", response_model=SumillerResponse)
async def sumiller_query(request: QueryRequest = Body(...)):
    """Endpoint principal para procesar consultas de los usuarios."""
    classification = await filter_and_classify_query(openai_client, request.query)
    category = classification.get("category", "OFF_TOPIC")
    
    response_text = ""
    wines_recommended = []
    used_rag = False

    if category in CATEGORY_RESPONSES:
        response_text = CATEGORY_RESPONSES[category]
    else: # WINE_SEARCH o WINE_THEORY
        user_context = await memory.get_user_context(request.user_id)
        
        if classification.get("should_use_rag", False) and SEARCH_SERVICE_URL:
            try:
                async with httpx.AsyncClient() as client:
                    rag_response = await client.post(f"{SEARCH_SERVICE_URL}/search", json={"query": request.query}, timeout=15.0)
                    rag_response.raise_for_status()
                    wines_recommended = rag_response.json().get("wines", [])
                    used_rag = True
            except Exception as e:
                logger.error(f"Error llamando al RAG service: {e}")
                response_text = "He tenido un problema al consultar nuestra bodega de vinos. Intentémoslo de nuevo en un momento."
        
        if not response_text:
             response_text = await generate_sumiller_response(request.query, wines_recommended, user_context, category)

    await memory.save_conversation(request.user_id, request.query, response_text, wines_recommended)

    return SumillerResponse(
        response=response_text,
        wines_recommended=wines_recommended,
        query_category=category,
        used_rag=used_rag
    )

@app.post("/rate-wine", status_code=201)
async def rate_wine_endpoint(request: WineRatingRequest = Body(...)):
    """Endpoint para que los usuarios valoren un vino."""
    try:
        await memory.rate_wine(request.user_id, request.wine_name, request.rating, request.notes)
        return {"message": f"¡Gracias! Tu valoración para '{request.wine_name}' ha sido guardada."}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error al guardar la valoración del vino: {e}")
        raise HTTPException(status_code=500, detail="No se pudo guardar la valoración.")

@app.post("/preferences")
async def update_preferences_endpoint(request: PreferencesRequest = Body(...)):
    """Endpoint para guardar o actualizar las preferencias de un usuario."""
    try:
        await memory.update_preferences(request.user_id, request.preferences)
        return {"message": f"Preferencias para el usuario {request.user_id} actualizadas correctamente."}
    except Exception as e:
        logger.error(f"Error al actualizar las preferencias: {e}")
        raise HTTPException(status_code=500, detail="No se pudieron guardar las preferencias.")

@app.get("/user/{user_id}/context")
async def get_user_context_endpoint(user_id: str):
    """Endpoint para recuperar el contexto completo de un usuario."""
    try:
        context = await memory.get_user_context(user_id)
        return context
    except Exception as e:
        logger.error(f"Error al obtener el contexto del usuario {user_id}: {e}")
        raise HTTPException(status_code=500, detail="No se pudo recuperar el contexto del usuario.")

@app.get("/stats")
async def get_stats_endpoint():
    """Endpoint para obtener estadísticas generales del servicio."""
    try:
        service_stats = await memory.get_stats()
        service_stats["service_name"] = "Sumiller Service V2"
        service_stats["openai_model"] = OPENAI_MODEL
        service_stats["rag_service_enabled"] = bool(SEARCH_SERVICE_URL)
        return service_stats
    except Exception as e:
        logger.error(f"Error al obtener las estadísticas: {e}")
        raise HTTPException(status_code=500, detail="No se pudieron obtener las estadísticas.")

@app.get("/health")
def health_check():
    """Endpoint de health check para verificar que el servicio está activo."""
    return {"status": "healthy", "service": "Sumiller Service V2", "timestamp": datetime.now().isoformat()}
