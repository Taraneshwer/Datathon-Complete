"""
app/services/embedding_service.py
─────────────────────────────────────────────────────────────────────────────
Async wrapper around sentence-transformers.

sentence-transformers encoding is CPU-bound (synchronous, GIL-holding),
so it is always offloaded to asyncio.to_thread() to avoid blocking the
FastAPI event loop.

The model is loaded once at startup via `EmbeddingService.load()` and the
singleton is shared across all requests.
─────────────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import asyncio
import logging

import numpy as np
from numpy.typing import NDArray
from sentence_transformers import SentenceTransformer

from app.config import get_settings

logger = logging.getLogger(__name__)


class EmbeddingService:
    """
    Async sentence-embedding service.

    Usage:
        service = await EmbeddingService.load()
        vector = await service.embed("crime text here")
    """

    def __init__(self, model: SentenceTransformer) -> None:
        self._model = model
        self._settings = get_settings()

    @classmethod
    async def load(cls) -> EmbeddingService:
        """
        Asynchronously load the sentence-transformers model.
        Loading is CPU-bound; offloaded to thread pool.
        """
        settings = get_settings()
        logger.info(
            "Loading embedding model '%s' on device='%s'...",
            settings.embedding_model,
            settings.embedding_device,
        )
        model = await asyncio.to_thread(
            _load_model,
            settings.embedding_model,
            settings.embedding_device,
        )
        logger.info("Embedding model loaded successfully.")
        return cls(model)

    async def embed(self, text: str) -> list[float]:
        """
        Encode a single text string and return the embedding as a float list.
        Always normalises the output vector (unit norm for cosine similarity).
        """
        text = text.strip()
        if not text:
            raise ValueError("Cannot embed an empty string.")

        vector: NDArray[np.float32] = await asyncio.to_thread(
            self._encode_single, text
        )
        return vector.tolist()

    async def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """
        Encode a batch of texts concurrently.
        Sentence-transformers batching is more efficient than N separate calls.
        """
        if not texts:
            return []

        vectors: NDArray[np.float32] = await asyncio.to_thread(
            self._encode_batch, texts
        )
        return [v.tolist() for v in vectors]

    def _encode_single(self, text: str) -> NDArray[np.float32]:
        return self._model.encode(
            text,
            normalize_embeddings=True,
            show_progress_bar=False,
        )

    def _encode_batch(self, texts: list[str]) -> NDArray[np.float32]:
        return self._model.encode(
            texts,
            normalize_embeddings=True,
            show_progress_bar=False,
            batch_size=32,
        )

    @property
    def vector_size(self) -> int:
        """Return the embedding dimension for the loaded model."""
        return int(self._model.get_sentence_embedding_dimension() or 384)


def _load_model(model_name: str, device: str) -> SentenceTransformer:
    """Synchronous model loader (called inside thread pool)."""
    return SentenceTransformer(model_name, device=device)


# Module-level singleton — populated by init_embedding_service()
_embedding_service: EmbeddingService | None = None


async def init_embedding_service() -> None:
    """Called during app startup lifespan to warm up the model."""
    global _embedding_service
    _embedding_service = await EmbeddingService.load()


def get_embedding_service() -> EmbeddingService:
    """Direct accessor for service classes."""
    if _embedding_service is None:
        raise RuntimeError(
            "EmbeddingService not initialised. "
            "Ensure init_embedding_service() is called at startup."
        )
    return _embedding_service
