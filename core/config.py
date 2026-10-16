import os
from pydantic import Field
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
        default="mongodb://localhost:27017",
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
