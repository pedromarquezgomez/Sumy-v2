# sumiller-service/query_filter.py
import os
import json
import logging
from typing import Dict, Any, Tuple
from openai import AsyncOpenAI
from pathlib import Path

logger = logging.getLogger(__name__)

def load_prompt_from_file(file_name: str) -> str:
    """Carga un prompt desde un archivo en el directorio 'prompts'."""
    prompt_path = Path(__file__).parent / "prompts" / file_name
    try:
        with open(prompt_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        logger.error(f"FATAL: Archivo de prompt no encontrado: {prompt_path}")
        return ""

def load_romantic_keywords() -> Tuple[Dict[str, float], float, float]:
    """Carga las palabras clave románticas y su configuración desde el archivo."""
    keywords = {}
    min_confidence = 0.7
    exact_match_bonus = 0.1
    
    try:
        keywords_file = Path(__file__).parent / "prompts" / "romantic_keywords.txt"
        with open(keywords_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                if '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()
                    
                    if key == 'MIN_CONFIDENCE':
                        min_confidence = float(value)
                    elif key == 'EXACT_MATCH_BONUS':
                        exact_match_bonus = float(value)
                    else:
                        keywords[key] = float(value)
        
        logger.info(f"✅ Cargadas {len(keywords)} palabras clave románticas")
        return keywords, min_confidence, exact_match_bonus
    except Exception as e:
        logger.error(f"Error cargando palabras clave románticas: {e}")
        return {}, 0.7, 0.1

def is_romantic_query_manual(user_query: str) -> Tuple[bool, str, float]:
    """
    Detecta si la consulta es romántica basándose en palabras clave.
    Returns: (es_romantica, palabra_clave, confianza)
    """
    keywords, min_confidence, exact_match_bonus = load_romantic_keywords()
    query_lower = user_query.lower()
    
    # Primero, buscar coincidencias exactas
    for kw, base_confidence in keywords.items():
        if kw == query_lower:
            return True, kw, min(1.0, base_confidence + exact_match_bonus)
    
    # Luego, buscar inclusiones
    for kw, base_confidence in keywords.items():
        if kw in query_lower:
            # Ajustar confianza basada en la longitud de la palabra clave
            length_factor = min(0.2, len(kw) / 50)  # Máximo 0.2 de bonus por longitud
            confidence = base_confidence + length_factor
            if confidence >= min_confidence:
                return True, kw, confidence
    
    return False, "", 0.0

class IntelligentQueryFilter:
    """Clasifica las consultas de los usuarios usando un LLM para decidir la mejor estrategia de respuesta."""

    def __init__(self, openai_client: AsyncOpenAI):
        self.openai_client = openai_client
        self.classification_prompt_template = load_prompt_from_file("sumiller_clasificacion.txt")
    
    async def classify_query(self, user_query: str) -> Dict[str, Any]:
        """Clasifica una consulta usando el LLM o un método de fallback."""
        if not self.openai_client or not self.classification_prompt_template:
            logger.warning("Cliente OpenAI o plantilla de prompt no disponible. Usando fallback.")
            return self._fallback_classification(user_query)

        full_prompt = self.classification_prompt_template + f'\nConsulta: "{user_query}"'
        
        try:
            response = await self.openai_client.chat.completions.create(
                model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
                messages=[{"role": "user", "content": full_prompt}],
                response_format={"type": "json_object"},
                temperature=0.1,
                max_tokens=150,
                timeout=10.0
            )
            result_text = response.choices[0].message.content.strip()
            
            try:
                classification = json.loads(result_text)
                # Validaciones básicas
                if "category" in classification and "confidence" in classification:
                    logger.info(f"✅ Clasificación LLM exitosa: {classification['category']} (Confianza: {classification['confidence']})")
                    return classification
                raise ValueError("Formato JSON de clasificación incompleto.")
                
            except (json.JSONDecodeError, ValueError) as e:
                logger.warning(f"⚠️ No se pudo parsear o validar el JSON del LLM: {result_text}. Error: {e}")
                return self._fallback_classification(user_query)
                
        except Exception as e:
            logger.error(f"❌ Error en la llamada de clasificación al LLM: {e}")
            return self._fallback_classification(user_query)
    
    def _fallback_classification(self, user_query: str) -> Dict[str, Any]:
        """Clasificación de respaldo basada en palabras clave si el LLM falla."""
        # Primero, comprobación de mensajes románticos
        is_romantic, keyword, score = is_romantic_query_manual(user_query)
        if is_romantic:
            return {
                "category": "SECRET_MESSAGE", 
                "confidence": score, 
                "reasoning": f"Coincidencia con '{keyword}' (confianza: {score:.2f})"
            }
        
        # Después, comprobación por palabras clave exactas
        query_lower = user_query.lower()
        if any(kw in query_lower for kw in ['recomienda', 'sugiere', 'busco', 'maridaje', 'para', 'con', 'rioja', 'ribera', 'vino']):
            return {"category": "WINE_SEARCH", "confidence": 0.7, "reasoning": "Fallback: keywords de búsqueda"}
        if any(kw in query_lower for kw in ['qué es', 'explica', 'diferencia', 'cómo', 'taninos', 'acidez', 'cata']):
            return {"category": "WINE_THEORY", "confidence": 0.7, "reasoning": "Fallback: keywords de teoría"}
        if any(kw in query_lower for kw in ['hola', 'buenos', 'saludos', 'qué tal', 'gracias']):
            return {"category": "GREETING", "confidence": 0.6, "reasoning": "Fallback: keywords de saludo"}
        return {"category": "OFF_TOPIC", "confidence": 0.5, "reasoning": "Fallback: no se detectaron keywords"}

# Respuestas predefinidas para categorías que no requieren búsqueda
CATEGORY_RESPONSES = {
    "GREETING": "¡Hola! Soy Sumy, tu sumiller virtual personal. 🍷 Estoy aquí para ayudarte a descubrir el vino perfecto para cualquier ocasión, resolver tus dudas sobre el fascinante mundo del vino o encontrar el maridaje ideal. ¿En qué puedo ayudarte hoy?",
    "SECRET_MESSAGE": "🍷💕 **Mensaje Secreto Descubierto** 💕🍷\n\nMi querida Vicky,\n\nEn este mundo de vinos y sabores, tú eres mi mejor maridaje. Como un gran vino que mejora con el tiempo, nuestro amor se vuelve más especial cada día.\n\nEres mi Ribera del Duero favorito: elegante, compleja y con una personalidad única que me conquista. Tu sonrisa es como un buen Champagne, burbujeante y llena de alegría.\n\nCon todo mi amor,\nPedro\n\n*Como sumiller, este es el maridaje más hermoso que he visto. ¡Felicidades! 🥂*",
    "OFF_TOPIC": "Entiendo tu curiosidad, pero mi especialidad es el maravilloso mundo del vino. 🍷 Puedo ayudarte con recomendaciones, maridajes o cualquier duda que tengas sobre viticultura y enología. ¿Te apetece que hablemos de vinos?"
}

async def filter_and_classify_query(openai_client: AsyncOpenAI, user_query: str) -> Dict[str, Any]:
    """Función principal para clasificar una consulta y determinar si necesita RAG."""
    filter_instance = IntelligentQueryFilter(openai_client)
    classification = await filter_instance.classify_query(user_query)
    classification["should_use_rag"] = (classification.get("category") == "WINE_SEARCH" and classification.get("confidence", 0) > 0.6)
    return classification
