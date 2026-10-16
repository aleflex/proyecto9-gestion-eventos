# 🎟️ PROYECTO 9: Sistema de Gestión de Eventos

> API REST moderna, escalable y robusta desarrollada con **FastAPI** y **MongoDB**, diseñada para la administración integral de eventos, control de fechas, ubicaciones, aforos, estados y registro de participantes.

[![CI Pipeline](https://github.com/gtorrico-fs/task-manager-API/actions/workflows/ci.yml/badge.svg)](https://github.com)
[![Python Version](https://img.shields.io/badge/python-3.10%20%7C%203.12-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-009688.svg?logo=fastapi)](https://fastapi.tiangolo.com)
[![MongoDB](https://img.shields.io/badge/MongoDB-Single%20Collection-green.svg?logo=mongodb)](https://www.mongodb.com/)
[![Vercel](https://img.shields.io/badge/Deploy-Vercel-black.svg?logo=vercel)](https://vercel.com)

---

## 📋 Tabla de Contenidos
1. [Objetivo del Proyecto](#-objetivo-del-proyecto)
2. [Estructura del Documento en MongoDB](#-estructura-del-documento-en-mongodb)
3. [Funcionalidades de la API](#-funcionalidades-de-la-api)
4. [Arquitectura del Proyecto](#-arquitectura-del-proyecto)
5. [Estrategia de Ramas Git (Flujo de Trabajo)](#-estrategia-de-ramas-git-flujo-de-trabajo)
6. [Integración Continua (GitHub Actions)](#-integración-continua-github-actions)
7. [Instalación y Ejecución Local](#-instalación-y-ejecución-local)
8. [Guía de Pruebas Automatizadas](#-guía-de-pruebas-automatizadas)
9. [Guía Paso a Paso: Despliegue en Vercel](#-guía-paso-a-paso-despliegue-en-vercel)
10. [Documentación Interactiva de Endpoints](#-documentación-interactiva-de-endpoints)

---

## 🎯 Objetivo del Proyecto
Desarrollar una API REST completa y validada utilizando **FastAPI** y **MongoDB** como motor de persistencia no relacional, almacenando toda la información en una **única colección** (`eventos`) y garantizando:
- Validación rigurosa de tipos con **Pydantic v2**.
- Verificación automática de capacidades y aforos en tiempo real.
- Prevención de duplicidad de eventos y participantes.
- Integración Continua (CI) mediante **GitHub Actions** en múltiples versiones de Python (3.10 y 3.12).
- Compatibilidad para despliegue Serverless en **Vercel** conectado a **MongoDB Atlas**.

---

## 📄 Estructura del Documento en MongoDB
Cada documento de la colección `eventos` cumple estrictamente con el esquema mínimo requerido:

```json
{
  "_id": "67104b2b9f1b2c3d4e5f6a7b",
  "nombre": "Conferencia Internacional de Inteligencia Artificial 2026",
  "descripcion": "Encuentro global de especialistas, investigadores y desarrolladores de IA.",
  "categoria": "Tecnología",
  "fecha": "2026-11-20",
  "hora": "09:30",
  "capacidad": 150,
  "ubicacion": "Auditorio Principal de Postgrado, Piso 3",
  "estado": "activo",
  "asistentes": [
    {
      "nombre": "Ana García Morales",
      "contacto": "ana.garcia@gmail.com",
      "fecha_registro": "2026-10-16 14:20:00 UTC"
    }
  ],
  "organizador": {
    "nombre": "Fundación Innovación Tech",
    "contacto": "contacto@innovaciontech.org"
  }
}
```

### Detalle de Campos:
* `_id`: Identificador único generado por MongoDB (ObjectId representado como string).
* `nombre`: Nombre del evento (`str`, min: 3, max: 150 caracteres).
* `descripcion`: Detalle y agenda del evento (`str`, min: 10 caracteres).
* `categoria`: Categoría temática (`str`, ej: Tecnología, Deportes, Cultura, Negocios).
* `fecha`: Fecha en formato estándar `YYYY-MM-DD`.
* `hora`: Hora de inicio en formato militar `HH:MM`.
* `capacidad`: Aforo máximo permitido (`int > 0`).
* `ubicacion`: Lugar físico o enlace virtual (`str`).
* `estado`: Estado del evento (`activo`, `en_curso`, `finalizado`, `cancelado`).
* `asistentes[]`: Arreglo de participantes registrados dentro del mismo documento.
* `organizador{}`: Objeto anidado con los campos obligatorios:
  * `nombre`: Nombre del organizador o institución.
  * `contacto`: Email o teléfono de contacto.

---

## 🚀 Funcionalidades de la API

| # | Funcionalidad | Método | Ruta del Endpoint | Descripción |
|---|---|:---:|---|---|
| **1** | Registrar nuevo evento | `POST` | `/api/v1/eventos/` | Crea un evento con su organizador y estado inicial. |
| **2** | Listar todos los eventos | `GET` | `/api/v1/eventos/` | Retorna lista de eventos con soporte de paginación y filtros. |
| **3** | Consultar evento por ID | `GET` | `/api/v1/eventos/{id}` | Busca un evento por su `_id` de MongoDB. |
| **4** | Modificar evento | `PUT` | `/api/v1/eventos/{id}` | Actualiza información validando límites de capacidad. |
| **5** | Eliminar evento | `DELETE` | `/api/v1/eventos/{id}` | Elimina el evento permanentemente. |
| **6** | Buscar eventos por nombre | `GET` | `/api/v1/eventos/buscar?nombre=...` | Búsqueda parcial e insensible a mayúsculas. |
| **7** | Filtrar por categoría | `GET` | `/api/v1/eventos/categoria/{categoria}` | Lista eventos de una categoría específica. |
| **8** | Filtrar por estado | `GET` | `/api/v1/eventos/estado/{estado}` | Lista eventos por estado (`activo`, `cancelado`, etc.). |
| **9** | Filtrar por fecha | `GET` | `/api/v1/eventos/fecha/{fecha}` | Lista eventos para una fecha `YYYY-MM-DD`. |
| **10.1** | Registrar asistente | `POST` | `/api/v1/eventos/{id}/asistentes` | Registra un participante controlando cupo disponible. |
| **10.2** | Consultar asistentes | `GET` | `/api/v1/eventos/{id}/asistentes` | Retorna participantes y balance de cupos. |

---

## 📁 Arquitectura del Proyecto

Siguiendo el estándar de desarrollo modular y los requerimientos del flujo de verificación:

```text
├── .github/
│   └── workflows/
│       └── ci.yml               # Workflow de GitHub Actions (Python 3.10 y 3.12)
├── api/
│   ├── __init__.py              # Exportación de router de eventos
│   ├── routes.py                # Implementación de los 10 endpoints requeridos
│   └── index.py                 # Punto de entrada Serverless para Vercel
├── core/
│   ├── __init__.py              # Exportación de configuración y conexión DB
│   ├── config.py                # Variables de entorno con pydantic-settings
│   └── database.py              # Conexión diferida (lazy) a MongoDB con PyMongo
├── schemas/
│   ├── __init__.py              # Modelos Pydantic v2
│   ├── organizador.py           # Esquema del objeto organizador
│   ├── asistente.py             # Esquema de asistentes
│   └── evento.py                # Esquemas EventoCreate, EventoUpdate, EventoResponse
├── utils/
│   ├── __init__.py              # Utilidades compartidas
│   └── helpers.py               # Validador de ObjectId y serializador BSON -> JSON
├── tests/
│   ├── __init__.py
│   └── test_eventos.py          # Pruebas automatizadas con mongomock y pytest
├── .env.example                 # Plantilla de variables de entorno
├── .gitignore                   # Exclusión de archivos sensibles y temporales
├── main.py                      # Instancia principal de FastAPI, CORS y rutas raíz
├── requirements.txt             # Dependencias de producción
├── vercel.json                  # Configuración de rutas y runtime para Vercel
└── README.md                    # Documentación técnica completa
```

---

## 🌿 Estrategia de Ramas Git (Flujo de Trabajo)
El repositorio implementa el flujo de trabajo visto en clases con **3 ramificaciones**:

```text
  main (Producción - Despliegue en Vercel)
   ▲
   │ Merge PR (Release v1.0.0)
  dev (Desarrollo e integración continua)
   ▲
   │ Merge PR
  feature/gestion-eventos (Desarrollo de las 10 funcionalidades)
```

### Comandos Git utilizados para el flujo:
```bash
# 1. Crear e iniciar en rama main
git checkout -b main
git add .
git commit -m "chore: initial project setup and ci configuration"

# 2. Crear rama de desarrollo dev
git checkout -b dev

# 3. Crear rama para la funcionalidad
git checkout -b feature/gestion-eventos

# 4. Desarrollar e integrar cambios
git add .
git commit -m "feat: implement 10 event management endpoints and schemas"

# 5. Integrar feature en dev
git checkout dev
git merge --no-ff feature/gestion-eventos -m "merge: feature/gestion-eventos into dev"

# 6. Integrar dev en main para producción
git checkout main
git merge --no-ff dev -m "merge: dev into main (Release v1.0.0)"

# 7. Publicar todas las ramas en GitHub
git push -u origin --all
```

---

## ⚙️ Integración Continua (GitHub Actions)
El workflow `.github/workflows/ci.yml` automatiza la verificación del código en cada `push` y `pull_request` sobre `main` y `dev`:

1. **Matriz de versiones**: Valida en **Python 3.10** y **Python 3.12.3**.
2. **Caché de Pip**: Acelera la descarga de paquetes.
3. **Compilación de módulos**: Ejecuta `python -m compileall -q main.py api core schemas utils`.
4. **Verificación de arranque**: Importa `from main import app` y certifica el registro de todas las rutas de la API utilizando variables de entorno de prueba.

---

## 💻 Instalación y Ejecución Local

### 1. Clonar el repositorio
```bash
git clone <URL_DE_TU_REPOSITORIO_GITHUB>
cd <CARPETA_DEL_REPOSITORIO>
```

### 2. Crear y activar entorno virtual
```bash
# En Windows:
python -m venv .venv
.venv\Scripts\activate

# En Linux / macOS:
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno
Crea el archivo `.env` a partir del ejemplo:
```bash
cp .env.example .env
```
Contenido recomendado de `.env`:
```ini
APP_NAME="Sistema de Gestión de Eventos"
APP_VERSION="1.0.0"
API_V1_PREFIX="/api/v1"
MONGODB_URI="mongodb://localhost:27017"
MONGODB_DB="gestion_eventos_db"
MONGODB_COLLECTION="eventos"
```

### 5. Iniciar la aplicación
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```
La API estará disponible en `http://localhost:8000`.

---

## 🧪 Guía de Pruebas Automatizadas
El proyecto incluye pruebas completas con `pytest` y `mongomock` (sin necesidad de tener MongoDB corriendo localmente):

```bash
# Ejecutar todas las pruebas con detalle
pytest tests/test_eventos.py -v
```

---

## ☁️ Guía Paso a Paso: Despliegue en Vercel

### Paso 1: Configurar Base de Datos en MongoDB Atlas (Gratuito)
1. Ingresa a [MongoDB Atlas](https://www.mongodb.com/cloud/atlas) e inicia sesión.
2. Crea un clúster gratuito **M0 Free Tier**.
3. En **Database Access**: Crea un usuario con rol *Read and write to any database* (guarda usuario y contraseña).
4. En **Network Access**: Añade la IP `0.0.0.0/0` (Allow Access from Anywhere) para permitir conexiones serverless de Vercel.
5. Haz clic en **Connect** > **Drivers** > copia la cadena de conexión:
   ```text
   mongodb+srv://<usuario>:<password>@cluster0.mongodb.net/?retryWrites=true&w=majority
   ```

### Paso 2: Subir el proyecto a GitHub
1. Crea un nuevo repositorio en GitHub.
2. Conecta el repositorio local y sube las 3 ramas:
   ```bash
   git remote add origin https://github.com/<tu-usuario>/<tu-repo>.git
   git push -u origin --all
   ```

### Paso 3: Desplegar en Vercel
1. Ingresa a [Vercel](https://vercel.com) e inicia sesión con tu cuenta de GitHub.
2. Haz clic en **Add New...** > **Project**.
3. Selecciona tu repositorio del proyecto.
4. En la sección **Environment Variables**, añade:
   * `APP_NAME`: `Sistema de Gestión de Eventos`
   * `APP_VERSION`: `1.0.0`
   * `API_V1_PREFIX`: `/api/v1`
   * `MONGODB_URI`: `<tu_connection_string_de_mongodb_atlas>`
   * `MONGODB_DB`: `gestion_eventos_db`
   * `MONGODB_COLLECTION`: `eventos`
5. Haz clic en **Deploy**.
6. ¡Listo! Vercel te proporcionará una URL pública (ejemplo: `https://tu-proyecto.vercel.app`).

---

## 📖 Documentación Interactiva de Endpoints

Una vez desplegada o en ejecución local, puedes interactuar directamente con la API desde el navegador:

* **Swagger UI**: [`/docs`](http://localhost:8000/docs)
* **Redoc**: [`/redoc`](http://localhost:8000/redoc)
* **OpenAPI Schema**: [`/openapi.json`](http://localhost:8000/openapi.json)

### Ejemplos cURL de Prueba:

#### 1. Registrar un nuevo evento:
```bash
curl -X POST "http://localhost:8000/api/v1/eventos/" \
     -H "Content-Type: application/json" \
     -d '{
       "nombre": "Conferencia Tech 2026",
       "descripcion": "Innovaciones en IA, desarrollo backend y computación en la nube.",
       "categoria": "Tecnología",
       "fecha": "2026-11-20",
       "hora": "10:00",
       "capacidad": 100,
       "ubicacion": "Auditorio Principal de Postgrado",
       "estado": "activo",
       "organizador": {
         "nombre": "Fundación Tech Bolivia",
         "contacto": "contacto@techbolivia.org"
       }
     }'
```

#### 2. Registrar un participante:
```bash
curl -X POST "http://localhost:8000/api/v1/eventos/<EVENTO_ID>/asistentes" \
     -H "Content-Type: application/json" \
     -d '{
       "nombre": "Carlos Mendoza",
       "contacto": "carlos.mendoza@email.com"
     }'
```

#### 3. Consultar asistentes:
```bash
curl -X GET "http://localhost:8000/api/v1/eventos/<EVENTO_ID>/asistentes"
```

#### 4. Buscar eventos por nombre:
```bash
curl -X GET "http://localhost:8000/api/v1/eventos/buscar?nombre=tech"
```

---

## 👨‍💻 Autor
Proyecto desarrollado para la evaluación de Sistemas de Información / Ingeniería de Software.
Licencia MIT.
