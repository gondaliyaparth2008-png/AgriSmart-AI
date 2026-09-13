"""
app/api/v1/router.py
---------------------
Aggregates all v1 endpoint routers into a single APIRouter
that is mounted at /api/v1 in main.py.
"""

from fastapi import APIRouter

from app.api.v1.endpoints import advisory, assistant, disease, health, weather

api_router = APIRouter()

api_router.include_router(disease.router)
api_router.include_router(advisory.router)
api_router.include_router(weather.router)
api_router.include_router(assistant.router)
api_router.include_router(health.router)
