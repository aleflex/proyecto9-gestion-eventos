from datetime import datetime, timezone
from pydantic import BaseModel, Field


class AsistenteBase(BaseModel):
    """
    Información de un asistente o participante de un evento.
    """
    nombre: str = Field(
        ...,
        min_length=2,
        max_length=120,
        description="Nombre completo del participante o asistente",
        examples=["Ana García Morales"]
    )
    contacto: str = Field(
        ...,
        min_length=3,
        max_length=120,
        description="Correo o número telefónico del asistente",
        examples=["ana.garcia@gmail.com"]
    )


class AsistenteCreate(AsistenteBase):
    pass


class AsistenteResponse(AsistenteBase):
    fecha_registro: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
        description="Fecha y hora en la que se registró el asistente"
    )


class AsistentesListResponse(BaseModel):
    evento_id: str
    nombre_evento: str
    capacidad_total: int
    total_asistentes: int
    cupos_disponibles: int
    asistentes: list[AsistenteResponse]
