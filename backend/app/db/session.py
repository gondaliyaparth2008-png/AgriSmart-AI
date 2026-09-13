"""
app/db/session.py
-----------------
Async SQLAlchemy engine, session factory, and FastAPI dependency.

Supports:
  • SQLite   via aiosqlite   (local development — zero setup)
  • PostgreSQL via asyncpg   (production — set DATABASE_URL in .env)

Usage in endpoints
------------------
    from app.db.session import get_db
    from sqlalchemy.ext.asyncio import AsyncSession

    @router.post("/something")
    async def my_endpoint(db: AsyncSession = Depends(get_db)):
        ...

Database initialisation
-----------------------
Call `init_db()` once at application startup (see app/main.py lifespan)
to create all tables defined in ORM models if they don't exist yet.
"""

from __future__ import annotations

import logging
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import settings

logger = logging.getLogger(__name__)

# ─── Engine ──────────────────────────────────────────────────────────────────
# connect_args is only needed for SQLite to allow the same connection to be
# used across threads (FastAPI uses a thread pool for sync operations).
_connect_args: dict = {}
if settings.DATABASE_URL.startswith("sqlite"):
    _connect_args = {"check_same_thread": False}

engine: AsyncEngine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,       # Log all SQL statements in debug mode
    future=True,               # SQLAlchemy 2.x "future" mode
    connect_args=_connect_args,
)

# ─── Session factory ──────────────────────────────────────────────────────────
AsyncSessionLocal: async_sessionmaker[AsyncSession] = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,    # Avoids lazy-load errors after commit
    autocommit=False,
    autoflush=False,
)


# ─── FastAPI dependency ───────────────────────────────────────────────────────
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Yield an AsyncSession and guarantee it is closed after the request,
    regardless of whether an exception was raised.

    Inject with:  db: AsyncSession = Depends(get_db)
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


# ─── Table creation ───────────────────────────────────────────────────────────
async def init_db() -> None:
    """
    Create all tables defined in ORM models if they don't already exist.

    This is a simple "create if missing" strategy suitable for development
    and hackathons. For production, use Alembic migrations instead.

    Called from app/main.py lifespan hook on startup.
    """
    # Import models here so Base.metadata is populated before create_all()
    from app.db.base import Base
    from app.models import advisory_log, prediction_log  # noqa: F401

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    logger.info("✅ Database tables verified / created at: %s", settings.DATABASE_URL)
