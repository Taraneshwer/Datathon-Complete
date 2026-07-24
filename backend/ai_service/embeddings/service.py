"""
ai_service/embeddings/service.py
"""
from __future__ import annotations

import asyncio
import logging
from typing import Any

from app.config import get_settings

logger = logging.getLogger(__name__)


class EmbeddingService:
    def __init__(self, model: Any) -> None:
        self._model = model
        self._settings = get_settings()

    @classmethod
    async def load(cls) -> EmbeddingService:
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
        text = text.strip()
        if not text:
            raise ValueError("Cannot embed an empty string.")

        vector = await asyncio.to_thread(self._encode_single, text)
        return vector.tolist()

    async def embed_batch(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []

        vectors = await asyncio.to_thread(self._encode_batch, texts)
        return [v.tolist() for v in vectors]

    def _encode_single(self, text: str) -> Any:
        return self._model.encode(
            text,
            normalize_embeddings=True,
            show_progress_bar=False,
        )

    def _encode_batch(self, texts: list[str]) -> Any:
        return self._model.encode(
            texts,
            normalize_embeddings=True,
            show_progress_bar=False,
            batch_size=32,
        )

    @property
    def vector_size(self) -> int:
        return int(self._model.get_sentence_embedding_dimension() or 384)


def _load_model(model_name: str, device: str) -> Any:
    # LAZY LOAD
    from sentence_transformers import SentenceTransformer
    return SentenceTransformer(model_name, device=device)


_embedding_service: EmbeddingService | None = None


async def get_embedding_service() -> EmbeddingService:
    global _embedding_service
    if _embedding_service is None:
        _embedding_service = await EmbeddingService.load()
    return _embedding_service
