"""
app/dependencies.py
─────────────────────────────────────────────────────────────────────────────
FastAPI dependency factories.
All dependencies are declared here and used via `Depends()` in route handlers.
─────────────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends, Header, HTTPException, Request, status
from neo4j import AsyncDriver
from qdrant_client import AsyncQdrantClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import Settings, get_settings
from app.db.neo4j_client import get_neo4j
from app.db.postgres import get_db
from app.db.qdrant_client import get_qdrant
from app.intelligence.hotspot_predictor import HotspotPredictor
from app.intelligence.pattern_matcher import PatternMatcher
from app.services.embedding_service import get_embedding_service
from app.services.ingest_service import IngestService


# ── Database sessions ─────────────────────────────────────────────────────────

DBSession = Annotated[AsyncSession, Depends(get_db)]
Neo4jDriver = Annotated[AsyncDriver, Depends(get_neo4j)]
QdrantClient = Annotated[AsyncQdrantClient, Depends(get_qdrant)]
AppSettings = Annotated[Settings, Depends(get_settings)]


# ── Composite service dependencies ────────────────────────────────────────────

async def get_ingest_service(
    db: DBSession,
    neo4j: Neo4jDriver,
    qdrant: QdrantClient,
) -> IngestService:
    """Construct an IngestService with all DB connections pre-resolved."""
    return IngestService(db=db, neo4j_driver=neo4j, qdrant=qdrant)


async def get_pattern_matcher(qdrant: QdrantClient) -> PatternMatcher:
    """Construct a PatternMatcher with embedding service + Qdrant."""
    embedder = get_embedding_service()
    return PatternMatcher(qdrant_client=qdrant, embedding_service=embedder)


async def get_hotspot_predictor() -> HotspotPredictor:
    """Construct the stateless HotspotPredictor."""
    return HotspotPredictor()


# ── Request metadata helpers ──────────────────────────────────────────────────

def get_client_ip(request: Request) -> str:
    """Extract the real client IP, honouring X-Forwarded-For in production."""
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    if request.client:
        return request.client.host
    return "unknown"


def get_actor(
    x_actor_id: str | None = Header(default=None, alias="X-Actor-ID"),
) -> str:
    """
    Resolve the actor identifier from the X-Actor-ID request header.
    Falls back to 'api-anonymous' when no header is provided.
    In production, replace with a real JWT / OAuth2 bearer-token extractor.
    """
    return x_actor_id or "api-anonymous"


# ── Type aliases for Depends wrappers ─────────────────────────────────────────

IngestServiceDep = Annotated[IngestService, Depends(get_ingest_service)]
PatternMatcherDep = Annotated[PatternMatcher, Depends(get_pattern_matcher)]
HotspotPredictorDep = Annotated[HotspotPredictor, Depends(get_hotspot_predictor)]
ActorDep = Annotated[str, Depends(get_actor)]
ClientIPDep = Annotated[str, Depends(get_client_ip)]
