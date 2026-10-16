import mongomock
import pytest
from fastapi.testclient import TestClient

import core.database as db_module
import api.routes as routes_module
from main import app

# Inicializar cliente de pruebas en memoria con mongomock
mock_client = mongomock.MongoClient()
mock_db = mock_client["test_db"]
mock_collection = mock_db["eventos"]

# Reemplazar la colección tanto en core.database como en api.routes
db_module.get_eventos_collection = lambda: mock_collection
routes_module.get_eventos_collection = lambda: mock_collection

client = TestClient(app)


@pytest.fixture(autouse=True)
def limpiar_coleccion():
    """Limpia la colección mock antes de cada prueba."""
    mock_collection.delete_many({})


def test_root_endpoint():
    """Verifica que el endpoint raíz responda correctamente."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["estado"] == "operativo"
    assert "documentacion" in data


def test_crear_evento_exitoso():
    """Funcionalidad 1: Registrar un nuevo evento."""
    payload = {
        "nombre": "Cumbre de Ciberseguridad 2026",
        "descripcion": "Congreso internacional sobre seguridad defensiva y ethical hacking.",
        "categoria": "Ciberseguridad",
        "fecha": "2026-11-15",
        "hora": "10:00",
        "capacidad": 50,
        "ubicacion": "Hotel Radisson, Salón Diamante",
        "estado": "activo",
        "organizador": {
            "nombre": "Sociedad de Seguridad Informática",
            "contacto": "info@seguridad.org"
        },
        "asistentes": []
    }
    response = client.post("/api/v1/eventos/", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["nombre"] == payload["nombre"]
    assert data["_id"] is not None
    assert data["cupos_disponibles"] == 50
    assert data["total_asistentes"] == 0
    assert data["organizador"]["nombre"] == payload["organizador"]["nombre"]


def test_crear_evento_duplicado():
    """Verifica validación de no duplicidad de evento con mismo nombre, fecha y hora."""
    payload = {
        "nombre": "Taller Python FastAPI",
        "descripcion": "Aprende a construir APIs REST modernas con Python.",
        "categoria": "Desarrollo",
        "fecha": "2026-12-01",
        "hora": "18:00",
        "capacidad": 20,
        "ubicacion": "Online Google Meet",
        "estado": "activo",
        "organizador": {
            "nombre": "Dev Community",
            "contacto": "contacto@dev.org"
        }
    }
    res1 = client.post("/api/v1/eventos/", json=payload)
    assert res1.status_code == 201
    res2 = client.post("/api/v1/eventos/", json=payload)
    assert res2.status_code == 409


def test_listar_eventos():
    """Funcionalidad 2: Listar todos los eventos."""
    for i in range(3):
        mock_collection.insert_one({
            "nombre": f"Evento de Prueba {i}",
            "descripcion": f"Descripción de prueba detallada del evento número {i}.",
            "categoria": "General",
            "fecha": f"2026-11-0{i+1}",
            "hora": "14:00",
            "capacidad": 30,
            "ubicacion": "Campus Universitario",
            "estado": "activo",
            "asistentes": [],
            "organizador": {"nombre": "Org Test", "contacto": "test@test.com"}
        })

    response = client.get("/api/v1/eventos/")
    assert response.status_code == 200
    eventos = response.json()
    assert len(eventos) == 3


def test_consultar_evento_por_id():
    """Funcionalidad 3: Consultar un evento mediante su identificador."""
    res_insert = mock_collection.insert_one({
        "nombre": "Hackathon Universitaria 2026",
        "descripcion": "Competencia de desarrollo de software durante 48 horas seguidas.",
        "categoria": "Innovación",
        "fecha": "2026-10-30",
        "hora": "08:00",
        "capacidad": 100,
        "ubicacion": "Facultad de Ingeniería de Sistemas",
        "estado": "activo",
        "asistentes": [],
        "organizador": {"nombre": "Club de Algoritmia", "contacto": "hackathon@uni.edu"}
    })
    evento_id = str(res_insert.inserted_id)

    response = client.get(f"/api/v1/eventos/{evento_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["nombre"] == "Hackathon Universitaria 2026"
    assert data["_id"] == evento_id


def test_modificar_evento():
    """Funcionalidad 4: Modificar la información de un evento."""
    res_insert = mock_collection.insert_one({
        "nombre": "Concierto Acústico",
        "descripcion": "Presentación en vivo de solistas y bandas locales de jazz y blues.",
        "categoria": "Música",
        "fecha": "2026-11-10",
        "hora": "20:00",
        "capacidad": 80,
        "ubicacion": "Teatro al Aire Libre",
        "estado": "activo",
        "asistentes": [],
        "organizador": {"nombre": "Arte Vivo", "contacto": "arte@musica.org"}
    })
    evento_id = str(res_insert.inserted_id)

    update_payload = {
        "ubicacion": "Teatro Municipal Alberto Saavedra Pérez",
        "capacidad": 120,
        "estado": "en_curso"
    }
    response = client.put(f"/api/v1/eventos/{evento_id}", json=update_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["ubicacion"] == "Teatro Municipal Alberto Saavedra Pérez"
    assert data["capacidad"] == 120
    assert data["estado"] == "en_curso"


def test_eliminar_evento():
    """Funcionalidad 5: Eliminar un evento."""
    res_insert = mock_collection.insert_one({
        "nombre": "Evento a Cancelar y Eliminar",
        "descripcion": "Evento temporal para validación del endpoint de borrado.",
        "categoria": "Varios",
        "fecha": "2026-12-31",
        "hora": "23:00",
        "capacidad": 10,
        "ubicacion": "Local Privado",
        "estado": "cancelado",
        "asistentes": [],
        "organizador": {"nombre": "Admin", "contacto": "admin@test.com"}
    })
    evento_id = str(res_insert.inserted_id)

    response = client.delete(f"/api/v1/eventos/{evento_id}")
    assert response.status_code == 200
    assert "eliminado exitosamente" in response.json()["mensaje"]

    # Verificar que ya no existe
    res_get = client.get(f"/api/v1/eventos/{evento_id}")
    assert res_get.status_code == 404


def test_buscar_eventos_por_nombre():
    """Funcionalidad 6: Buscar eventos por nombre."""
    mock_collection.insert_one({
        "nombre": "Seminario de Machine Learning",
        "descripcion": "Modelos predictivos y redes neuronales profundas aplicadas.",
        "categoria": "Inteligencia Artificial",
        "fecha": "2026-11-25",
        "hora": "15:00",
        "capacidad": 40,
        "ubicacion": "Virtual",
        "estado": "activo",
        "asistentes": [],
        "organizador": {"nombre": "AI Lab", "contacto": "ai@lab.org"}
    })

    # Búsqueda parcial e insensible a mayúsculas
    response = client.get("/api/v1/eventos/buscar?nombre=machine")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["nombre"] == "Seminario de Machine Learning"


def test_filtrar_por_categoria():
    """Funcionalidad 7: Filtrar eventos por categoría."""
    mock_collection.insert_one({
        "nombre": "Torneo de Ajedrez Rápido",
        "descripcion": "Torneo blitz a 5 rondas para todas las categorías universitarias.",
        "categoria": "Deportes",
        "fecha": "2026-11-05",
        "hora": "16:00",
        "capacidad": 32,
        "ubicacion": "Coliseo Cerrado",
        "estado": "activo",
        "asistentes": [],
        "organizador": {"nombre": "Federación Ajedrez", "contacto": "ajedrez@dep.org"}
    })

    response = client.get("/api/v1/eventos/categoria/Deportes")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert data[0]["categoria"] == "Deportes"


def test_filtrar_por_estado():
    """Funcionalidad 8: Filtrar eventos por estado."""
    mock_collection.insert_one({
        "nombre": "Feria Gastronómica de Otoño",
        "descripcion": "Muestra de platos típicos y cocina fusión tradicional.",
        "categoria": "Cultura",
        "fecha": "2026-11-18",
        "hora": "11:00",
        "capacidad": 200,
        "ubicacion": "Plaza Mayor",
        "estado": "finalizado",
        "asistentes": [],
        "organizador": {"nombre": "Asociación Culinaria", "contacto": "feria@gastronomia.bo"}
    })

    response = client.get("/api/v1/eventos/estado/finalizado")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert data[0]["estado"] == "finalizado"


def test_filtrar_por_fecha():
    """Funcionalidad 9: Filtrar eventos por fecha."""
    mock_collection.insert_one({
        "nombre": "Lanzamiento de Startup Tech",
        "descripcion": "Presentación de la plataforma ante inversores y medios de prensa.",
        "categoria": "Negocios",
        "fecha": "2026-12-10",
        "hora": "19:00",
        "capacidad": 60,
        "ubicacion": "Cowork Innovation Hub",
        "estado": "activo",
        "asistentes": [],
        "organizador": {"nombre": "Founders Club", "contacto": "founders@hub.com"}
    })

    response = client.get("/api/v1/eventos/fecha/2026-12-10")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert data[0]["fecha"] == "2026-12-10"


def test_registrar_y_consultar_asistentes():
    """Funcionalidad 10: Registrar y consultar los asistentes de un evento."""
    res_insert = mock_collection.insert_one({
        "nombre": "Workshop de Docker y Kubernetes",
        "descripcion": "Contenedores y orquestación práctica en entornos de producción.",
        "categoria": "DevOps",
        "fecha": "2026-11-22",
        "hora": "10:00",
        "capacidad": 2,  # Capacidad pequeña para probar límite
        "ubicacion": "Laboratorio 4",
        "estado": "activo",
        "asistentes": [],
        "organizador": {"nombre": "Cloud Group", "contacto": "cloud@devops.org"}
    })
    evento_id = str(res_insert.inserted_id)

    # 1. Registrar primer asistente
    asistente_1 = {
        "nombre": "Carlos Mendoza",
        "contacto": "carlos.mendoza@correo.com"
    }
    res_reg1 = client.post(f"/api/v1/eventos/{evento_id}/asistentes", json=asistente_1)
    assert res_reg1.status_code == 201
    assert res_reg1.json()["total_asistentes"] == 1
    assert res_reg1.json()["cupos_disponibles"] == 1

    # 2. Intentar registrar al mismo asistente (debe fallar por contacto duplicado)
    res_dup = client.post(f"/api/v1/eventos/{evento_id}/asistentes", json=asistente_1)
    assert res_dup.status_code == 409

    # 3. Registrar segundo asistente (llenando la capacidad)
    asistente_2 = {
        "nombre": "Laura Valenzuela",
        "contacto": "laura.v@correo.com"
    }
    res_reg2 = client.post(f"/api/v1/eventos/{evento_id}/asistentes", json=asistente_2)
    assert res_reg2.status_code == 201
    assert res_reg2.json()["total_asistentes"] == 2
    assert res_reg2.json()["cupos_disponibles"] == 0

    # 4. Intentar registrar un tercer asistente (debe fallar por capacidad máxima)
    asistente_3 = {
        "nombre": "Marcos Rivera",
        "contacto": "marcos@correo.com"
    }
    res_lleno = client.post(f"/api/v1/eventos/{evento_id}/asistentes", json=asistente_3)
    assert res_lleno.status_code == 400
    assert "capacidad máxima" in res_lleno.json()["detail"]

    # 5. Consultar los asistentes registrados (GET /asistentes)
    res_asistentes = client.get(f"/api/v1/eventos/{evento_id}/asistentes")
    assert res_asistentes.status_code == 200
    datos_asistentes = res_asistentes.json()
    assert datos_asistentes["total_asistentes"] == 2
    assert datos_asistentes["cupos_disponibles"] == 0
    assert len(datos_asistentes["asistentes"]) == 2
    assert datos_asistentes["asistentes"][0]["nombre"] == "Carlos Mendoza"
    assert datos_asistentes["asistentes"][1]["nombre"] == "Laura Valenzuela"


def test_validaciones_errores():
    """Pruebas de validación de ObjectId inválido y 404."""
    # ObjectId con caracteres o longitud inválida -> 400
    res_inv = client.get("/api/v1/eventos/id-invalido-123")
    assert res_inv.status_code == 400
    assert "no es un ObjectId válido" in res_inv.json()["detail"]

    # ObjectId con formato válido pero no existente -> 404
    res_404 = client.get("/api/v1/eventos/507f1f77bcf86cd799439011")
    assert res_404.status_code == 404
