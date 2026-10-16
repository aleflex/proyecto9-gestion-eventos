from typing import Any, Dict, Optional
from bson import ObjectId
from bson.errors import InvalidId
from fastapi import HTTPException, status


def validate_object_id(id_str: str) -> ObjectId:
    """
    Valida y convierte una cadena de texto a un ObjectId de MongoDB.
    Lanza HTTPException con código 400 si el formato es inválido.
    """
    if not id_str or not ObjectId.is_valid(id_str):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"El identificador '{id_str}' no es un ObjectId válido de MongoDB. Debe ser una cadena de 24 caracteres hexadecimales."
        )
    try:
        return ObjectId(id_str)
    except InvalidId:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Identificador '{id_str}' inválido para MongoDB."
        )


def serialize_evento(doc: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """
    Convierte un documento BSON obtenido de MongoDB a un diccionario compatible con Pydantic y JSON.
    Convierte el '_id' a string y añade campos calculados como total_asistentes y cupos_disponibles.
    """
    if not doc:
        return None

    data = dict(doc)
    oid = str(data.get("_id"))
    data["_id"] = oid
    data["id"] = oid

    # Garantizar asistentes como lista
    asistentes = data.get("asistentes") or []
    data["asistentes"] = asistentes

    # Cálculos de capacidad
    capacidad = int(data.get("capacidad", 0))
    total_asistentes = len(asistentes)
    data["total_asistentes"] = total_asistentes
    data["cupos_disponibles"] = max(0, capacidad - total_asistentes)

    # Garantizar organizador
    if "organizador" not in data or not isinstance(data["organizador"], dict):
        data["organizador"] = {
            "nombre": "Sin asignar",
            "contacto": "Sin contacto"
        }

    return data
