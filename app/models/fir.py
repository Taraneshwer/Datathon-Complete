"""
app/models/fir.py
─────────────────────────────────────────────────────────────────────────────
SQLModel table definitions for the AI Crime Intelligence Platform.
Covers: Cases, Evidence, Officers (RBAC), Audit Trails, Blockchain Records.
─────────────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum
from typing import Optional

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlmodel import Column, Field, Relationship, SQLModel


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

class TimestampMixin(SQLModel):
    created_at: datetime = Field(
        default_factory=datetime.now,
        sa_column=Column(sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    updated_at: datetime = Field(
        default_factory=datetime.now,
        sa_column=Column(
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
        ),
    )


# ─────────────────────────────────────────────────────────────────────────────
# Officer — RBAC identity
# ─────────────────────────────────────────────────────────────────────────────

class Officer(TimestampMixin, table=True):
    __tablename__ = "officers"

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        sa_column=Column(PG_UUID(as_uuid=True), primary_key=True),
    )
    badge_number: str = Field(index=True, unique=True, max_length=32)
    full_name: str = Field(max_length=256)
    email: str = Field(unique=True, max_length=256)
    hashed_password: str = Field(max_length=256)
    role: OfficerRole = Field(default=OfficerRole.FIELD_OFFICER)
    station_code: str | None = Field(default=None, max_length=64)
    district: str | None = Field(default=None, max_length=128)
    is_active: bool = Field(default=True)
    mfa_secret: str | None = Field(default=None, max_length=64)
    mfa_enabled: bool = Field(default=False)
    last_login: datetime | None = Field(default=None)

    # Relationships
    audit_trails: list["AuditTrail"] = Relationship(back_populates="officer")


# ─────────────────────────────────────────────────────────────────────────────
# Case — root entity for every FIR
# ─────────────────────────────────────────────────────────────────────────────

class Case(TimestampMixin, table=True):
    __tablename__ = "cases"

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        sa_column=Column(PG_UUID(as_uuid=True), primary_key=True),
    )
    fir_number: str = Field(index=True, unique=True, max_length=64)
    title: str = Field(max_length=512)
    description: str = Field(sa_column=Column(sa.Text))
    status: CaseStatus = Field(default=CaseStatus.OPEN)
    severity: CrimeSeverity = Field(default=CrimeSeverity.MEDIUM)
    crime_type: str | None = Field(default=None, max_length=128)

    # Incident geography
    latitude: float | None = Field(default=None)
    longitude: float | None = Field(default=None)
    h3_index: str | None = Field(default=None, max_length=20)    # H3 cell index
    location_name: str | None = Field(default=None, max_length=256)
    district: str | None = Field(default=None, max_length=128)
    state: str | None = Field(default=None, max_length=128)

    # Incident temporal
    incident_datetime: datetime | None = Field(default=None)

    # Reporting
    reporting_officer_id: str | None = Field(default=None, max_length=128)
    station_code: str | None = Field(default=None, max_length=64)

    # AI analysis flags
    bias_detected: bool = Field(default=False)
    blind_spots_identified: int = Field(default=0)
    risk_score: float | None = Field(default=None)

    # Linkage IDs for vector and blockchain stores
    qdrant_point_id: str | None = Field(default=None, max_length=64)
    blockchain_tx_id: str | None = Field(default=None, max_length=256)

    # Relationships
    evidence_items: list["EvidenceItem"] = Relationship(back_populates="case")
    audit_trails: list["AuditTrail"] = Relationship(back_populates="case")
    blockchain_records: list["BlockchainRecord"] = Relationship(back_populates="case")
    alerts: list["SystemAlert"] = Relationship(back_populates="case")


# ─────────────────────────────────────────────────────────────────────────────
# EvidenceItem — AI-enriched evidence records
# ─────────────────────────────────────────────────────────────────────────────

class EvidenceItem(TimestampMixin, table=True):
    __tablename__ = "evidence_items"

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        sa_column=Column(PG_UUID(as_uuid=True), primary_key=True),
    )
    case_id: uuid.UUID = Field(foreign_key="cases.id", index=True)
    evidence_type: EvidenceType = Field(default=EvidenceType.OTHER)
    status: EvidenceStatus = Field(default=EvidenceStatus.COLLECTED)
    description: str = Field(sa_column=Column(sa.Text))
    file_reference: str | None = Field(default=None, max_length=512)
    file_size_bytes: int | None = Field(default=None)
    mime_type: str | None = Field(default=None, max_length=128)

    # AI-extracted analysis results (stored as JSONB)
    ai_analysis: dict | None = Field(
        default=None,
        sa_column=Column(JSONB),
        description="OCR text, face detections, object detections, transcription, etc.",
    )

    # Flexible metadata
    metadata_json: dict | None = Field(default=None, sa_column=Column(JSONB))

    # Chain-of-custody
    collected_by: str | None = Field(default=None, max_length=128)
    collected_at: datetime | None = Field(default=None)
    blockchain_hash: str | None = Field(default=None, max_length=256)

    # Relationship
    case: Optional[Case] = Relationship(back_populates="evidence_items")


# ─────────────────────────────────────────────────────────────────────────────
# BlockchainRecord — Immutable cryptographic audit log
# ─────────────────────────────────────────────────────────────────────────────

class BlockchainRecord(TimestampMixin, table=True):
    __tablename__ = "blockchain_records"

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        sa_column=Column(PG_UUID(as_uuid=True), primary_key=True),
    )
    case_id: uuid.UUID = Field(foreign_key="cases.id", index=True)
    record_type: str = Field(max_length=64)  # "evidence", "fir", "officer_action"
    entity_id: str = Field(max_length=64)    # ID of the entity being recorded
    sha256_hash: str = Field(max_length=64)  # SHA-256 of the payload
    previous_hash: str | None = Field(default=None, max_length=64)
    officer_signature: str | None = Field(default=None, max_length=512)
    fabric_tx_id: str | None = Field(default=None, max_length=256)  # Hyperledger Fabric TX
    payload_json: dict | None = Field(default=None, sa_column=Column(JSONB))

    case: Optional[Case] = Relationship(back_populates="blockchain_records")


# ─────────────────────────────────────────────────────────────────────────────
# SystemAlert — Early warning and AI-generated alerts
# ─────────────────────────────────────────────────────────────────────────────

class SystemAlert(TimestampMixin, table=True):
    __tablename__ = "system_alerts"

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        sa_column=Column(PG_UUID(as_uuid=True), primary_key=True),
    )
    case_id: uuid.UUID | None = Field(default=None, foreign_key="cases.id", index=True)
    alert_type: AlertType
    severity: CrimeSeverity = Field(default=CrimeSeverity.MEDIUM)
    title: str = Field(max_length=512)
    description: str = Field(sa_column=Column(sa.Text))
    affected_districts: list[str] | None = Field(default=None, sa_column=Column(JSONB))
    recommendations: list[str] | None = Field(default=None, sa_column=Column(JSONB))
    is_acknowledged: bool = Field(default=False)
    acknowledged_by: str | None = Field(default=None, max_length=128)
    acknowledged_at: datetime | None = Field(default=None)

    case: Optional[Case] = Relationship(back_populates="alerts")


# ─────────────────────────────────────────────────────────────────────────────
# AuditTrail — Full forensic audit of every operation
# ─────────────────────────────────────────────────────────────────────────────

class AuditTrail(TimestampMixin, table=True):
    __tablename__ = "audit_trails"

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        sa_column=Column(PG_UUID(as_uuid=True), primary_key=True),
    )
    case_id: uuid.UUID | None = Field(default=None, foreign_key="cases.id", index=True)
    officer_id: uuid.UUID | None = Field(default=None, foreign_key="officers.id", index=True)
    action: AuditAction
    actor: str = Field(max_length=128)
    detail: str | None = Field(default=None, sa_column=Column(sa.Text))
    ip_address: str | None = Field(default=None, max_length=45)
    user_agent: str | None = Field(default=None, max_length=512)
    extra_json: dict | None = Field(default=None, sa_column=Column(JSONB))

    case: Optional[Case] = Relationship(back_populates="audit_trails")
    officer: Optional[Officer] = Relationship(back_populates="audit_trails")
