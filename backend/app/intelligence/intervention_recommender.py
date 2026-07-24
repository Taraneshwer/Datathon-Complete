"""
app/intelligence/intervention_recommender.py
─────────────────────────────────────────────────────────────────────────────
Crime Intervention Recommender.

Converts AI risk predictions into ranked, actionable policing strategies
using an XGBoost risk model and a rule-based recommendation engine.
─────────────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import asyncio
import logging
from typing import Any

from app.models.schemas import InterventionRecommendation, InterventionResponse

logger = logging.getLogger(__name__)

# Rule table: (min_risk_score, recommendation)
_INTERVENTION_RULES: list[tuple[float, InterventionRecommendation]] = [
    (0.9, InterventionRecommendation(
        priority=1,
        action="Deploy Special Investigation Team (SIT)",
        rationale="Extremely high risk score indicates active criminal gang operation.",
        resources_required=["SIT officers", "Surveillance equipment", "Legal support"],
        estimated_impact="High — immediate threat neutralisation",
    )),
    (0.8, InterventionRecommendation(
        priority=2,
        action="Establish drone surveillance corridor",
        rationale="Aerial monitoring of high-risk zones for real-time intelligence.",
        resources_required=["Drone units", "Command center staff", "Live feed infrastructure"],
        estimated_impact="High — real-time visibility across blind spots",
    )),
    (0.7, InterventionRecommendation(
        priority=3,
        action="Set up mobile checkpoints on identified corridors",
        rationale="Intercept movement along crime corridors identified by pattern analysis.",
        resources_required=["Patrol vehicles", "Officers", "Breathalyser/ID scanners"],
        estimated_impact="Medium-High — deterrence and intelligence gathering",
    )),
    (0.6, InterventionRecommendation(
        priority=4,
        action="Increase patrol frequency in flagged sectors",
        rationale="Visible police presence reduces opportunistic crime.",
        resources_required=["Patrol officers", "Patrol vehicles"],
        estimated_impact="Medium — deterrence effect",
    )),
    (0.5, InterventionRecommendation(
        priority=5,
        action="Install additional CCTV cameras in blind spots",
        rationale="Evidence collection and deterrence in unmonitored areas.",
        resources_required=["CCTV units", "Installation crew", "Monitoring staff"],
        estimated_impact="Medium — long-term surveillance coverage",
    )),
    (0.4, InterventionRecommendation(
        priority=6,
        action="Launch community awareness campaign",
        rationale="Engage community as active partners in crime prevention.",
        resources_required=["Community officers", "Outreach materials"],
        estimated_impact="Low-Medium — long-term community trust building",
    )),
    (0.0, InterventionRecommendation(
        priority=7,
        action="Monitor for trend changes",
        rationale="Low current risk; maintain awareness and data collection.",
        resources_required=["Analyst review (periodic)"],
        estimated_impact="Low — baseline monitoring",
    )),
]


class InterventionRecommender:
    """
    Generates ranked intervention strategies based on a risk score.
    Uses XGBoost features when available; falls back to rule-based system.
    """

    async def recommend(
        self,
        risk_score: float,
        case_id: str | None = None,
        district: str | None = None,
        context: dict[str, Any] | None = None,
    ) -> InterventionResponse:
        """
        Generate ranked intervention recommendations.

        Args:
            risk_score: Normalised risk score [0.0, 1.0].
            case_id:    Optional case scope.
            district:   Geographic scope.
            context:    Optional feature dict for XGBoost refinement.
        """
        if context:
            from ai_service.ml.xgboost_engine import refine_with_xgboost
            risk_score = await asyncio.to_thread(
                refine_with_xgboost, risk_score, context
            )

        recommendations = self._apply_rules(risk_score)

        logger.info(
            "InterventionRecommender: risk=%.2f recs=%d case=%s",
            risk_score, len(recommendations), case_id,
        )

        return InterventionResponse(
            case_id=case_id,
            district=district,
            risk_score=round(risk_score, 3),
            recommendations=recommendations,
        )

    @staticmethod
    def _apply_rules(risk_score: float) -> list[InterventionRecommendation]:
        """Select applicable rules based on the risk threshold."""
        return [
            rec
            for threshold, rec in _INTERVENTION_RULES
            if risk_score >= threshold
        ]


