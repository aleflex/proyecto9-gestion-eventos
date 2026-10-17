import os
from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Configuración global de la aplicación.
    Carga variables desde el entorno del sistema y opcionalmente desde un archivo .env.
    """
    APP_NAME: str = Field(
        default="Sistema de Gestión de Eventos",
        description="Nombre representativo de la aplicación"
    )
    APP_VERSION: str = Field(
        default="1.0.0",
        description="Versión actual de la API"
    )
    API_V1_PREFIX: str = Field(
        default="/api/v1",
        description="Prefijo de rutas para la versión 1 de la API"
    )
    MONGODB_URI: str = Field(
        default="mongodb+srv://Vercel-Admin-Proyect-event-management-system-APT:FbWlSNeZenFsBkda@proyect-event-managemen.hyminli.mongodb.net/?retryWrites=true&w=majority",
        validation_alias=AliasChoices("MONGODB_URI", "MONGODB_URL", "DATABASE_URL", "MONGO_URL"),
        description="URI de conexión a la base de datos MongoDB"
    )
    MONGODB_DB: str = Field(
        default="gestion_eventos_db",
        description="Nombre de la base de datos a utilizar"
    )
    MONGODB_COLLECTION: str = Field(
        default="eventos",
        description="Nombre de la colección única para los eventos"
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )


settings = Settings()
