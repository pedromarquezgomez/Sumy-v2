# sumiller-service/query_filter.py
import os
import json
import logging
from typing import Dict, Any, Tuple
from pathlib import Path
import vertexai
from vertexai.generative_models import GenerativeModel

logger = logging.getLogger(__name__)

# --- INICIALIZACIÓN DE VERTEX AI ---
PROJECT_ID = os.getenv("GCP_PROJECT")
LOCATION = os.getenv("GCP_REGION", "europe-west1")
vertexai.init(project=PROJECT_ID, location=LOCATION)

# Cargar el modelo de IA una sola vez
classification_model = GenerativeModel("gemini-2.0-flash")


def load_prompt_from_file(file_name: str) -> str:
    prompt_path = Path(__file__).parent / "prompts" / file_name
    try:
        with open(prompt_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        logger.error(f"FATAL: Archivo de prompt no encontrado: {prompt_path}")
        return ""

# (El resto de funciones de carga de keywords y fallback se mantienen igual)
def load_romantic_keywords() -> Tuple[Dict[str, float], float, float]:
    keywords = {}
    min_confidence = 0.7
    exact_match_bonus = 0.1
    try:
        keywords_file = Path(__file__).parent / "prompts" / "romantic_keywords.txt"
        with open(keywords_file, 'r', encoding='utf-8') as f:
            for line in f:
                line_without_comment = line.split('#')[0].strip()
                if not line_without_comment or '=' not in line_without_comment:
                    continue
                key, value = line_without_comment.split('=', 1)
                key, value = key.strip(), value.strip()
                if key == 'MIN_CONFIDENCE': min_confidence = float(value)
                elif key == 'EXACT_MATCH_BONUS': exact_match_bonus = float(value)
                else: keywords[key] = float(value)
        return keywords, min_confidence, exact_match_bonus
    except Exception as e:
        logger.error(f"Error cargando palabras clave románticas: {e}")
        return {}, 0.7, 0.1

def is_romantic_query_manual(user_query: str) -> Tuple[bool, str, float]:
    keywords, min_confidence, exact_match_bonus = load_romantic_keywords()
    query_lower = user_query.lower()
    for kw, base_conf in keywords.items():
        if kw == query_lower: return True, kw, min(1.0, base_conf + exact_match_bonus)
        if kw in query_lower:
            conf = base_conf + min(0.2, len(kw) / 50)
            if conf >= min_confidence: return True, kw, conf
    return False, "", 0.0

def _fallback_classification(user_query: str) -> Dict[str, Any]:
    is_romantic, keyword, score = is_romantic_query_manual(user_query)
    if is_romantic: return {"category": "SECRET_MESSAGE", "confidence": score, "reasoning": f"Coincidencia con '{keyword}'"}
    query_lower = user_query.lower()
    if any(kw in query_lower for kw in ['recomienda', 'sugiere', 'maridaje', 'vino']): return {"category": "WINE_SEARCH", "confidence": 0.7, "reasoning": "Fallback: keywords de búsqueda"}
    if any(kw in query_lower for kw in ['qué es', 'explica', 'diferencia', 'taninos']): return {"category": "WINE_THEORY", "confidence": 0.7, "reasoning": "Fallback: keywords de teoría"}
    if any(kw in query_lower for kw in ['hola', 'buenos', 'saludos']): return {"category": "GREETING", "confidence": 0.6, "reasoning": "Fallback: keywords de saludo"}
    return {"category": "OFF_TOPIC", "confidence": 0.5, "reasoning": "Fallback: no se detectaron keywords"}


class IntelligentQueryFilter:
    def __init__(self):
        self.model = classification_model
        self.classification_prompt_template = load_prompt_from_file("sumiller_clasificacion.txt")

    async def classify_query(self, user_query: str) -> Dict[str, Any]:
        if not self.classification_prompt_template:
            return _fallback_classification(user_query)

        full_prompt = self.classification_prompt_template + f'\nConsulta: "{user_query}"'
        
        try:
            # --- LLAMADA A VERTEX AI ---
            response = await self.model.generate_content_async(full_prompt)
            
            # Limpiar y parsear la respuesta JSON del modelo
            json_text = response.text.strip().replace("```json", "").replace("```", "").strip()
            classification = json.loads(json_text)

            if "category" in classification and "confidence" in classification:
                logger.info(f"✅ Clasificación Vertex AI: {classification['category']} (Confianza: {classification['confidence']})")
                return classification
            raise ValueError("Formato JSON de clasificación incompleto.")
        except Exception as e:
            logger.error(f"❌ Error en la llamada de clasificación a Vertex AI: {e}")
            return _fallback_classification(user_query)

CATEGORY_RESPONSES = {
    "GREETING": "¡Hola! Soy Sumy, tu sumiller virtual personal. 🍷 Estoy aquí para ayudarte a descubrir el vino perfecto para cualquier ocasión, resolver tus dudas sobre el fascinante mundo del vino o encontrar el maridaje ideal. ¿En qué puedo ayudarte hoy?"
}

async def filter_and_classify_query(user_query: str) -> Dict[str, Any]:
    filter_instance = IntelligentQueryFilter()
    classification = await filter_instance.classify_query(user_query)
    classification["should_use_rag"] = (classification.get("category") == "WINE_SEARCH" and classification.get("confidence", 0) > 0.6)
    return classification
