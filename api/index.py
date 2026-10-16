"""
Punto de entrada para el despliegue serverless en Vercel.
Importa la instancia FastAPI principal de main.py.
"""
from main import app

# Exporta app para el runtime de Vercel
__all__ = ["app"]
