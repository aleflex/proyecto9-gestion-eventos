import logging
from typing import Optional
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database
from core.config import settings

logger = logging.getLogger(__name__)

_mongo_client: Optional[MongoClient] = None


def get_mongo_client() -> MongoClient:
    """
    Obtiene o inicializa la instancia de MongoClient de forma diferida (lazy).
    Esto previene bloqueos de conexión durante la importación en entornos CI/CD
    donde el servidor de MongoDB puede no estar disponible.
    """
    global _mongo_client
    if _mongo_client is None:
        logger.info(f"Conectando a MongoDB en: {settings.MONGODB_URI}")
        _mongo_client = MongoClient(
            settings.MONGODB_URI,
            serverSelectionTimeoutMS=5000,
            connect=False
        )
    return _mongo_client


def get_database() -> Database:
    """
    Retorna la base de datos configurada.
    """
    client = get_mongo_client()
    return client[settings.MONGODB_DB]


def get_eventos_collection() -> Collection:
    """
    Retorna la colección única 'eventos' de MongoDB.
    """
    db = get_database()
    return db[settings.MONGODB_COLLECTION]


def close_mongo_client() -> None:
    """
    Cierra la conexión activa con MongoDB.
    """
    global _mongo_client
    if _mongo_client is not None:
        _mongo_client.close()
        _mongo_client = None
        logger.info("Conexión con MongoDB cerrada.")


def check_database_connection() -> dict:
    """
    Verifica el estado de la conexión a MongoDB mediante el comando 'ping'.
    """
    try:
        client = get_mongo_client()
        client.admin.command("ping")
        return {
            "status": "connected",
            "database": settings.MONGODB_DB,
            "collection": settings.MONGODB_COLLECTION
        }
    except Exception as e:
        logger.warning(f"Error verificando conexión con MongoDB: {e}")
        return {
            "status": "disconnected",
            "error": str(e),
            "database": settings.MONGODB_DB,
            "collection": settings.MONGODB_COLLECTION
        }
