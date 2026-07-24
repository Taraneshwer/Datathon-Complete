"""
app/dependencies.py
─────────────────────────────────────────────────────────────────────────────
FastAPI dependency factories.
All dependencies are declared here and used via `Depends()` in route handlers.
─────────────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

from typing import Annotated, Any

from fastapi import Depends, Header, Request
from neo4j import AsyncDriver
from qdrant_client import AsyncQdrantClient

from app.config import Settings, get_settings
from app.db.catalyst import get_datastore
from app.db.neo4j_client import get_neo4j
from app.db.qdrant_client import get_qdrant
from app.intelligence.hotspot_predictor import HotspotPredictor
from app.intelligence.pattern_matcher import PatternMatcher
from app.repositories import (
    AlertRepository,
    AuditRepository,
    BlockchainRepository,
    CaseRepository,
    EvidenceRepository,
    OfficerRepository,
)
from ai_service.embeddings.service import get_embedding_service
from app.services.ingest_service import IngestService

# ── Database sessions ─────────────────────────────────────────────────────────

CatalystClient = Annotated[Any, Depends(get_datastore)]

def get_officer_repo() -> OfficerRepository:
    return OfficerRepository()

def get_case_repo() -> CaseRepository:
    return CaseRepository()

def get_evidence_repo() -> EvidenceRepository:
    return EvidenceRepository()

def get_audit_repo() -> AuditRepository:
    return AuditRepository()

def get_alert_repo() -> AlertRepository:
    return AlertRepository()

def get_blockchain_repo() -> BlockchainRepository:
    return BlockchainRepository()

OfficerRepoDep = Annotated[OfficerRepository, Depends(get_officer_repo)]
CaseRepoDep = Annotated[CaseRepository, Depends(get_case_repo)]
EvidenceRepoDep = Annotated[EvidenceRepository, Depends(get_evidence_repo)]
AuditRepoDep = Annotated[AuditRepository, Depends(get_audit_repo)]
AlertRepoDep = Annotated[AlertRepository, Depends(get_alert_repo)]
BlockchainRepoDep = Annotated[BlockchainRepository, Depends(get_blockchain_repo)]
Neo4jDriver = Annotated[AsyncDriver, Depends(get_neo4j)]
QdrantClient = Annotated[AsyncQdrantClient, Depends(get_qdrant)]
AppSettings = Annotated[Settings, Depends(get_settings)]


# ── Composite service dependencies ────────────────────────────────────────────

async def get_ingest_service(
    case_repo: CaseRepoDep,
    evidence_repo: EvidenceRepoDep,
    audit_repo: AuditRepoDep,
    neo4j: Neo4jDriver,
    qdrant: QdrantClient,
) -> IngestService:
    """Construct an IngestService with all DB connections pre-resolved."""
    return IngestService(case_repo=case_repo, evidence_repo=evidence_repo, audit_repo=audit_repo, neo4j_driver=neo4j, qdrant=qdrant)


async def get_pattern_matcher(qdrant: QdrantClient) -> PatternMatcher:
    """Construct a PatternMatcher with embedding service + Qdrant."""
    embedder = await get_embedding_service()
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
