"""
app/db/postgres.py
─────────────────────────────────────────────────────────────────────────────
Async PostgreSQL engine and session factory using SQLAlchemy 2.x + asyncpg.
Exposes:
  - `engine`           — AsyncEngine singleton (created at startup)
  - `AsyncSessionLocal` — async_sessionmaker factory
  - `create_db_tables()` — idempotent table bootstrap (SQLModel.metadata)
  - `get_db()`         — FastAPI dependency yielding an AsyncSession
─────────────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlmodel import SQLModel
from tenacity import (
    after_log,
    before_log,
    retry,
    stop_after_attempt,
    wait_exponential,
)

from app.config import get_settings

logger = logging.getLogger(__name__)

# Module-level singletons — populated by init_engine()
_engine: AsyncEngine | None = None
_session_factory: async_sessionmaker[AsyncSession] | None = None


def _build_engine() -> AsyncEngine:
    settings = get_settings()
    return create_async_engine(
        settings.postgres_dsn,
        echo=settings.debug,
        pool_size=settings.postgres_pool_size,
        max_overflow=settings.postgres_max_overflow,
        pool_timeout=settings.postgres_pool_timeout,
        pool_pre_ping=True,           # Detect stale connections before use
        pool_recycle=1800,            # Recycle connections every 30 minutes
        connect_args={
            "command_timeout": 60,    # asyncpg-specific query timeout
            "server_settings": {
                "application_name": get_settings().app_name,
            },
        },
    )


@retry(
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=1, min=2, max=30),
    before=before_log(logger, logging.INFO),
    after=after_log(logger, logging.WARNING),
    reraise=True,
)
async def init_engine() -> None:
    """
    Initialise the async engine and session factory.
    Retries up to 5 times with exponential back-off — useful when the
    database container is still starting alongside the app.
    """
    global _engine, _session_factory

    _engine = _build_engine()
    _session_factory = async_sessionmaker(
        _engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )
    # Verify connectivity
    async with _engine.begin() as conn:
        await conn.run_sync(lambda c: c.execute(  # type: ignore[arg-type]
            __import__("sqlalchemy").text("SELECT 1")
        ))
    logger.info("PostgreSQL connection pool initialised successfully.")


async def create_db_tables() -> None:
    """
    Create all SQLModel-registered tables if they do not already exist.
    Safe to call on every startup (uses CREATE TABLE IF NOT EXISTS semantics).
    """
    if _engine is None:
        raise RuntimeError("Database engine not initialised. Call init_engine() first.")

    # Import all models so SQLModel.metadata is populated
    import app.models.fir  # noqa: F401

    async with _engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    logger.info("Database tables verified / created.")


async def close_engine() -> None:
    """Gracefully dispose the connection pool on shutdown."""
    if _engine is not None:
        await _engine.dispose()
        logger.info("PostgreSQL connection pool closed.")


@asynccontextmanager
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Async context manager yielding a transactional AsyncSession.
    Rolls back automatically on exception; commits on clean exit.
    """
    if _session_factory is None:
        raise RuntimeError("Session factory not initialised.")

    async with _session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency — use via `Depends(get_db)`.
    Yields a transactional AsyncSession with automatic rollback on error.
    """
    async with get_session() as session:
        yield session
