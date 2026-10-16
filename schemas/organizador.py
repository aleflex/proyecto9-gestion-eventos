from pydantic import BaseModel, Field


class OrganizadorBase(BaseModel):
    """
    Información del organizador de un evento.
    """
    nombre: str = Field(
        ...,
        min_length=2,
        max_length=120,
        description="Nombre completo o entidad del organizador",
        examples=["Fundación Innovación Tech"]
    )
    contacto: str = Field(
        ...,
        min_length=3,
        max_length=120,
        description="Información de contacto (correo electrónico, teléfono o red social)",
        examples=["contacto@innovaciontech.org"]
    )


class OrganizadorCreate(OrganizadorBase):
    pass


class OrganizadorUpdate(BaseModel):
    nombre: str | None = Field(
        None,
        min_length=2,
        max_length=120,
        description="Nombre completo o entidad del organizador"
    )
    contacto: str | None = Field(
        None,
        min_length=3,
        max_length=120,
        description="Información de contacto del organizador"
    )


class OrganizadorResponse(OrganizadorBase):
    pass
