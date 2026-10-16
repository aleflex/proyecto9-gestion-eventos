import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from core.config import settings
from core.database import check_database_connection, close_mongo_client
from api.routes import router as eventos_router

# Configuración de logs
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("gestion_eventos_api")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Ciclo de vida de la aplicación FastAPI.
    Se ejecuta al iniciar y al detener el servidor.
    """
    logger.info(f"Iniciando {settings.APP_NAME} v{settings.APP_VERSION}...")
    # Verificación de conexión opcional sin bloquear el arranque
    db_status = check_database_connection()
    if db_status["status"] == "connected":
        logger.info(f"Conexión a MongoDB exitosa en BD: '{settings.MONGODB_DB}', Colección: '{settings.MONGODB_COLLECTION}'.")
    else:
        logger.warning(f"MongoDB no está disponible de inmediato ({db_status.get('error', 'desconectado')}). Se reintentará con cada petición.")
    yield
    logger.info("Cerrando recursos de la aplicación...")
    close_mongo_client()


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="""
# 🎟️ API REST - Sistema de Gestión de Eventos

API desarrollada con **FastAPI** y **MongoDB** para la administración integral de eventos,
fechas, ubicaciones, capacidad, estados y participantes/asistentes.

---
### 📌 Características Principales
* **100% Asíncrona & Rápida**: Construida con FastAPI y Pydantic v2.
* **Colección Única**: Toda la persistencia reside en la colección `eventos` de MongoDB.
* **Control de Capacidad**: Validación automática de aforos y cupos disponibles en tiempo real.
* **Gestión de Asistentes**: Registro con fecha UTC y prevención de duplicidad por contacto.
* **Despliegue Serverless**: Configurada para ejecutarse en **Vercel** y conectarse a **MongoDB Atlas**.
    """,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Configuración de Middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclusión del Router de Eventos con el prefijo configurado (por defecto /api/v1)
app.include_router(eventos_router, prefix=settings.API_V1_PREFIX)

# Compatibilidad para inspección de rutas en app.routes (FastAPI < 0.113 y >= 0.113)
# Asegura que cada endpoint mantenga sus atributos .methods y .path directamente en app.routes
from fastapi.routing import APIRoute
for r in list(app.routes):
    if hasattr(r, "original_router"):
        prefix = getattr(r.include_context, "prefix", settings.API_V1_PREFIX) if hasattr(r, "include_context") else settings.API_V1_PREFIX
        for sub_r in getattr(r.original_router, "routes", []):
            if hasattr(sub_r, "methods") and hasattr(sub_r, "path"):
                full_path = prefix.rstrip("/") + "/" + sub_r.path.lstrip("/")
                if not any(getattr(existing, "path", None) == full_path and getattr(existing, "methods", None) == sub_r.methods for existing in app.routes):
                    app.routes.append(
                        APIRoute(
                            path=full_path,
                            endpoint=sub_r.endpoint,
                            methods=list(sub_r.methods),
                            include_in_schema=False
                        )
                    )


@app.get(
    "/",
    tags=["General"],
    summary="Ruta Raíz / Bienvenida",
    description="Retorna información general de la API, enlaces a la documentación interactiva y estado de los servicios."
)
def root():
    return {
        "aplicacion": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "estado": "operativo",
        "documentacion": {
            "swagger": "/docs",
            "redoc": "/redoc",
            "openapi": "/openapi.json"
        },
        "endpoints_principales": {
            "eventos": f"{settings.API_V1_PREFIX}/eventos",
            "buscar": f"{settings.API_V1_PREFIX}/eventos/buscar?nombre=...",
            "salud": "/health"
        }
    }


@app.get(
    "/health",
    tags=["General"],
    summary="Health Check / Chequeo de Salud",
    description="Verifica el estado del servicio y la conectividad con MongoDB."
)
def health_check():
    db_check = check_database_connection()
    status_code = status.HTTP_200_OK if db_check["status"] == "connected" else status.HTTP_503_SERVICE_UNAVAILABLE

    return JSONResponse(
        status_code=status_code,
        content={
            "api_status": "ok",
            "app_name": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "database": db_check
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
