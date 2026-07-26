"""
ai_service/embeddings/service.py
"""
from __future__ import annotations

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
            "Loading NVIDIA embedding model '%s'...",
            settings.embedding_model,
        )
        from langchain_nvidia_ai_endpoints import NVIDIAEmbeddings
        model = NVIDIAEmbeddings(
            model=settings.embedding_model,
            api_key=settings.nvidia_api_key,
            truncate="END"
        )
        logger.info("Embedding model loaded successfully.")
        return cls(model)

    async def embed(self, text: str) -> list[float]:
        text = text.strip()
        if not text:
            raise ValueError("Cannot embed an empty string.")

        vector = await self._model.aembed_query(text)
        return vector

    async def embed_batch(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []

        vectors = await self._model.aembed_documents(texts)
        return vectors

    @property
    def vector_size(self) -> int:
        return self._settings.qdrant_vector_size


_embedding_service: EmbeddingService | None = None


async def get_embedding_service() -> EmbeddingService:
    global _embedding_service
    if _embedding_service is None:
        _embedding_service = await EmbeddingService.load()
    return _embedding_service
