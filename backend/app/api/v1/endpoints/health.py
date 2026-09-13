"""
app/api/v1/endpoints/health.py
--------------------------------
Safe database connection-test endpoint for AgriSmart AI.

Endpoints
---------
GET /api/v1/health/db
    Runs a lightweight `SELECT 1` against the configured database and
    returns a JSON status object. Credentials and connection strings are
    NEVER included in the response.

GET /api/v1/health/supabase
    Reports whether SUPABASE_URL and SUPABASE_PUBLISHABLE_KEY are configured
    (without revealing their values).
"""

from __future__ import annotations

import logging
from typing import Any, Dict

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.session import get_db

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/health", tags=["🏥 Health"])


# ─── Database connectivity probe ─────────────────────────────────────────────


@router.get(
    "/db",
    summary="Database connection test",
    description=(
        "Runs a `SELECT 1` against the configured database to verify connectivity. "
        "**Credentials are never included in the response.** "
        "Returns `status: ok` with the database driver type on success, "
        "or `status: error` with a safe message on failure."
    ),
    response_model=Dict[str, Any],
)
async def db_health(db: AsyncSession = Depends(get_db)) -> Dict[str, Any]:
    """
    Safe database liveness check.

    - Executes `SELECT 1` to confirm the connection is alive.
    - Reports which driver/backend is in use (sqlite / postgresql).
    - Never exposes the connection string, password, or host details.
    """
    # Detect driver from URL prefix (safe — no credentials in prefix)
    db_url = settings.DATABASE_URL
    if db_url.startswith("sqlite"):
        driver = "sqlite+aiosqlite"
        backend = "SQLite (local development)"
    elif "postgresql" in db_url or "postgres" in db_url:
        driver = "postgresql+asyncpg"
        backend = "PostgreSQL (Supabase)"
    else:
        driver = "unknown"
        backend = "unknown"

    try:
        await db.execute(text("SELECT 1"))
        logger.info("✅ Database health check passed (%s)", driver)
        return {
            "status": "ok",
            "message": "Database connection is healthy.",
            "backend": backend,
            "driver": driver,
            # NOTE: host, port, password, and full URL are intentionally omitted
        }
    except Exception as exc:
        logger.error("❌ Database health check failed: %s", exc)
        return {
            "status": "error",
            "message": (
                "Could not connect to the database. "
                "Check DATABASE_URL in your .env file and ensure the database is reachable."
            ),
            "backend": backend,
            "driver": driver,
            # Safe — no credentials or stack trace exposed to the client
        }


# ─── Supabase configuration probe ────────────────────────────────────────────


@router.get(
    "/supabase",
    summary="Supabase configuration check",
    description=(
        "Reports whether SUPABASE_URL and SUPABASE_PUBLISHABLE_KEY are configured. "
        "**Actual key values are never returned.**"
    ),
    response_model=Dict[str, Any],
)
async def supabase_health() -> Dict[str, Any]:
    """
    Reports Supabase credential presence without exposing their values.

    Use this to verify that your .env variables have been loaded correctly
    before testing authenticated Supabase features.
    """
    url_configured = bool(settings.SUPABASE_URL)
    key_configured = bool(settings.SUPABASE_PUBLISHABLE_KEY)
    db_is_postgres = not settings.DATABASE_URL.startswith("sqlite")

    overall = url_configured and key_configured and db_is_postgres

    return {
        "status": "ok" if overall else "incomplete",
        "supabase_url_set": url_configured,
        "supabase_publishable_key_set": key_configured,
        "database_backend": (
            "PostgreSQL (Supabase)" if db_is_postgres else "SQLite (local dev — set DATABASE_URL in .env)"
        ),
        "ready": overall,
        "hint": (
            "All Supabase credentials are configured. ✅"
            if overall
            else (
                "One or more Supabase credentials are missing. "
                "Open backend/.env and fill in SUPABASE_URL, SUPABASE_PUBLISHABLE_KEY, and DATABASE_URL."
            )
        ),
    }
