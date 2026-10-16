from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Path, Query, status

from core.database import get_eventos_collection
from schemas.evento import (
    EventoCreate,
    EventoUpdate,
    EventoResponse,
    MensajeResponse
)
from schemas.asistente import (
    AsistenteCreate,
    AsistentesListResponse
)
from utils.helpers import validate_object_id, serialize_evento

router = APIRouter(prefix="/eventos", tags=["Eventos"])


# ---------------------------------------------------------------------------
# 1. REGISTRAR UN NUEVO EVENTO
# ---------------------------------------------------------------------------
@router.post(
    "/",
    response_model=EventoResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar un nuevo evento",
    description="Crea un nuevo documento de evento en la colección MongoDB incluyendo el objeto organizador y asistentes iniciales."
)
def crear_evento(evento_in: EventoCreate):
    collection = get_eventos_collection()

    # Validación de no duplicidad básica por nombre, fecha y hora
    duplicado = collection.find_one({
        "nombre": {"$regex": f"^{evento_in.nombre.strip()}$", "$options": "i"},
        "fecha": evento_in.fecha,
        "hora": evento_in.hora
    })
    if duplicado:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Ya existe un evento con el nombre '{evento_in.nombre}' en la fecha {evento_in.fecha} a las {evento_in.hora}."
        )

    # Preparación de datos a insertar
    evento_dict = evento_in.model_dump()

    # Formatear la fecha de registro para los asistentes iniciales si existen
    if "asistentes" in evento_dict and evento_dict["asistentes"]:
        for asistente in evento_dict["asistentes"]:
            if "fecha_registro" not in asistente or not asistente["fecha_registro"]:
                asistente["fecha_registro"] = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

        # Validar que no sobrepase la capacidad inicial
        if len(evento_dict["asistentes"]) > evento_dict["capacidad"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"La cantidad de asistentes iniciales ({len(evento_dict['asistentes'])}) supera la capacidad del evento ({evento_dict['capacidad']})."
            )
    else:
        evento_dict["asistentes"] = []

    insert_result = collection.insert_one(evento_dict)
    creado = collection.find_one({"_id": insert_result.inserted_id})
    return serialize_evento(creado)


# ---------------------------------------------------------------------------
# 2. LISTAR TODOS LOS EVENTOS (Con filtros opcionales integrados)
# ---------------------------------------------------------------------------
@router.get(
    "/",
    response_model=List[EventoResponse],
    summary="Listar todos los eventos",
    description="Obtiene todos los eventos registrados con opción de filtrado general por nombre, categoría, estado y fecha, además de paginación."
)
def listar_eventos(
    nombre: Optional[str] = Query(None, description="Filtrar por coincidencia en el nombre"),
    categoria: Optional[str] = Query(None, description="Filtrar por categoría exacta o parcial"),
    estado: Optional[str] = Query(None, description="Filtrar por estado del evento"),
    fecha: Optional[str] = Query(None, pattern=r"^\d{4}-\d{2}-\d{2}$", description="Filtrar por fecha (YYYY-MM-DD)"),
    skip: int = Query(0, ge=0, description="Cantidad de registros a omitir para paginación"),
    limit: int = Query(50, ge=1, le=100, description="Cantidad máxima de registros a retornar")
):
    collection = get_eventos_collection()
    query = {}

    if nombre:
        query["nombre"] = {"$regex": nombre.strip(), "$options": "i"}
    if categoria:
        query["categoria"] = {"$regex": f"^{categoria.strip()}$", "$options": "i"}
    if estado:
        query["estado"] = {"$regex": f"^{estado.strip()}$", "$options": "i"}
    if fecha:
        query["fecha"] = fecha.strip()

    cursor = collection.find(query).skip(skip).limit(limit).sort("fecha", 1)
    eventos = [serialize_evento(doc) for doc in cursor]
    return eventos


# ---------------------------------------------------------------------------
# 6. BUSCAR EVENTOS POR NOMBRE (Ruta específica)
# ---------------------------------------------------------------------------
@router.get(
    "/buscar",
    response_model=List[EventoResponse],
    summary="Buscar eventos por nombre",
    description="Busca eventos cuyos nombres contengan la palabra o frase especificada (búsqueda insensible a mayúsculas)."
)
def buscar_eventos_por_nombre(
    nombre: str = Query(..., min_length=1, description="Texto a buscar en el nombre del evento")
):
    collection = get_eventos_collection()
    query = {"nombre": {"$regex": nombre.strip(), "$options": "i"}}
    cursor = collection.find(query).sort("fecha", 1)
    resultados = [serialize_evento(doc) for doc in cursor]
    return resultados


# ---------------------------------------------------------------------------
# 7. FILTRAR EVENTOS POR CATEGORÍA (Ruta específica)
# ---------------------------------------------------------------------------
@router.get(
    "/categoria/{categoria}",
    response_model=List[EventoResponse],
    summary="Filtrar eventos por categoría",
    description="Filtra y lista todos los eventos pertenecientes a una categoría específica."
)
def filtrar_por_categoria(categoria: str):
    collection = get_eventos_collection()
    query = {"categoria": {"$regex": f"^{categoria.strip()}$", "$options": "i"}}
    cursor = collection.find(query).sort("fecha", 1)
    eventos = [serialize_evento(doc) for doc in cursor]
    return eventos


# ---------------------------------------------------------------------------
# 8. FILTRAR EVENTOS POR ESTADO (Ruta específica)
# ---------------------------------------------------------------------------
@router.get(
    "/estado/{estado}",
    response_model=List[EventoResponse],
    summary="Filtrar eventos por estado",
    description="Filtra y lista todos los eventos según su estado (ej: activo, cancelado, finalizado)."
)
def filtrar_por_estado(estado: str):
    collection = get_eventos_collection()
    query = {"estado": {"$regex": f"^{estado.strip()}$", "$options": "i"}}
    cursor = collection.find(query).sort("fecha", 1)
    eventos = [serialize_evento(doc) for doc in cursor]
    return eventos


# ---------------------------------------------------------------------------
# 9. FILTRAR EVENTOS POR FECHA (Ruta específica)
# ---------------------------------------------------------------------------
@router.get(
    "/fecha/{fecha}",
    response_model=List[EventoResponse],
    summary="Filtrar eventos por fecha",
    description="Filtra y lista todos los eventos programados para una fecha específica (YYYY-MM-DD)."
)
def filtrar_por_fecha(fecha: str = Path(..., pattern=r"^\d{4}-\d{2}-\d{2}$", description="Fecha en formato YYYY-MM-DD")):
    collection = get_eventos_collection()
    query = {"fecha": fecha.strip()}
    cursor = collection.find(query).sort("hora", 1)
    eventos = [serialize_evento(doc) for doc in cursor]
    return eventos


# ---------------------------------------------------------------------------
# 3. CONSULTAR UN EVENTO POR SU IDENTIFICADOR (_id)
# ---------------------------------------------------------------------------
@router.get(
    "/{id}",
    response_model=EventoResponse,
    summary="Consultar un evento por ID",
    description="Obtiene la información completa de un evento mediante su _id de MongoDB."
)
def obtener_evento_por_id(id: str):
    oid = validate_object_id(id)
    collection = get_eventos_collection()
    evento = collection.find_one({"_id": oid})
    if not evento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No se encontró ningún evento con el identificador '{id}'."
        )
    return serialize_evento(evento)


# ---------------------------------------------------------------------------
# 4. MODIFICAR LA INFORMACIÓN DE UN EVENTO
# ---------------------------------------------------------------------------
@router.put(
    "/{id}",
    response_model=EventoResponse,
    summary="Modificar la información de un evento",
    description="Actualiza los campos proporcionados de un evento existente."
)
def actualizar_evento(id: str, evento_in: EventoUpdate):
    oid = validate_object_id(id)
    collection = get_eventos_collection()

    evento_actual = collection.find_one({"_id": oid})
    if not evento_actual:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No se encontró ningún evento con el identificador '{id}' para actualizar."
        )

    # Extraer únicamente los campos enviados
    update_data = evento_in.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se enviaron campos válidos para actualizar."
        )

    # Validación de capacidad contra asistentes ya registrados
    if "capacidad" in update_data:
        nueva_capacidad = update_data["capacidad"]
        asistentes_actuales = len(evento_actual.get("asistentes", []))
        if nueva_capacidad < asistentes_actuales:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"La nueva capacidad ({nueva_capacidad}) no puede ser menor al número de asistentes actualmente registrados ({asistentes_actuales})."
            )

    # Si se actualiza el organizador anidado
    if "organizador" in update_data and update_data["organizador"]:
        org_actual = evento_actual.get("organizador", {})
        org_actual.update({k: v for k, v in update_data["organizador"].items() if v is not None})
        update_data["organizador"] = org_actual

    collection.update_one({"_id": oid}, {"$set": update_data})
    evento_actualizado = collection.find_one({"_id": oid})
    return serialize_evento(evento_actualizado)


# ---------------------------------------------------------------------------
# 5. ELIMINAR UN EVENTO
# ---------------------------------------------------------------------------
@router.delete(
    "/{id}",
    response_model=MensajeResponse,
    summary="Eliminar un evento",
    description="Elimina permanentemente un evento de la colección por su identificador."
)
def eliminar_evento(id: str):
    oid = validate_object_id(id)
    collection = get_eventos_collection()

    resultado = collection.delete_one({"_id": oid})
    if resultado.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No se encontró ningún evento con el identificador '{id}' para eliminar."
        )

    return MensajeResponse(
        mensaje=f"Evento con ID '{id}' eliminado exitosamente de la base de datos."
    )


# ---------------------------------------------------------------------------
# 10. REGISTRAR Y CONSULTAR LOS ASISTENTES DE UN EVENTO
# ---------------------------------------------------------------------------
@router.post(
    "/{id}/asistentes",
    response_model=EventoResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar un asistente en el evento",
    description="Registra un nuevo participante en la lista de asistentes del evento, verificando disponibilidad de cupo y no duplicidad."
)
def registrar_asistente(id: str, asistente_in: AsistenteCreate):
    oid = validate_object_id(id)
    collection = get_eventos_collection()

    evento = collection.find_one({"_id": oid})
    if not evento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No se encontró el evento con ID '{id}' para registrar al asistente."
        )

    # Validar estado del evento
    estado_evento = str(evento.get("estado", "")).lower()
    if estado_evento in ["cancelado", "finalizado"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"No se pueden registrar asistentes en un evento en estado '{evento.get('estado')}'."
        )

    asistentes = evento.get("asistentes", [])
    capacidad = int(evento.get("capacidad", 0))

    # Validar capacidad máxima
    if len(asistentes) >= capacidad:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"El evento ha alcanzado su capacidad máxima permitida de {capacidad} asistentes."
        )

    # Validar que no esté ya registrado con el mismo contacto
    contacto_limpio = asistente_in.contacto.strip().lower()
    for existente in asistentes:
        if existente.get("contacto", "").strip().lower() == contacto_limpio:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"El asistente con contacto '{asistente_in.contacto}' ya está registrado en este evento."
            )

    # Crear el nuevo asistente con timestamp
    nuevo_asistente = {
        "nombre": asistente_in.nombre.strip(),
        "contacto": asistente_in.contacto.strip(),
        "fecha_registro": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    }

    collection.update_one(
        {"_id": oid},
        {"$push": {"asistentes": nuevo_asistente}}
    )

    evento_actualizado = collection.find_one({"_id": oid})
    return serialize_evento(evento_actualizado)


@router.get(
    "/{id}/asistentes",
    response_model=AsistentesListResponse,
    summary="Consultar asistentes de un evento",
    description="Retorna la lista de todos los participantes registrados en el evento junto al balance de cupos."
)
def consultar_asistentes(id: str):
    oid = validate_object_id(id)
    collection = get_eventos_collection()

    evento = collection.find_one({"_id": oid})
    if not evento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No se encontró el evento con ID '{id}'."
        )

    asistentes = evento.get("asistentes", [])
    capacidad = int(evento.get("capacidad", 0))
    total = len(asistentes)
    disponibles = max(0, capacidad - total)

    return AsistentesListResponse(
        evento_id=str(evento["_id"]),
        nombre_evento=evento.get("nombre", "Sin nombre"),
        capacidad_total=capacidad,
        total_asistentes=total,
        cupos_disponibles=disponibles,
        asistentes=asistentes
    )
