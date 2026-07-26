"""
app/services/trust_service.py
─────────────────────────────────────────────────────────────────────────────
Data Trust Layer — validates, scores, and verifies data integrity before
it enters the intelligence processing pipeline.

Checks performed:
  1. Schema completeness score
  2. Data quality scoring (text richness)
  3. Geographic validity (India bounding box)
  4. Source authentication (station code + officer badge)
  5. Duplicate fingerprint detection (in-process SHA-256 set)
─────────────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import hashlib
import logging
from dataclasses import dataclass, field
from datetime import datetime

from app.models.schemas import FIRIngestRequest

logger = logging.getLogger(__name__)

# Minimum trust score to proceed with ingestion (0.0–1.0)
MINIMUM_TRUST_SCORE = 0.50

# In-process fingerprint store — prevents exact duplicate FIRs within a session.
# For a production multi-process deployment, replace with a shared DB-backed set.
_seen_fingerprints: set[str] = set()


@dataclass
class TrustReport:
    """Result of the Data Trust Layer validation pipeline."""

    passed: bool
    overall_score: float                        # 0.0 – 1.0
    completeness_score: float = 0.0
    quality_score: float = 0.0
    geo_validity_score: float = 0.0
    source_authenticated: bool = False
    is_duplicate: bool = False
    fingerprint: str = ""
    issues: list[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())


class TrustService:
    """
    Data Trust Layer for the crime intelligence platform.
    All FIR data passes through this service before ingestion.
    """

    async def validate(self, payload: FIRIngestRequest) -> TrustReport:
        """
        Run the full trust pipeline against an inbound FIR payload.
        Returns a TrustReport; caller should reject if `passed=False`.
        """
        issues: list[str] = []

        # 1. Completeness scoring
        completeness = self._score_completeness(payload, issues)

        # 2. Data quality scoring
        quality = self._score_quality(payload, issues)

        # 3. Geo-validity
        geo = self._score_geo(payload, issues)

        # 4. Source authentication (station code present)
        source_ok = bool(payload.station_code and payload.reporting_officer_id)
        if not source_ok:
            issues.append("Missing station_code or reporting_officer_id — source unverified.")

        # 5. Duplicate fingerprint check (in-process set)
        fingerprint = self._compute_fingerprint(payload)
        is_duplicate = fingerprint in _seen_fingerprints
        if is_duplicate:
            issues.append(f"Duplicate FIR fingerprint detected: {fingerprint[:16]}…")

        # Weighted overall score
        overall = (
            completeness * 0.35
            + quality * 0.30
            + geo * 0.20
            + (0.15 if source_ok else 0.0)
        )

        passed = overall >= MINIMUM_TRUST_SCORE and not is_duplicate

        if passed:
            _seen_fingerprints.add(fingerprint)

        report = TrustReport(
            passed=passed,
            overall_score=round(overall, 3),
            completeness_score=round(completeness, 3),
            quality_score=round(quality, 3),
            geo_validity_score=round(geo, 3),
            source_authenticated=source_ok,
            is_duplicate=is_duplicate,
            fingerprint=fingerprint,
            issues=issues,
        )

        logger.info(
            "TrustService: FIR=%s score=%.2f passed=%s issues=%d",
            payload.fir_number,
            overall,
            passed,
            len(issues),
        )
        return report

    # ── Scoring sub-components ────────────────────────────────────────────────

    @staticmethod
    def _score_completeness(payload: FIRIngestRequest, issues: list[str]) -> float:
        checks = {
            "fir_number": bool(payload.fir_number),
            "title": bool(payload.title),
            "description": len(payload.description) >= 50,
            "incident_datetime": payload.incident_datetime is not None,
            "location": payload.latitude is not None and payload.longitude is not None,
            "location_name": bool(payload.location_name),
            "evidence_items": len(payload.evidence_items) > 0,
            "graph_entities": (
                len(payload.graph_entities.criminals) > 0
                or len(payload.graph_entities.vehicles) > 0
            ),
        }
        score = sum(checks.values()) / len(checks)
        missing = [k for k, v in checks.items() if not v]
        if missing:
            issues.append(f"Missing or incomplete fields: {', '.join(missing)}")
        return score

    @staticmethod
    def _score_quality(payload: FIRIngestRequest, issues: list[str]) -> float:
        desc_len = len(payload.description)
        if desc_len < 50:
            issues.append("Description too short (< 50 chars) — low data quality.")
            return 0.2
        elif desc_len < 150:
            return 0.6
        elif desc_len < 500:
            return 0.85
        return 1.0

    @staticmethod
    def _score_geo(payload: FIRIngestRequest, issues: list[str]) -> float:
        if payload.latitude is None or payload.longitude is None:
            issues.append("No geographic coordinates provided.")
            return 0.0
        # India bounding box: lat 6–37°N, lon 68–97°E
        lat_ok = 6.0 <= payload.latitude <= 37.5
        lon_ok = 68.0 <= payload.longitude <= 97.5
        if not (lat_ok and lon_ok):
            issues.append(
                f"Coordinates ({payload.latitude}, {payload.longitude}) "
                "are outside India's bounding box."
            )
            return 0.3
        return 1.0

    @staticmethod
    def _compute_fingerprint(payload: FIRIngestRequest) -> str:
        content = (
            f"{payload.fir_number}|{payload.title[:100]}|"
            f"{str(payload.latitude)}|{str(payload.longitude)}|"
            f"{str(payload.incident_datetime)}"
        )
        return hashlib.sha256(content.encode()).hexdigest()
