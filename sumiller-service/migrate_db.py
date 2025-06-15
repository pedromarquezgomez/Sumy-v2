#!/usr/bin/env python3
"""
Script de migración para actualizar la base de datos de Sumiller
Añade las columnas faltantes: user_name y total_interactions
"""

import sqlite3
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def migrate_database():
    """Migra la base de datos añadiendo las columnas faltantes."""
    db_dir = Path("./database")
    db_dir.mkdir(exist_ok=True)
    db_path = db_dir / "sumiller.db"
    
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            
            # Verificar si las columnas existen antes de añadirlas
            
            # 1. Añadir user_name a conversations si no existe
            try:
                cursor.execute("ALTER TABLE conversations ADD COLUMN user_name TEXT")
                logger.info("✅ Columna 'user_name' añadida a la tabla 'conversations'")
            except sqlite3.OperationalError as e:
                if "duplicate column name" in str(e):
                    logger.info("ℹ️ Columna 'user_name' ya existe en 'conversations'")
                else:
                    raise
            
            # 2. Añadir total_interactions a user_preferences si no existe
            try:
                cursor.execute("ALTER TABLE user_preferences ADD COLUMN total_interactions INTEGER DEFAULT 0")
                logger.info("✅ Columna 'total_interactions' añadida a la tabla 'user_preferences'")
            except sqlite3.OperationalError as e:
                if "duplicate column name" in str(e):
                    logger.info("ℹ️ Columna 'total_interactions' ya existe en 'user_preferences'")
                else:
                    raise
            
            # 3. Añadir user_name a user_preferences si no existe
            try:
                cursor.execute("ALTER TABLE user_preferences ADD COLUMN user_name TEXT")
                logger.info("✅ Columna 'user_name' añadida a la tabla 'user_preferences'")
            except sqlite3.OperationalError as e:
                if "duplicate column name" in str(e):
                    logger.info("ℹ️ Columna 'user_name' ya existe en 'user_preferences'")
                else:
                    raise
            
            # 4. Añadir user_name a wine_ratings si no existe
            try:
                cursor.execute("ALTER TABLE wine_ratings ADD COLUMN user_name TEXT")
                logger.info("✅ Columna 'user_name' añadida a la tabla 'wine_ratings'")
            except sqlite3.OperationalError as e:
                if "duplicate column name" in str(e):
                    logger.info("ℹ️ Columna 'user_name' ya existe en 'wine_ratings'")
                else:
                    raise
            
            # 5. Añadir favorite_wines a user_preferences si no existe
            try:
                cursor.execute("ALTER TABLE user_preferences ADD COLUMN favorite_wines TEXT")
                logger.info("✅ Columna 'favorite_wines' añadida a la tabla 'user_preferences'")
            except sqlite3.OperationalError as e:
                if "duplicate column name" in str(e):
                    logger.info("ℹ️ Columna 'favorite_wines' ya existe en 'user_preferences'")
                else:
                    raise
            
            # 6. Añadir last_session_id a user_preferences si no existe
            try:
                cursor.execute("ALTER TABLE user_preferences ADD COLUMN last_session_id TEXT")
                logger.info("✅ Columna 'last_session_id' añadida a la tabla 'user_preferences'")
            except sqlite3.OperationalError as e:
                if "duplicate column name" in str(e):
                    logger.info("ℹ️ Columna 'last_session_id' ya existe en 'user_preferences'")
                else:
                    raise
            
            conn.commit()
            logger.info("🎉 Migración de base de datos completada exitosamente")
            
    except Exception as e:
        logger.error(f"❌ Error durante la migración: {e}")
        raise

if __name__ == "__main__":
    migrate_database() 