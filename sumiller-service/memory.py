# Módulo de Memoria Integrada para Sumiller Service usando SQLite.
import sqlite3
import json
import logging
import os
from datetime import datetime
from typing import Dict, List, Any
from pathlib import Path

logger = logging.getLogger(__name__)

class SumillerMemory:
    """Gestión de memoria conversacional y preferencias del usuario."""
    
    def __init__(self, db_path: str = None):
        if db_path is None:
            # Crea el archivo de la BD en un subdirectorio para mantener el proyecto limpio.
            db_dir = Path("./database")
            db_dir.mkdir(exist_ok=True)
            db_path = db_dir / "sumiller.db"
        self.db_path = Path(db_path)
        self._init_database()
    
    def _init_database(self):
        """Inicializa la base de datos SQLite y sus tablas si no existen."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    query TEXT NOT NULL,
                    response TEXT NOT NULL,
                    wines_recommended TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    session_id TEXT
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_preferences (
                    user_id TEXT PRIMARY KEY,
                    preferences TEXT NOT NULL,
                    last_updated DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS wine_ratings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    wine_name TEXT NOT NULL,
                    rating INTEGER CHECK(rating >= 1 AND rating <= 5),
                    notes TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()
            logger.info(f"✅ Base de datos de memoria inicializada en: {self.db_path}")

    async def save_conversation(self, user_id: str, query: str, response: str, wines_recommended: List[Dict] = None, session_id: str = None):
        """Guarda una interacción en la memoria."""
        try:
            wines_json = json.dumps(wines_recommended or [])
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("INSERT INTO conversations (user_id, query, response, wines_recommended, session_id) VALUES (?, ?, ?, ?, ?)", 
                             (user_id, query, response, wines_json, session_id))
                conn.commit()
            logger.info(f"💾 Conversación guardada para el usuario {user_id}")
        except Exception as e:
            logger.error(f"Error al guardar la conversación: {e}")

    async def get_user_context(self, user_id: str, limit: int = 5) -> Dict[str, Any]:
        """Obtiene el contexto completo de un usuario."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                
                # Conversaciones recientes
                conversations = conn.execute("SELECT query, response, timestamp FROM conversations WHERE user_id = ? ORDER BY timestamp DESC LIMIT ?", (user_id, limit)).fetchall()
                
                # Preferencias del usuario
                prefs_row = conn.execute("SELECT preferences FROM user_preferences WHERE user_id = ?", (user_id,)).fetchone()
                preferences = json.loads(prefs_row['preferences']) if prefs_row else {}
                
                # Vinos mejor valorados por el usuario
                top_wines = conn.execute("SELECT wine_name, AVG(rating) as avg_rating FROM wine_ratings WHERE user_id = ? GROUP BY wine_name ORDER BY avg_rating DESC LIMIT 3", (user_id,)).fetchall()
                
                return {
                    "user_id": user_id,
                    "recent_conversations": [dict(conv) for conv in conversations],
                    "preferences": preferences,
                    "favorite_wines": [dict(wine) for wine in top_wines],
                }
        except Exception as e:
            logger.error(f"Error al obtener el contexto del usuario: {e}")
            return {"user_id": user_id, "recent_conversations": [], "preferences": {}, "favorite_wines": [], "error": str(e)}
            
    async def update_preferences(self, user_id: str, preferences: Dict[str, Any]):
        """Crea o actualiza las preferencias de un usuario."""
        try:
            prefs_json = json.dumps(preferences)
            with sqlite3.connect(self.db_path) as conn:
                # INSERT OR REPLACE (UPSERT) para simplicidad
                conn.execute("INSERT OR REPLACE INTO user_preferences (user_id, preferences, last_updated) VALUES (?, ?, ?)",
                             (user_id, prefs_json, datetime.now()))
                conn.commit()
            logger.info(f"⚙️ Preferencias actualizadas para el usuario {user_id}")
        except Exception as e:
            logger.error(f"Error al actualizar las preferencias: {e}")

    async def rate_wine(self, user_id: str, wine_name: str, rating: int, notes: str = ""):
        """Permite a un usuario valorar un vino."""
        if not 1 <= rating <= 5:
            raise ValueError("La valoración debe estar entre 1 y 5.")
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("INSERT INTO wine_ratings (user_id, wine_name, rating, notes) VALUES (?, ?, ?, ?)",
                             (user_id, wine_name, rating, notes))
                conn.commit()
            logger.info(f"⭐ Nueva valoración de {user_id} para '{wine_name}': {rating}/5")
        except Exception as e:
            logger.error(f"Error al guardar la valoración: {e}")

    async def get_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas generales de la base de datos de memoria."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                total_conversations = conn.execute("SELECT COUNT(*) FROM conversations").fetchone()[0]
                total_users = conn.execute("SELECT COUNT(DISTINCT user_id) FROM conversations").fetchone()[0]
                total_ratings = conn.execute("SELECT COUNT(*) FROM wine_ratings").fetchone()[0]
                
                db_size_bytes = os.path.getsize(self.db_path)
                db_size_kb = db_size_bytes / 1024
                
                return {
                    "total_conversations": total_conversations,
                    "unique_users": total_users,
                    "total_ratings": total_ratings,
                    "database_size_kb": round(db_size_kb, 2)
                }
        except Exception as e:
            logger.error(f"Error al obtener estadísticas: {e}")
            return {"error": str(e)}
