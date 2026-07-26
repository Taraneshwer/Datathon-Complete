"""
app/routers/analytics.py
─────────────────────────────────────────────────────────────────────────────
Analytics & Intelligence router.

Endpoints:
  POST /analytics/replay/{case_id}       — Crime timeline replay
  POST /analytics/bias/{case_id}         — Investigation bias detection
  POST /analytics/blind-spots           — Geographic blind spot discovery
  POST /analytics/interventions         — Intervention recommendations
  POST /analytics/early-warning         — National early warning scan
  GET  /analytics/blockchain/{case_id}  — Verify blockchain audit chain
─────────────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException, Query

from app.dependencies import (
    AlertRepoDep,
    AuditRepoDep,
    BlockchainRepoDep,
    CaseRepoDep,
    EvidenceRepoDep,
)
from app.intelligence.bias_detector import BiasDetector
from app.intelligence.blind_spot_detector import BlindSpotDetector
from app.intelligence.crime_replay import CrimeReplayEngine
from app.intelligence.early_warning import EarlyWarningSystem
from app.intelligence.intervention_recommender import InterventionRecommender
from app.models.schemas import (
    BiasDetectionResponse,
    BlindSpotRequest,
    BlindSpotResponse,
    CrimeReplayResponse,
    EarlyWarningResponse,
    InterventionResponse,
)
from app.services.blockchain_service import BlockchainService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/analytics", tags=["Intelligence Analytics"])


# ─────────────────────────────────────────────────────────────────────────────
# POST /analytics/replay/{case_id}
# ─────────────────────────────────────────────────────────────────────────────

@router.post(
    "/replay/{case_id}",
    response_model=CrimeReplayResponse,
    summary="Reconstruct crime investigation timeline",
)
async def get_crime_replay(case_id: str, case_repo: CaseRepoDep, evidence_repo: EvidenceRepoDep, audit_repo: AuditRepoDep) -> CrimeReplayResponse:
    """
    Reconstruct a complete, chronological investigation timeline for a case.
    Merges FIR registration, evidence collection, and officer action events.
    """
    try:
        engine = CrimeReplayEngine(case_repo, evidence_repo, audit_repo)
        return await engine.build_timeline(case_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        logger.error("Replay failed for case %s: %s", case_id, exc, exc_info=True)
        raise HTTPException(status_code=500, detail="Timeline reconstruction failed.")


# ─────────────────────────────────────────────────────────────────────────────
# POST /analytics/bias/{case_id}
# ─────────────────────────────────────────────────────────────────────────────

@router.post(
    "/bias/{case_id}",
    response_model=BiasDetectionResponse,
    summary="Detect investigation bias before court submission",
)
async def detect_bias(case_id: str, case_repo: CaseRepoDep, evidence_repo: EvidenceRepoDep) -> BiasDetectionResponse:
    """
    Analyze a case for systematic investigative bias including:
    evidence imbalance, witness gap, confirmation bias, and missing leads.
    """
    try:
        detector = BiasDetector(case_repo, evidence_repo)
        return await detector.analyze(case_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        logger.error("Bias detection failed: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail="Bias analysis failed.")


# ─────────────────────────────────────────────────────────────────────────────
# POST /analytics/blind-spots
# ─────────────────────────────────────────────────────────────────────────────

@router.post(
    "/blind-spots",
    response_model=BlindSpotResponse,
    summary="Discover geographic surveillance blind spots",
)
async def discover_blind_spots(payload: BlindSpotRequest) -> BlindSpotResponse:
    """
    Tessellate a geographic bounding box using H3 hexagons and identify
    areas with high crime density but insufficient CCTV and patrol coverage.
    Returns ranked blind spots with infrastructure recommendations.
    """
    try:
        detector = BlindSpotDetector()
        return await detector.detect(payload)
    except Exception as exc:
        logger.error("Blind-spot detection failed: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail="Blind-spot analysis failed.")


# ─────────────────────────────────────────────────────────────────────────────
# POST /analytics/interventions
# ─────────────────────────────────────────────────────────────────────────────

@router.post(
    "/interventions",
    response_model=InterventionResponse,
    summary="Generate crime intervention recommendations",
)
async def recommend_interventions(
    risk_score: float = Query(..., ge=0.0, le=1.0, description="Normalised risk score"),
    case_id: str | None = Query(default=None),
    district: str | None = Query(default=None),
) -> InterventionResponse:
    """
    Convert a risk score into ranked, actionable policing interventions
    from drone surveillance to community awareness programs.
    """
    recommender = InterventionRecommender()
    return await recommender.recommend(
        risk_score=risk_score, case_id=case_id, district=district
    )


# ─────────────────────────────────────────────────────────────────────────────
# POST /analytics/early-warning
# ─────────────────────────────────────────────────────────────────────────────

@router.post(
    "/early-warning",
    response_model=EarlyWarningResponse,
    summary="Run national crime early warning scan",
)
async def run_early_warning(
    case_repo: CaseRepoDep,
    alert_repo: AlertRepoDep,
    monitoring_days: int = Query(default=30, ge=7, le=365),
    districts: list[str] | None = Query(default=None),
) -> EarlyWarningResponse:
    """
    Scan crime trends across all districts to detect:
    gang migration, interstate crime, cybercrime spikes, and drug routes.
    Generates and persists structured alerts.
    """
    try:
        ews = EarlyWarningSystem(case_repo, alert_repo)
        return await ews.run_analysis(
            monitoring_days=monitoring_days, districts=districts
        )
    except Exception as exc:
        logger.error("Early warning scan failed: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail="Early warning analysis failed.")


# ─────────────────────────────────────────────────────────────────────────────
# GET /analytics/blockchain/{case_id}
# ─────────────────────────────────────────────────────────────────────────────

@router.get(
    "/blockchain/{case_id}",
    summary="Verify blockchain audit chain integrity for a case",
)
async def verify_blockchain(case_id: str, case_repo: CaseRepoDep, blockchain_repo: BlockchainRepoDep) -> dict:
    """
    Verify the cryptographic audit chain for a case.
    Detects any tampered or missing records in the chain.
    """
    svc = BlockchainService(case_repo, blockchain_repo)
    return await svc.verify_chain(case_id)
