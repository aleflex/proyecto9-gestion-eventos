"""
Módulo core de configuración y conexión a base de datos.
"""
from core.config import settings
from core.database import get_database, get_eventos_collection, get_mongo_client

__all__ = ["settings", "get_database", "get_eventos_collection", "get_mongo_client"]
