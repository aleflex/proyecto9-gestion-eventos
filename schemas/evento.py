from typing import Any, List, Optional
from pydantic import BaseModel, ConfigDict, Field
from schemas.organizador import OrganizadorBase, OrganizadorUpdate
from schemas.asistente import AsistenteCreate, AsistenteResponse


class EventoBase(BaseModel):
    """
    Campos base para la entidad Evento.
    """
    nombre: str = Field(
        ...,
        min_length=3,
        max_length=150,
        description="Nombre o título del evento",
        examples=["Conferencia Internacional de Inteligencia Artificial 2026"]
    )
    descripcion: str = Field(
        ...,
        min_length=10,
        max_length=2000,
        description="Descripción detallada de los objetivos y actividades del evento",
        examples=["Encuentro global de especialistas, investigadores y desarrolladores de IA."]
    )
    categoria: str = Field(
        ...,
        min_length=2,
        max_length=60,
        description="Categoría o temática del evento",
        examples=["Tecnología"]
    )
    fecha: str = Field(
        ...,
        pattern=r"^\d{4}-\d{2}-\d{2}$",
        description="Fecha programada para el evento en formato YYYY-MM-DD",
        examples=["2026-11-20"]
    )
    hora: str = Field(
        ...,
        pattern=r"^(?:[01]\d|2[0-3]):[0-5]\d(?::[0-5]\d)?$",
        description="Hora de inicio en formato HH:MM (24 horas)",
        examples=["09:30"]
    )
    capacidad: int = Field(
        ...,
        gt=0,
        description="Capacidad máxima permitida de asistentes (debe ser mayor a cero)",
        examples=[150]
    )
    ubicacion: str = Field(
        ...,
        min_length=3,
        max_length=250,
        description="Ubicación física (dirección, auditorio) o enlace virtual (Zoom, Meet)",
        examples=["Auditorio Principal de Postgrado, Piso 3"]
    )
    estado: str = Field(
        default="activo",
        description="Estado actual del evento (ej: activo, cancelado, finalizado, pospuesto)",
        examples=["activo"]
    )


class EventoCreate(EventoBase):
    """
    Schema para el registro de un nuevo evento.
    Incluye obligatoriamente el objeto 'organizador'.
    """
    organizador: OrganizadorBase = Field(
        ...,
        description="Datos del organizador del evento"
    )
    asistentes: Optional[List[AsistenteCreate]] = Field(
        default_factory=list,
        description="Lista opcional inicial de asistentes registrados"
    )


class EventoUpdate(BaseModel):
    """
    Schema para la actualización parcial o total de un evento existente.
    """
    nombre: Optional[str] = Field(None, min_length=3, max_length=150)
    descripcion: Optional[str] = Field(None, min_length=10, max_length=2000)
    categoria: Optional[str] = Field(None, min_length=2, max_length=60)
    fecha: Optional[str] = Field(None, pattern=r"^\d{4}-\d{2}-\d{2}$")
    hora: Optional[str] = Field(None, pattern=r"^(?:[01]\d|2[0-3]):[0-5]\d(?::[0-5]\d)?$")
    capacidad: Optional[int] = Field(None, gt=0)
    ubicacion: Optional[str] = Field(None, min_length=3, max_length=250)
    estado: Optional[str] = Field(None, min_length=3, max_length=50)
    organizador: Optional[OrganizadorUpdate] = None


class EventoResponse(EventoBase):
    """
    Schema de respuesta para un evento, incluyendo _id/id y el organizador completo.
    """
    id: str = Field(..., alias="_id", description="Identificador único del evento (MongoDB ObjectId)")
    organizador: OrganizadorBase
    asistentes: List[AsistenteResponse] = Field(default_factory=list)
    total_asistentes: int = Field(default=0, description="Cantidad actual de asistentes registrados")
    cupos_disponibles: int = Field(default=0, description="Cupos restantes disponibles")

    model_config = ConfigDict(
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "_id": "67104b2b9f1b2c3d4e5f6a7b",
                "nombre": "Conferencia Internacional de Inteligencia Artificial 2026",
                "descripcion": "Encuentro global de especialistas, investigadores y desarrolladores de IA.",
                "categoria": "Tecnología",
                "fecha": "2026-11-20",
                "hora": "09:30",
                "capacidad": 150,
                "ubicacion": "Auditorio Principal de Postgrado, Piso 3",
                "estado": "activo",
                "organizador": {
                    "nombre": "Fundación Innovación Tech",
                    "contacto": "contacto@innovaciontech.org"
                },
                "asistentes": [
                    {
                        "nombre": "Ana García Morales",
                        "contacto": "ana.garcia@gmail.com",
                        "fecha_registro": "2026-10-16 14:20:00 UTC"
                    }
                ],
                "total_asistentes": 1,
                "cupos_disponibles": 149
            }
        }
    )


class MensajeResponse(BaseModel):
    mensaje: str
    detalle: Optional[Any] = None
