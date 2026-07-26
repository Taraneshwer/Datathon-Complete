"""
app/models/schemas.py
─────────────────────────────────────────────────────────────────────────────
Pydantic v2 request / response schemas for the full platform.
─────────────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field, field_validator, model_validator

from app.models.fir import (
    AlertType,
    CaseStatus,
    CrimeSeverity,
    EvidenceType,
    OfficerRole,
)

# ─────────────────────────────────────────────────────────────────────────────
# Graph entity sub-schemas
# ─────────────────────────────────────────────────────────────────────────────

class CriminalNode(BaseModel):
    name: str = Field(..., min_length=1, max_length=256)
    alias: str | None = None
    national_id: str | None = Field(default=None, max_length=64)
    known_addresses: list[str] = Field(default_factory=list)


class VictimNode(BaseModel):
    name: str = Field(..., min_length=1, max_length=256)
    victim_id: str | None = None
    age: int | None = Field(default=None, ge=0, le=130)
    contact: str | None = Field(default=None, max_length=32)


class WitnessNode(BaseModel):
    name: str = Field(..., min_length=1, max_length=256)
    witness_id: str | None = None
    statement_summary: str | None = Field(default=None, max_length=1024)


class VehicleNode(BaseModel):
    registration_number: str = Field(..., min_length=1, max_length=32)
    make: str | None = None
    model: str | None = None
    color: str | None = None


class LocationNode(BaseModel):
    name: str = Field(..., min_length=1, max_length=256)
    latitude: float = Field(..., ge=-90.0, le=90.0)
    longitude: float = Field(..., ge=-180.0, le=180.0)
    address: str | None = None


class WeaponNode(BaseModel):
    type: str = Field(..., min_length=1, max_length=128)
    description: str | None = None
    serial_number: str | None = None


class OrganizationNode(BaseModel):
    name: str = Field(..., min_length=1, max_length=256)
    org_type: str | None = Field(default=None, max_length=128)
    registration_id: str | None = None


class FinancialAccountNode(BaseModel):
    account_number: str = Field(..., min_length=4, max_length=64)
    bank: str | None = Field(default=None, max_length=256)
    account_type: str | None = Field(default=None, max_length=64)


class GraphEntities(BaseModel):
    """All graph entities to write into Neo4j for a single FIR."""
    criminals: list[CriminalNode] = Field(default_factory=list)
    victims: list[VictimNode] = Field(default_factory=list)
    witnesses: list[WitnessNode] = Field(default_factory=list)
    vehicles: list[VehicleNode] = Field(default_factory=list)
    locations: list[LocationNode] = Field(default_factory=list)
    weapons: list[WeaponNode] = Field(default_factory=list)
    organizations: list[OrganizationNode] = Field(default_factory=list)
    financial_accounts: list[FinancialAccountNode] = Field(default_factory=list)


# ─────────────────────────────────────────────────────────────────────────────
# Evidence
# ─────────────────────────────────────────────────────────────────────────────

class EvidenceMetadata(BaseModel):
    evidence_type: EvidenceType = EvidenceType.OTHER
    description: str = Field(..., min_length=5, max_length=4096)
    file_reference: str | None = Field(default=None, max_length=512)
    collected_by: str | None = Field(default=None, max_length=128)
    collected_at: datetime | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator("description")
    @classmethod
    def description_not_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Evidence description must not be blank.")
        return v.strip()


class EvidenceAnalysisResult(BaseModel):
    """AI-extracted intelligence from an evidence file."""
    evidence_id: str
    evidence_type: EvidenceType
    ocr_text: str | None = None
    detected_faces: int = 0
    detected_objects: list[str] = Field(default_factory=list)
    transcription: str | None = None
    summary: str | None = None
    confidence: float = 0.0
    processing_time_ms: float = 0.0


# ─────────────────────────────────────────────────────────────────────────────
# FIR Ingestion
# ─────────────────────────────────────────────────────────────────────────────

class FIRIngestRequest(BaseModel):
    fir_number: str = Field(
        ..., min_length=3, max_length=64,
        pattern=r"^[A-Z0-9\-/]+$",
        description="Unique FIR reference number (uppercase alphanumeric).",
    )
    title: str = Field(..., min_length=5, max_length=512)
    description: str = Field(..., min_length=20, max_length=16384)
    status: CaseStatus = CaseStatus.OPEN
    severity: CrimeSeverity = CrimeSeverity.MEDIUM
    crime_type: str | None = Field(default=None, max_length=128)

    # Geography
    latitude: float | None = Field(default=None, ge=-90.0, le=90.0)
    longitude: float | None = Field(default=None, ge=-180.0, le=180.0)
    location_name: str | None = Field(default=None, max_length=256)
    district: str | None = Field(default=None, max_length=128)
    state: str | None = Field(default=None, max_length=128)

    # Temporal
    incident_datetime: datetime | None = None

    # Reporting
    reporting_officer_id: str | None = Field(default=None, max_length=128)
    station_code: str | None = Field(default=None, max_length=64)

    # Payloads
    evidence_items: list[EvidenceMetadata] = Field(default_factory=list)
    graph_entities: GraphEntities = Field(default_factory=GraphEntities)

    @model_validator(mode="after")
    def validate_location_pair(self) -> FIRIngestRequest:
        if (self.latitude is None) != (self.longitude is None):
            raise ValueError("Both latitude and longitude must be provided together.")
        return self

    @field_validator("description")
    @classmethod
    def description_not_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("FIR description must not be blank.")
        return v.strip()


class IngestResponse(BaseModel):
    case_id: uuid.UUID
    fir_number: str
    qdrant_point_id: str
    neo4j_nodes_created: int
    evidence_items_stored: int
    trust_score: float
    blockchain_hash: str | None = None
    message: str = "FIR ingested successfully."


# ─────────────────────────────────────────────────────────────────────────────
# Pattern Matching
# ─────────────────────────────────────────────────────────────────────────────

class PatternMatch(BaseModel):
    case_id: str
    fir_number: str
    similarity_score: float
    description_snippet: str


class PatternMatchResponse(BaseModel):
    query_text: str
    matches: list[PatternMatch]
    total_found: int


# ─────────────────────────────────────────────────────────────────────────────
# Hotspot Prediction
# ─────────────────────────────────────────────────────────────────────────────

class CoordinatePoint(BaseModel):
    latitude: float = Field(..., ge=-90.0, le=90.0)
    longitude: float = Field(..., ge=-180.0, le=180.0)
    label: str | None = None


class HotspotRequest(BaseModel):
    coordinates: list[CoordinatePoint] = Field(..., min_length=3)
    algorithm: str = Field(default="dbscan", pattern="^(dbscan|hdbscan)$")


class ClusterResult(BaseModel):
    cluster_id: int
    centroid_latitude: float
    centroid_longitude: float
    h3_index: str | None = None
    point_count: int
    point_indices: list[int]
    risk_level: str = "medium"


class HotspotResponse(BaseModel):
    total_points: int
    noise_points: int
    algorithm_used: str
    clusters: list[ClusterResult]
    patrol_recommendations: list[str] = Field(default_factory=list)


# ─────────────────────────────────────────────────────────────────────────────
# Crime Replay
# ─────────────────────────────────────────────────────────────────────────────

class TimelineEvent(BaseModel):
    event_id: str
    event_type: str
    timestamp: datetime
    actor: str | None = None
    description: str
    location: str | None = None
    evidence_ids: list[str] = Field(default_factory=list)


class CrimeReplayResponse(BaseModel):
    case_id: str
    fir_number: str
    total_events: int
    timeline: list[TimelineEvent]


# ─────────────────────────────────────────────────────────────────────────────
# Investigation Bias Detection
# ─────────────────────────────────────────────────────────────────────────────

class BiasIndicator(BaseModel):
    bias_type: str
    severity: str
    description: str
    recommendation: str


class BiasDetectionResponse(BaseModel):
    case_id: str
    fir_number: str
    overall_bias_score: float
    bias_detected: bool
    indicators: list[BiasIndicator]
    missing_leads: list[str] = Field(default_factory=list)


# ─────────────────────────────────────────────────────────────────────────────
# Crime Blind-Spot Discovery
# ─────────────────────────────────────────────────────────────────────────────

class BlindSpotRequest(BaseModel):
    district: str
    latitude_min: float
    latitude_max: float
    longitude_min: float
    longitude_max: float


class BlindSpotResult(BaseModel):
    h3_index: str
    centroid_latitude: float
    centroid_longitude: float
    crime_density: float
    cctv_coverage: float
    patrol_density: float
    blind_spot_score: float
    recommendations: list[str]


class BlindSpotResponse(BaseModel):
    district: str
    total_cells_analyzed: int
    blind_spots_found: int
    results: list[BlindSpotResult]


# ─────────────────────────────────────────────────────────────────────────────
# Crime Intervention Recommendations
# ─────────────────────────────────────────────────────────────────────────────

class InterventionRecommendation(BaseModel):
    priority: int
    action: str
    rationale: str
    resources_required: list[str] = Field(default_factory=list)
    estimated_impact: str


class InterventionResponse(BaseModel):
    case_id: str | None = None
    district: str | None = None
    risk_score: float
    recommendations: list[InterventionRecommendation]
    generated_at: datetime = Field(default_factory=datetime.now)


# ─────────────────────────────────────────────────────────────────────────────
# Early Warning System
# ─────────────────────────────────────────────────────────────────────────────

class EarlyWarningAlert(BaseModel):
    alert_id: str
    alert_type: AlertType
    severity: CrimeSeverity
    title: str
    description: str
    affected_districts: list[str]
    confidence_score: float
    recommendations: list[str]
    generated_at: datetime = Field(default_factory=datetime.now)


class EarlyWarningResponse(BaseModel):
    monitoring_period_days: int
    alerts_generated: int
    alerts: list[EarlyWarningAlert]


# ─────────────────────────────────────────────────────────────────────────────
# AI Assistant
# ─────────────────────────────────────────────────────────────────────────────

class ChatRequest(BaseModel):
    query: str = Field(..., min_length=3, max_length=4096)
    case_context_id: uuid.UUID | None = None
    top_k: int = Field(default=5, ge=1, le=20)

    @field_validator("query")
    @classmethod
    def query_not_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Query must not be blank.")
        return v.strip()


class SourceDocument(BaseModel):
    case_id: str
    fir_number: str
    similarity_score: float
    excerpt: str


class ChatResponse(BaseModel):
    query: str
    answer: str
    sources: list[SourceDocument]
    graph_paths: list[str]
    processing_time_ms: float


# ─────────────────────────────────────────────────────────────────────────────
# Authentication
# ─────────────────────────────────────────────────────────────────────────────

class LoginRequest(BaseModel):
    badge_number: str = Field(..., min_length=3, max_length=32)
    password: str = Field(..., min_length=8)
    mfa_code: str | None = Field(default=None, min_length=6, max_length=8)


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in_minutes: int
    officer_id: str
    role: OfficerRole


class OfficerCreate(BaseModel):
    badge_number: str = Field(..., min_length=3, max_length=32)
    full_name: str = Field(..., min_length=2, max_length=256)
    email: str = Field(..., max_length=256)
    password: str = Field(..., min_length=8, max_length=128)
    role: OfficerRole = OfficerRole.FIELD_OFFICER
    station_code: str | None = None
    district: str | None = None


# ─────────────────────────────────────────────────────────────────────────────
# WebSocket Alert
# ─────────────────────────────────────────────────────────────────────────────

class AlertPayload(BaseModel):
    event_type: str = Field(..., max_length=64)
    case_id: str | None = None
    fir_number: str | None = None
    severity: CrimeSeverity | None = None
    message: str = Field(..., max_length=2048)
    timestamp: datetime = Field(default_factory=datetime.now)


# ─────────────────────────────────────────────────────────────────────────────
# Generic Error
# ─────────────────────────────────────────────────────────────────────────────

class ErrorDetail(BaseModel):
    field: str | None = None
    message: str


class ErrorResponse(BaseModel):
    status_code: int
    error: str
    details: list[ErrorDetail] = Field(default_factory=list)
