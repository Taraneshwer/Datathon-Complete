"""
ai_service/embeddings/service.py
─────────────────────────────────────────────────────────────────────────────
100% Zoho Catalyst-Native Embedding Service.
Replaces third-party embedding models (NVIDIA NIM / OpenAI / SentenceTransformers)
with native Zoho Catalyst QuickML Embedding Service.
─────────────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations
import logging
from typing import Any, List, Optional
from app.config import get_settings
from app.db.catalyst import CatalystDBClient

logger = logging.getLogger(__name__)

class EmbeddingService:
    """100% Catalyst-Native QuickML Embedding Service."""
    def __init__(self, quickml_client: Any = None) -> None:
        self.db = CatalystDBClient()
        self._quickml_client = quickml_client
        self._settings = get_settings()

    @property
    def quickml(self):
        if self._quickml_client is None:
            try:
                self._quickml_client = self.db.get_quickml_service()
            except Exception as e:
                logger.debug(f"QuickML service unavailable: {e}")
                return None
        return self._quickml_client

    @classmethod
    async def load(cls) -> EmbeddingService:
        settings = get_settings()
        logger.info("Loading Catalyst QuickML Native Embedding service ('%s')...", settings.embedding_model)
        return cls()

    async def embed(self, text: str) -> List[float]:
        text = text.strip()
        if not text:
            raise ValueError("Cannot embed an empty string.")

        try:
            # Native Catalyst QuickML embedding generation
            res = self.quickml.embed(text=text, model=self._settings.embedding_model)
            if isinstance(res, dict) and "embedding" in res:
                return res["embedding"]
            if isinstance(res, list):
                return res
            return []
        except Exception as e:
            logger.warning(f"Catalyst QuickML embedding call failed: {e}")
            return []

    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        if not texts:
            return []
        results = []
        for t in texts:
            results.append(await self.embed(t))
        return results

    @property
    def vector_size(self) -> int:
        return 1024

_embedding_service: Optional[EmbeddingService] = None

async def get_embedding_service() -> EmbeddingService:
    global _embedding_service
    if _embedding_service is None:
        _embedding_service = await EmbeddingService.load()
    return _embedding_service
