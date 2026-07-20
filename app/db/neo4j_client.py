"""
app/db/neo4j_client.py
─────────────────────────────────────────────────────────────────────────────
Async Neo4j driver singleton using the official neo4j Python driver (v5+).
Exposes:
  - `init_neo4j()`        — create driver + verify connectivity
  - `close_neo4j()`       — graceful shutdown
  - `get_neo4j_session()` — async context manager yielding an AsyncSession
  - `get_neo4j()`         — FastAPI dependency yielding the driver
─────────────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any

from neo4j import AsyncDriver, AsyncGraphDatabase, AsyncSession
from tenacity import (
    after_log,
    before_log,
    retry,
    stop_after_attempt,
    wait_exponential,
)

from app.config import get_settings

logger = logging.getLogger(__name__)

_driver: AsyncDriver | None = None


@retry(
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=1, min=2, max=30),
    before=before_log(logger, logging.INFO),
    after=after_log(logger, logging.WARNING),
    reraise=True,
)
async def init_neo4j() -> None:
    """
    Initialise the async Neo4j driver and verify server connectivity.
    Retries with exponential back-off (max 5 attempts).
    """
    global _driver
    settings = get_settings()

    _driver = AsyncGraphDatabase.driver(
        settings.neo4j_uri,
        auth=(settings.neo4j_user, settings.neo4j_password),
        max_connection_pool_size=settings.neo4j_max_connection_pool_size,
        connection_timeout=float(settings.neo4j_connection_timeout),
        encrypted=False,  # Set True + supply TLS certs in production
    )

    # Verify connectivity
    await _driver.verify_connectivity()

    # Bootstrap constraint / index DDL (idempotent)
    async with _driver.session() as session:
        await _bootstrap_schema(session)

    logger.info("Neo4j driver initialised and schema bootstrapped.")


async def _bootstrap_schema(session: AsyncSession) -> None:
    """
    Create uniqueness constraints and indexes.
    These are idempotent — safe to run on every startup.
    """
    ddl_statements: list[str] = [
        # Unique constraints
        "CREATE CONSTRAINT criminal_id IF NOT EXISTS "
        "FOR (c:Criminal) REQUIRE c.national_id IS UNIQUE",

        "CREATE CONSTRAINT vehicle_reg IF NOT EXISTS "
        "FOR (v:Vehicle) REQUIRE v.registration_number IS UNIQUE",

        "CREATE CONSTRAINT case_fir IF NOT EXISTS "
        "FOR (c:Case) REQUIRE c.fir_number IS UNIQUE",

        # Indexes for fast lookups
        "CREATE INDEX criminal_name IF NOT EXISTS FOR (c:Criminal) ON (c.name)",
        "CREATE INDEX location_coords IF NOT EXISTS "
        "FOR (l:Location) ON (l.latitude, l.longitude)",
        "CREATE INDEX weapon_type IF NOT EXISTS FOR (w:Weapon) ON (w.type)",
    ]
    for stmt in ddl_statements:
        try:
            await session.run(stmt)
        except Exception as exc:
            # Log but don't fail — constraint may already exist
            logger.debug("Schema DDL skipped (already exists?): %s | %s", stmt[:60], exc)


async def close_neo4j() -> None:
    """Close the driver and release all pooled connections."""
    if _driver is not None:
        await _driver.close()
        logger.info("Neo4j driver closed.")


@asynccontextmanager
async def get_neo4j_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Async context manager yielding a Neo4j AsyncSession.
    Always closes the session on exit regardless of outcome.
    """
    if _driver is None:
        raise RuntimeError("Neo4j driver not initialised. Call init_neo4j() first.")
    async with _driver.session() as session:
        yield session


async def get_neo4j() -> AsyncGenerator[AsyncDriver, None]:
    """
    FastAPI dependency — use via `Depends(get_neo4j)`.
    Yields the driver directly so callers can open their own sessions.
    """
    if _driver is None:
        raise RuntimeError("Neo4j driver not initialised.")
    yield _driver


def get_driver() -> AsyncDriver:
    """Direct synchronous accessor for use inside service classes."""
    if _driver is None:
        raise RuntimeError("Neo4j driver not initialised.")
    return _driver
