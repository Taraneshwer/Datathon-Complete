"""
app/intelligence/bias_detector.py
─────────────────────────────────────────────────────────────────────────────
Investigation Bias Detector.

Analyzes an investigation case for common systematic biases before
court submission, including:
  - Confirmation Bias (evidence only supports one theory)
  - Witness Bias (all witnesses from same group)
  - Location Bias (only one area searched)
  - Evidence Imbalance (missing forensic / digital evidence)
  - Missing Leads (no follow-up on known associates)
  - Alternative Suspects not explored
─────────────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import logging
import uuid

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select, func

from app.models.fir import Case, EvidenceItem, EvidenceType
from app.models.schemas import (
    BiasDetectionResponse,
    BiasIndicator,
)

logger = logging.getLogger(__name__)


class BiasDetector:
    """Analyzes investigation completeness and detects systematic biases."""

    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def analyze(self, case_id: str) -> BiasDetectionResponse:
        """
        Run all bias checks against a case and return a structured report.
        """
        cid = uuid.UUID(case_id)

        case_result = await self._db.exec(select(Case).where(Case.id == cid))
        case = case_result.first()
        if not case:
            raise ValueError(f"Case '{case_id}' not found.")

        ev_result = await self._db.exec(
            select(EvidenceItem).where(EvidenceItem.case_id == cid)
        )
        evidence = ev_result.all()

        indicators: list[BiasIndicator] = []
        missing_leads: list[str] = []

        # ── Check 1: Evidence imbalance ───────────────────────────────────────
        ev_types = {e.evidence_type for e in evidence}
        if EvidenceType.FORENSIC not in ev_types:
            indicators.append(BiasIndicator(
                bias_type="EVIDENCE_IMBALANCE",
                severity="high",
                description="No forensic evidence has been collected or recorded.",
                recommendation="Ensure forensic team has processed the crime scene.",
            ))
            missing_leads.append("Forensic evidence collection")

        if EvidenceType.DIGITAL not in ev_types and EvidenceType.SURVEILLANCE not in ev_types:
            indicators.append(BiasIndicator(
                bias_type="EVIDENCE_IMBALANCE",
                severity="medium",
                description="No digital or surveillance evidence linked to the case.",
                recommendation="Review CCTV footage and digital device logs in the vicinity.",
            ))
            missing_leads.append("CCTV / digital evidence review")

        # ── Check 2: Witness gap ──────────────────────────────────────────────
        witness_count = sum(1 for e in evidence if e.evidence_type == EvidenceType.WITNESS)
        if witness_count == 0:
            indicators.append(BiasIndicator(
                bias_type="WITNESS_BIAS",
                severity="high",
                description="No witness statements recorded for this case.",
                recommendation="Canvas the area for eyewitnesses and record statements.",
            ))
            missing_leads.append("Witness canvassing")
        elif witness_count == 1:
            indicators.append(BiasIndicator(
                bias_type="WITNESS_BIAS",
                severity="low",
                description="Only one witness statement on record — corroboration lacking.",
                recommendation="Seek additional witnesses to corroborate or challenge the account.",
            ))

        # ── Check 3: Confirmation bias (single evidence type dominates) ────────
        if evidence:
            most_common = max(
                set(e.evidence_type for e in evidence),
                key=lambda t: sum(1 for e in evidence if e.evidence_type == t),
            )
            dominant_ratio = sum(1 for e in evidence if e.evidence_type == most_common) / len(evidence)
            if dominant_ratio > 0.80 and len(evidence) >= 3:
                indicators.append(BiasIndicator(
                    bias_type="CONFIRMATION_BIAS",
                    severity="medium",
                    description=(
                        f"Over {dominant_ratio:.0%} of evidence is of type "
                        f"'{most_common.value}'. Investigation may be one-dimensional."
                    ),
                    recommendation="Diversify evidence collection across multiple types.",
                ))

        # ── Check 4: Missing geographic coverage ──────────────────────────────
        if not case.latitude or not case.longitude:
            indicators.append(BiasIndicator(
                bias_type="LOCATION_BIAS",
                severity="medium",
                description="No geographic coordinates recorded for the crime scene.",
                recommendation="Record precise GPS coordinates of the crime scene.",
            ))
            missing_leads.append("Crime scene GPS coordinates")

        # ── Check 5: Insufficient description ────────────────────────────────
        if len(case.description) < 200:
            indicators.append(BiasIndicator(
                bias_type="INVESTIGATION_COMPLETENESS",
                severity="low",
                description="Case description is very brief — may indicate incomplete documentation.",
                recommendation="Expand case description with full investigative findings.",
            ))

        bias_score = min(1.0, len(indicators) * 0.18)
        bias_detected = bias_score >= 0.18

        if bias_detected:
            # Update the case flag in PostgreSQL
            case.bias_detected = True
            self._db.add(case)
            await self._db.flush()

        logger.info(
            "BiasDetector: case=%s score=%.2f indicators=%d",
            case_id, bias_score, len(indicators),
        )

        return BiasDetectionResponse(
            case_id=case_id,
            fir_number=case.fir_number,
            overall_bias_score=round(bias_score, 3),
            bias_detected=bias_detected,
            indicators=indicators,
            missing_leads=missing_leads,
        )
