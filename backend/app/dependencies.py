"""
app/dependencies.py
─────────────────────────────────────────────────────────────────────────────
100% Zoho Catalyst-Native FastAPI Dependency Injection Factories.
Replaces Neo4j and Qdrant dependencies with unified CatalystDBClient.
─────────────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations
from typing import Annotated, Any
from fastapi import Depends, Header, Request
from app.config import Settings, get_settings
from app.db.catalyst import get_datastore, CatalystDBClient, get_db_client
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
from app.services.storage_service import StorageService

# ── Database sessions ─────────────────────────────────────────────────────────

CatalystClient = Annotated[Any, Depends(get_datastore)]
CatalystDBDep = Annotated[CatalystDBClient, Depends(get_db_client)]

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
AppSettings = Annotated[Settings, Depends(get_settings)]

# ── Composite service dependencies ────────────────────────────────────────────

async def get_ingest_service(
    case_repo: CaseRepoDep,
    evidence_repo: EvidenceRepoDep,
    audit_repo: AuditRepoDep,
    db_client: CatalystDBDep,
) -> IngestService:
    """Construct a 100% Catalyst-Native IngestService."""
    return IngestService(case_repo=case_repo, evidence_repo=evidence_repo, audit_repo=audit_repo, db_client=db_client)

async def get_storage_service(db_client: CatalystDBDep) -> StorageService:
    """Construct a Catalyst Stratus StorageService."""
    return StorageService(db_client=db_client)

async def get_pattern_matcher(db_client: CatalystDBDep) -> PatternMatcher:
    """Construct a PatternMatcher backed by Catalyst QuickML Knowledge Base."""
    embedder = await get_embedding_service()
    return PatternMatcher(db_client=db_client, embedding_service=embedder)

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
    """Resolve the actor identifier from the X-Actor-ID request header."""
    return x_actor_id or "api-anonymous"

# ── Type aliases for Depends wrappers ─────────────────────────────────────────

IngestServiceDep = Annotated[IngestService, Depends(get_ingest_service)]
StorageServiceDep = Annotated[StorageService, Depends(get_storage_service)]
PatternMatcherDep = Annotated[PatternMatcher, Depends(get_pattern_matcher)]
HotspotPredictorDep = Annotated[HotspotPredictor, Depends(get_hotspot_predictor)]
ActorDep = Annotated[str, Depends(get_actor)]
ClientIPDep = Annotated[str, Depends(get_client_ip)]
