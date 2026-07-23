"""
app/db/qdrant_client.py
─────────────────────────────────────────────────────────────────────────────
Async Qdrant client singleton with collection bootstrapping.
Exposes:
  - `init_qdrant()`    — create client + ensure collection exists
  - `close_qdrant()`   — graceful shutdown
  - `get_qdrant()`     — FastAPI dependency / direct accessor
─────────────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import logging
from collections.abc import AsyncGenerator

from qdrant_client import AsyncQdrantClient
from qdrant_client.http.exceptions import UnexpectedResponse
from qdrant_client.models import (
    Distance,
    HnswConfigDiff,
    OptimizersConfigDiff,
    VectorParams,
)
from tenacity import (
    after_log,
    before_log,
    retry,
    stop_after_attempt,
    wait_exponential,
)

from app.config import get_settings

logger = logging.getLogger(__name__)

_client: AsyncQdrantClient | None = None


@retry(
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=1, min=2, max=30),
    before=before_log(logger, logging.INFO),
    after=after_log(logger, logging.WARNING),
    reraise=True,
)
async def init_qdrant() -> None:
    """
    Initialise the async Qdrant client and ensure the crime vectors
    collection exists with proper HNSW / optimizer settings.
    """
    global _client
    settings = get_settings()

    _client = AsyncQdrantClient(
        host=settings.qdrant_host,
        port=settings.qdrant_port,
        api_key=settings.qdrant_api_key or None,
        timeout=30,
        prefer_grpc=False,  # Switch to True when running with gRPC port
    )

    await _ensure_collection(settings.qdrant_collection, settings.qdrant_vector_size)
    logger.info(
        "Qdrant client initialised. Collection '%s' ready.", settings.qdrant_collection
    )


async def _ensure_collection(collection_name: str, vector_size: int) -> None:
    """
    Create the Qdrant collection if it does not already exist.
    Uses cosine distance — ideal for sentence-transformer embeddings.
    """
    if _client is None:
        raise RuntimeError("Qdrant client not initialised.")

    existing = {c.name for c in await _client.get_collections()}

    if collection_name in existing:
        logger.debug("Qdrant collection '%s' already exists — skipping.", collection_name)
        return

    await _client.create_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(
            size=vector_size,
            distance=Distance.COSINE,
            on_disk=False,
        ),
        hnsw_config=HnswConfigDiff(
            m=16,               # Number of edges per node in HNSW graph
            ef_construct=100,   # Larger = better recall during indexing
            full_scan_threshold=10000,
        ),
        optimizers_config=OptimizersConfigDiff(
            indexing_threshold=20000,       # Vectors before switching to HNSW
            memmap_threshold=50000,
        ),
    )
    logger.info("Qdrant collection '%s' created (size=%d).", collection_name, vector_size)


async def close_qdrant() -> None:
    """Close the Qdrant HTTP connection pool."""
    if _client is not None:
        await _client.close()
        logger.info("Qdrant client closed.")


def get_client() -> AsyncQdrantClient:
    """Direct synchronous accessor for service classes."""
    if _client is None:
        raise RuntimeError("Qdrant client not initialised.")
    return _client


async def get_qdrant() -> AsyncGenerator[AsyncQdrantClient, None]:
    """
    FastAPI dependency — use via `Depends(get_qdrant)`.
    Yields the shared async client instance.
    """
    if _client is None:
        raise RuntimeError("Qdrant client not initialised.")
    yield _client
