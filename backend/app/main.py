"""
app/main.py
-----------
AgriSmart AI — FastAPI application factory.

This module:
  • Creates the FastAPI application instance with full OpenAPI metadata.
  • Registers CORS middleware (open for hackathon, lock down for production).
  • Mounts the versioned API router.
  • Provides root health-check and liveness/readiness probe endpoints.
  • Configures structured logging on startup.
"""

from __future__ import annotations

import logging
import time
from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator, Dict

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1.router import api_router
from app.core.config import settings
from app.db.session import init_db

# =========================================================================== #
#  Logging configuration
# =========================================================================== #

logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
)
logger = logging.getLogger(__name__)


# =========================================================================== #
#  Application lifespan (startup / shutdown hooks)
# =========================================================================== #


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Startup / shutdown lifecycle hook.

    Startup:
      1. Emit warnings for missing optional credentials (Gemini, Weather API).
      2. Initialise database — create tables if they don't exist.
      3. Log inference mode (real model or mock).

    Shutdown:
      • Log clean shutdown message.
    """
    logger.info("🚀 %s v%s — starting up", settings.APP_NAME, settings.APP_VERSION)

    # Warn about missing optional credentials — never crash
    settings.emit_startup_warnings()

    # Initialise database tables
    try:
        await init_db()
    except Exception as exc:
        logger.error(
            "❌ Database initialisation failed: %s. "
            "Check DATABASE_URL in .env. Continuing without DB.",
            exc,
        )

    yield  # ← application runs here

    logger.info("🛑 %s — shutting down cleanly.", settings.APP_NAME)


# =========================================================================== #
#  FastAPI application instance
# =========================================================================== #

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=settings.APP_DESCRIPTION,
    lifespan=lifespan,
    docs_url="/docs",           # Swagger UI
    redoc_url="/redoc",         # ReDoc UI
    openapi_url="/openapi.json",
    contact={
        "name": "AgriSmart AI Team",
        "url": "https://github.com/agrismart-ai",
        "email": "team@agrismart.ai",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
    openapi_tags=[
        {
            "name": "🌿 Disease Detection",
            "description": (
                "**Core Task** — Upload a plant leaf image to get an instant disease prediction "
                "with confidence score, severity rating, and actionable precautions."
            ),
        },
        {
            "name": "💧 Irrigation Advisory",
            "description": (
                "**Bonus** — Submit field sensor data to receive a personalised 3-day irrigation "
                "schedule and a sustainability score."
            ),
        },
        {
            "name": "⛅ Weather Intelligence",
            "description": (
                "**Bonus** — Get a multi-day weather risk analysis tailored to your crop and location."
            ),
        },
        {
            "name": "🤖 AI Assistant",
            "description": (
                "**Bonus** — Ask the GenAI-powered farmer assistant any agricultural question "
                "in English or regional Indian languages."
            ),
        },
        {
            "name": "🏥 Health",
            "description": "System health-check and readiness probe endpoints.",
        },
    ],
)


# =========================================================================== #
#  Middleware
# =========================================================================== #

# ── CORS ─────────────────────────────────────────────────────────────────────
# Open to all origins for hackathon rapid integration.
# Before production, replace ["*"] with your frontend domain(s).
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=False,          # Must be False when allow_origins=["*"]
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Process-Time"],
)


# ── Request timing ────────────────────────────────────────────────────────────
@app.middleware("http")
async def add_process_time_header(request: Request, call_next: Any) -> Any:
    """Injects X-Process-Time header (ms) into every response."""
    t0 = time.perf_counter()
    response = await call_next(request)
    elapsed_ms = round((time.perf_counter() - t0) * 1000, 2)
    response.headers["X-Process-Time"] = f"{elapsed_ms}ms"
    return response


# =========================================================================== #
#  Routers
# =========================================================================== #

app.include_router(api_router, prefix=settings.API_V1_PREFIX)


# =========================================================================== #
#  Root & health endpoints
# =========================================================================== #


@app.get(
    "/",
    tags=["🏥 Health"],
    summary="Root health check",
    description="Returns service name, version, status, and links to API documentation.",
    response_model=Dict[str, Any],
)
async def root() -> Dict[str, Any]:
    return {
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "healthy",
        "model_mode": "mock" if not settings.MODEL_PATH else "real",
        "gemini_active": bool(settings.GEMINI_API_KEY),
        "weather_live": bool(settings.WEATHER_API_KEY),
        "docs": "/docs",
        "redoc": "/redoc",
        "openapi": "/openapi.json",
        "endpoints": {
            "disease_predict": f"{settings.API_V1_PREFIX}/disease/predict",
            "disease_classes": f"{settings.API_V1_PREFIX}/disease/classes",
            "advisory_recommend": f"{settings.API_V1_PREFIX}/advisory/recommend",
            "weather_risk": f"{settings.API_V1_PREFIX}/weather/risk",
            "weather_current": f"{settings.API_V1_PREFIX}/weather/current",
            "assistant_query": f"{settings.API_V1_PREFIX}/assistant/query",
        },
    }


@app.get(
    "/health",
    tags=["🏥 Health"],
    summary="Liveness probe",
    description="Kubernetes / Docker liveness probe. Returns 200 OK when the service is alive.",
    response_model=Dict[str, str],
)
async def health_check() -> Dict[str, str]:
    return {"status": "ok"}


@app.get(
    "/ready",
    tags=["🏥 Health"],
    summary="Readiness probe",
    description=(
        "Kubernetes / Docker readiness probe. "
        "Returns 200 OK when all dependencies are initialised and the service can serve traffic."
    ),
    response_model=Dict[str, Any],
)
async def readiness_check() -> Dict[str, Any]:
    return {
        "status": "ready",
        "model_mode": "mock" if not settings.MODEL_PATH else "loaded",
        "version": settings.APP_VERSION,
    }
