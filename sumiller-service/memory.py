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
                    user_name TEXT,
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
                    user_name TEXT,
                    preferences TEXT NOT NULL,
                    last_updated DATETIME DEFAULT CURRENT_TIMESTAMP,
                    total_interactions INTEGER DEFAULT 0,
                    favorite_wines TEXT,
                    last_session_id TEXT
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS wine_ratings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    user_name TEXT,
                    wine_name TEXT NOT NULL,
                    rating INTEGER CHECK(rating >= 1 AND rating <= 5),
                    notes TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()
            logger.info(f"✅ Base de datos de memoria inicializada en: {self.db_path}")

    async def save_conversation(self, user_id: str, query: str, response: str, wines_recommended: List[Dict] = None, session_id: str = None, user_name: str = None):
        """Guarda una interacción en la memoria."""
        try:
            wines_json = json.dumps(wines_recommended or [])
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO conversations 
                    (user_id, user_name, query, response, wines_recommended, session_id) 
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (user_id, user_name, query, response, wines_json, session_id))
                
                # Actualizar contador de interacciones
                conn.execute("""
                    UPDATE user_preferences 
                    SET total_interactions = total_interactions + 1,
                        last_session_id = ?
                    WHERE user_id = ?
                """, (session_id, user_id))
                
                conn.commit()
            logger.info(f"💾 Conversación guardada para el usuario {user_id} ({user_name})")
        except Exception as e:
            logger.error(f"Error al guardar la conversación: {e}")

    async def get_user_context(self, user_id: str, limit: int = 5) -> Dict[str, Any]:
        """Obtiene el contexto completo de un usuario."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                
                # Información del usuario
                user_info = conn.execute("""
                    SELECT preferences, total_interactions, favorite_wines 
                    FROM user_preferences 
                    WHERE user_id = ?
                """, (user_id,)).fetchone()
                
                # Conversaciones recientes
                conversations = conn.execute("""
                    SELECT query, response, timestamp, wines_recommended 
                    FROM conversations 
                    WHERE user_id = ? 
                    ORDER BY timestamp DESC 
                    LIMIT ?
                """, (user_id, limit)).fetchall()
                
                # Vinos mejor valorados
                top_wines = conn.execute("""
                    SELECT wine_name, AVG(rating) as avg_rating, COUNT(*) as total_ratings 
                    FROM wine_ratings 
                    WHERE user_id = ? 
                    GROUP BY wine_name 
                    ORDER BY avg_rating DESC 
                    LIMIT 3
                """, (user_id,)).fetchall()
                
                return {
                    "user_id": user_id,
                    "recent_conversations": [dict(conv) for conv in conversations],
                    "preferences": json.loads(user_info['preferences']) if user_info and user_info['preferences'] else {},
                    "favorite_wines": json.loads(user_info['favorite_wines']) if user_info and user_info['favorite_wines'] else [],
                    "top_rated_wines": [dict(wine) for wine in top_wines]
                }
        except Exception as e:
            logger.error(f"Error al obtener el contexto del usuario: {e}")
            return {
                "user_id": user_id,
                "recent_conversations": [],
                "preferences": {},
                "favorite_wines": [],
                "top_rated_wines": []
            }
            
    async def update_preferences(self, user_id: str, preferences: Dict[str, Any], user_name: str = None):
        """Crea o actualiza las preferencias de un usuario."""
        try:
            prefs_json = json.dumps(preferences)
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO user_preferences 
                    (user_id, user_name, preferences, last_updated) 
                    VALUES (?, ?, ?, ?)
                """, (user_id, user_name, prefs_json, datetime.now()))
                conn.commit()
            logger.info(f"⚙️ Preferencias actualizadas para el usuario {user_id} ({user_name})")
        except Exception as e:
            logger.error(f"Error al actualizar las preferencias: {e}")

    async def rate_wine(self, user_id: str, wine_name: str, rating: int, notes: str = "", user_name: str = None):
        """Permite a un usuario valorar un vino."""
        if not 1 <= rating <= 5:
            raise ValueError("La valoración debe estar entre 1 y 5.")
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO wine_ratings 
                    (user_id, user_name, wine_name, rating, notes) 
                    VALUES (?, ?, ?, ?, ?)
                """, (user_id, user_name, wine_name, rating, notes))
                
                # Actualizar vinos favoritos si la valoración es alta
                if rating >= 4:
                    user_info = conn.execute("""
                        SELECT favorite_wines FROM user_preferences WHERE user_id = ?
                    """, (user_id,)).fetchone()
                    
                    current_favorites = json.loads(user_info['favorite_wines']) if user_info and user_info['favorite_wines'] else []
                    if wine_name not in current_favorites:
                        current_favorites.append(wine_name)
                        conn.execute("""
                            UPDATE user_preferences 
                            SET favorite_wines = ? 
                            WHERE user_id = ?
                        """, (json.dumps(current_favorites), user_id))
                
                conn.commit()
            logger.info(f"⭐ Nueva valoración de {user_id} ({user_name}) para '{wine_name}': {rating}/5")
        except Exception as e:
            logger.error(f"Error al guardar la valoración: {e}")

    async def get_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas generales de la base de datos de memoria."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                total_conversations = conn.execute("SELECT COUNT(*) FROM conversations").fetchone()[0]
                total_users = conn.execute("SELECT COUNT(DISTINCT user_id) FROM conversations").fetchone()[0]
                total_ratings = conn.execute("SELECT COUNT(*) FROM wine_ratings").fetchone()[0]
                avg_rating = conn.execute("SELECT AVG(rating) FROM wine_ratings").fetchone()[0]
                
                db_size_bytes = os.path.getsize(self.db_path)
                db_size_kb = db_size_bytes / 1024
                
                return {
                    "total_conversations": total_conversations,
                    "unique_users": total_users,
                    "total_ratings": total_ratings,
                    "average_rating": round(avg_rating, 2) if avg_rating else 0,
                    "database_size_kb": round(db_size_kb, 2)
                }
        except Exception as e:
            logger.error(f"Error al obtener estadísticas: {e}")
            return {"error": str(e)}
