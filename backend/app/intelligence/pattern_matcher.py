"""
app/intelligence/pattern_matcher.py
─────────────────────────────────────────────────────────────────────────────
Asynchronous pattern matching engine.
Queries Qdrant for cosine-similar crime records against a given text input,
returning ranked PatternMatch results with similarity scores.

Architecture:
  1. Text → embedding (offloaded to thread pool via EmbeddingService)
  2. Embedding → Qdrant search (async native)
  3. Qdrant hits → PatternMatch schema list
─────────────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import logging
from typing import Any

from qdrant_client import AsyncQdrantClient
from qdrant_client.models import FieldCondition, Filter, MatchValue, ScoredPoint

from app.config import get_settings
from app.models.schemas import PatternMatch, PatternMatchResponse
from app.services.embedding_service import EmbeddingService

logger = logging.getLogger(__name__)


class PatternMatcher:
    """
    Async pattern matching engine backed by Qdrant vector similarity search.

    Usage:
        matcher = PatternMatcher(qdrant_client, embedding_service)
        result = await matcher.find_similar(text="armed robbery near central market")
    """

    def __init__(
        self,
        qdrant_client: AsyncQdrantClient,
        embedding_service: EmbeddingService,
    ) -> None:
        self._qdrant = qdrant_client
        self._embedder = embedding_service
        self._settings = get_settings()

    async def find_similar(
        self,
        text: str,
        top_k: int | None = None,
        score_threshold: float | None = None,
        filter_conditions: dict[str, Any] | None = None,
    ) -> PatternMatchResponse:
        """
        Embed `text` and query Qdrant for the most similar crime records.

        Args:
            text:              Query narrative to match against.
            top_k:             Number of results (defaults to settings value).
            score_threshold:   Minimum cosine similarity (defaults to settings value).
            filter_conditions: Optional Qdrant payload filters as
                               {field: value} dict (e.g. {"severity": "high"}).

        Returns:
            PatternMatchResponse with ranked matches and metadata.
        """
        settings = self._settings
        k = top_k or settings.pattern_match_top_k
        threshold = score_threshold or settings.pattern_match_score_threshold

        logger.debug("PatternMatcher: encoding query text (len=%d)", len(text))
        query_vector = await self._embedder.embed(text)

        # Build optional payload filter
        qdrant_filter: Filter | None = None
        if filter_conditions:
            qdrant_filter = Filter(
                must=[
                    FieldCondition(key=k, match=MatchValue(value=v))
                    for k, v in filter_conditions.items()
                ]
            )

        logger.debug(
            "PatternMatcher: querying Qdrant | collection=%s top_k=%d threshold=%.2f",
            settings.qdrant_collection,
            k,
            threshold,
        )

        try:
            hits: list[ScoredPoint] = await self._qdrant.search(
                collection_name=settings.qdrant_collection,
                query_vector=query_vector,
                limit=k,
                score_threshold=threshold,
                query_filter=qdrant_filter,
                with_payload=True,
                with_vectors=False,
            )
        except Exception as exc:
            logger.error("PatternMatcher: Qdrant search failed — %s", exc, exc_info=True)
            raise RuntimeError(f"Vector search failed: {exc}") from exc

        matches = [self._hit_to_match(hit) for hit in hits]
        logger.info(
            "PatternMatcher: found %d matches (threshold=%.2f)", len(matches), threshold
        )

        return PatternMatchResponse(
            query_text=text[:256],  # Truncate for response payload safety
            matches=matches,
            total_found=len(matches),
        )

    @staticmethod
    def _hit_to_match(hit: ScoredPoint) -> PatternMatch:
        """Convert a Qdrant ScoredPoint to a PatternMatch schema instance."""
        payload = hit.payload or {}
        description = payload.get("description", "")
        return PatternMatch(
            case_id=str(payload.get("case_id", hit.id)),
            fir_number=str(payload.get("fir_number", "UNKNOWN")),
            similarity_score=round(float(hit.score), 4),
            description_snippet=description[:200] if description else "",
        )

    async def find_similar_to_case(
        self, case_id: str, top_k: int | None = None
    ) -> PatternMatchResponse:
        """
        Find patterns similar to an existing case by fetching its stored vector.
        Useful for "find cases like this one" queries.
        """
        settings = self._settings
        k = top_k or settings.pattern_match_top_k

        try:
            results = await self._qdrant.recommend(
                collection_name=settings.qdrant_collection,
                positive=[case_id],
                limit=k,
                score_threshold=settings.pattern_match_score_threshold,
                with_payload=True,
                with_vectors=False,
            )
        except Exception as exc:
            logger.error("PatternMatcher: Qdrant recommend failed — %s", exc, exc_info=True)
            raise RuntimeError(f"Vector recommend failed: {exc}") from exc

        matches = [self._hit_to_match(hit) for hit in results]
        return PatternMatchResponse(
            query_text=f"[Case similarity for ID: {case_id}]",
            matches=matches,
            total_found=len(matches),
        )
