"""
app/models/fir.py
─────────────────────────────────────────────────────────────────────────────
Pydantic model definitions for the AI Crime Intelligence Platform.
Covers: Cases, Evidence, Officers (RBAC), Audit Trails, Blockchain Records.
Mapped to Zoho Catalyst Data Store ZCQL schema.
─────────────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field

# ─────────────────────────────────────────────────────────────────────────────
# Enumerations
# ─────────────────────────────────────────────────────────────────────────────

class CaseStatus(str, Enum):
    OPEN = "open"
    UNDER_INVESTIGATION = "under_investigation"
    CLOSED = "closed"
    ARCHIVED = "archived"
    COURT_SUBMITTED = "court_submitted"


class CrimeSeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class EvidenceType(str, Enum):
    PHYSICAL = "physical"
    DIGITAL = "digital"
    WITNESS = "witness"
    FORENSIC = "forensic"
    SURVEILLANCE = "surveillance"
    AUDIO = "audio"
    VIDEO = "video"
    IMAGE = "image"
    DOCUMENT = "document"
    OTHER = "other"


class EvidenceStatus(str, Enum):
    COLLECTED = "collected"
    PROCESSING = "processing"
    ANALYZED = "analyzed"
    COURT_SUBMITTED = "court_submitted"
    REJECTED = "rejected"


class OfficerRole(str, Enum):
    """RBAC roles for platform access control."""
    SUPER_ADMIN = "super_admin"          # Full platform access
    DISTRICT_ADMIN = "district_admin"    # District-level management
    INVESTIGATING_OFFICER = "io"         # Case investigation & updates
    ANALYST = "analyst"                  # Read + intelligence queries only
    FIELD_OFFICER = "field_officer"      # FIR filing only
    FORENSIC_EXPERT = "forensic_expert"  # Evidence processing access
    COURT_LIAISON = "court_liaison"      # Court submission access


class AuditAction(str, Enum):
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    QUERY = "query"
    INGEST = "ingest"
    EVIDENCE_UPLOAD = "evidence_upload"
    GRAPH_UPDATE = "graph_update"
    AI_QUERY = "ai_query"
    BLOCKCHAIN_RECORD = "blockchain_record"
    LOGIN = "login"
    LOGOUT = "logout"
    MFA_CHALLENGE = "mfa_challenge"


class AlertType(str, Enum):
    NEW_CASE = "new_case"
    PATTERN_MATCH = "pattern_match"
    HOTSPOT_DETECTED = "hotspot_detected"
    GANG_MIGRATION = "gang_migration"
    INTERSTATE_CRIME = "interstate_crime"
    CYBERCRIME_SPIKE = "cybercrime_spike"
    DRUG_ROUTE = "drug_route"
    EARLY_WARNING = "early_warning"
    BIAS_DETECTED = "bias_detected"
    BLIND_SPOT = "blind_spot"


# ─────────────────────────────────────────────────────────────────────────────
# Base mixin
# ─────────────────────────────────────────────────────────────────────────────

class TimestampMixin(BaseModel):
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


# ─────────────────────────────────────────────────────────────────────────────
# Officer — RBAC identity
# ─────────────────────────────────────────────────────────────────────────────

class Officer(TimestampMixin):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    badge_number: str
    full_name: str
    email: str
    hashed_password: str
    role: OfficerRole = Field(default=OfficerRole.FIELD_OFFICER)
    station_code: str | None = None
    district: str | None = None
    is_active: bool = True
    mfa_secret: str | None = None
    mfa_enabled: bool = False
    last_login: datetime | None = None


# ─────────────────────────────────────────────────────────────────────────────
# Case — root entity for every FIR
# ─────────────────────────────────────────────────────────────────────────────

class Case(TimestampMixin):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    fir_number: str
    title: str
    description: str
    status: CaseStatus = Field(default=CaseStatus.OPEN)
    severity: CrimeSeverity = Field(default=CrimeSeverity.MEDIUM)
    crime_type: str | None = None

    # Incident geography
    latitude: float | None = None
    longitude: float | None = None
    h3_index: str | None = None
    location_name: str | None = None
    district: str | None = None
    state: str | None = None

    # Incident temporal
    incident_datetime: datetime | None = None

    # Reporting
    reporting_officer_id: str | None = None
    station_code: str | None = None

    # AI analysis flags
    bias_detected: bool = False
    blind_spots_identified: int = 0
    risk_score: float | None = None

    # Linkage IDs for vector and blockchain stores
    qdrant_point_id: str | None = None
    blockchain_tx_id: str | None = None


# ─────────────────────────────────────────────────────────────────────────────
# EvidenceItem — AI-enriched evidence records
# ─────────────────────────────────────────────────────────────────────────────

class EvidenceItem(TimestampMixin):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    case_id: uuid.UUID
    evidence_type: EvidenceType = Field(default=EvidenceType.OTHER)
    status: EvidenceStatus = Field(default=EvidenceStatus.COLLECTED)
    description: str
    file_reference: str | None = None
    file_size_bytes: int | None = None
    mime_type: str | None = None
    original_filename: str | None = None
    object_name: str | None = None
    bucket_name: str | None = None
    sha256_hash: str | None = None
    upload_status: str | None = None
    upload_time: datetime | None = None

    # AI-extracted analysis results (stored as JSON)
    ai_analysis: dict | None = Field(
        default=None,
        description="OCR text, face detections, object detections, transcription, etc.",
    )

    # Flexible metadata
    metadata_json: dict | None = None

    # Chain-of-custody
    collected_by: str | None = None
    collected_at: datetime | None = None
    blockchain_hash: str | None = None


# ─────────────────────────────────────────────────────────────────────────────
# BlockchainRecord — Immutable cryptographic audit log
# ─────────────────────────────────────────────────────────────────────────────

class BlockchainRecord(TimestampMixin):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    case_id: uuid.UUID
    record_type: str
    entity_id: str
    sha256_hash: str
    previous_hash: str | None = None
    officer_signature: str | None = None
    fabric_tx_id: str | None = None
    payload_json: dict | None = None


# ─────────────────────────────────────────────────────────────────────────────
# SystemAlert — Early warning and AI-generated alerts
# ─────────────────────────────────────────────────────────────────────────────

class SystemAlert(TimestampMixin):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    case_id: uuid.UUID | None = None
    alert_type: AlertType
    severity: CrimeSeverity = Field(default=CrimeSeverity.MEDIUM)
    title: str
    description: str
    affected_districts: list[str] | None = None
    recommendations: list[str] | None = None
    is_acknowledged: bool = False
    acknowledged_by: str | None = None
    acknowledged_at: datetime | None = None


# ─────────────────────────────────────────────────────────────────────────────
# AuditTrail — Full forensic audit of every operation
# ─────────────────────────────────────────────────────────────────────────────

class AuditTrail(TimestampMixin):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    case_id: uuid.UUID | None = None
    officer_id: uuid.UUID | None = None
    action: AuditAction
    actor: str
    detail: str | None = None
    ip_address: str | None = None
    user_agent: str | None = None
    extra_json: dict | None = None
