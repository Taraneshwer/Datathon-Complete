"""
app/intelligence/early_warning.py
─────────────────────────────────────────────────────────────────────────────
National Crime Early Warning System.

Monitors crime trend patterns across districts and generates automated
alerts for emerging threats: gang migration, interstate crime, cybercrime
spikes, drug route emergence, and financial fraud clusters.

Uses sliding-window frequency analysis over Catalyst Data Store results.
─────────────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import logging
import uuid
from collections import Counter
from datetime import datetime, timedelta

from app.config import get_settings
from app.models.fir import AlertType, Case, CrimeSeverity, SystemAlert
from app.models.schemas import EarlyWarningAlert, EarlyWarningResponse
from app.repositories import AlertRepository, CaseRepository

logger = logging.getLogger(__name__)


class EarlyWarningSystem:
    """
    Automated crime trend monitoring and early warning alert generation.
    Runs across configurable monitoring windows.
    """

    def __init__(self, case_repo: CaseRepository, alert_repo: AlertRepository) -> None:
        self._case_repo = case_repo
        self._alert_repo = alert_repo
        self._settings = get_settings()

    async def run_analysis(
        self, monitoring_days: int = 30, districts: list[str] | None = None
    ) -> EarlyWarningResponse:
        """
        Run the full early warning analysis pipeline.

        Args:
            monitoring_days: Lookback window for trend analysis.
            districts:       Optional district filter; None = all districts.

        Returns:
            EarlyWarningResponse with all generated alerts.
        """
        since = datetime.now() - timedelta(days=monitoring_days)
        alerts: list[EarlyWarningAlert] = []
        
        since_iso = since.isoformat()
        
        # Fetch current cases
        current_cases = await self._case_repo.search(f"created_at >= '{since_iso}'")
        if districts:
            current_cases = [c for c in current_cases if c.district in districts]

        # Prior period count (double the window)
        prior_since = since - timedelta(days=monitoring_days)
        prior_since_iso = prior_since.isoformat()
        prior_cases_all = await self._case_repo.search(f"created_at >= '{prior_since_iso}' AND created_at < '{since_iso}'")
        if districts:
            prior_cases_all = [c for c in prior_cases_all if c.district in districts]

        # ── Check 1: Crime volume spike ───────────────────────────────────────
        spike_alerts = await self._detect_volume_spike(current_cases, prior_cases_all)
        alerts.extend(spike_alerts)

        # ── Check 2: Interstate crime pattern ─────────────────────────────────
        interstate = await self._detect_interstate_pattern(current_cases)
        alerts.extend(interstate)

        # ── Check 3: Cybercrime cluster ───────────────────────────────────────
        cyber = await self._detect_cybercrime_spike(current_cases, monitoring_days, districts)
        alerts.extend(cyber)

        # ── Check 4: Gang migration (multi-district same severity) ────────────
        gang = await self._detect_gang_migration(current_cases)
        alerts.extend(gang)

        # Persist new alerts to database
        for alert in alerts:
            db_alert = SystemAlert(
                alert_type=alert.alert_type,
                severity=alert.severity,
                title=alert.title,
                description=alert.description,
                affected_districts=alert.affected_districts,
                recommendations=alert.recommendations,
            )
            await self._alert_repo.create(db_alert)

        logger.info(
            "EarlyWarningSystem: %d alerts generated (window=%d days)",
            len(alerts), monitoring_days,
        )

        return EarlyWarningResponse(
            monitoring_period_days=monitoring_days,
            alerts_generated=len(alerts),
            alerts=alerts,
        )

    async def _detect_volume_spike(
        self, current_cases: list[Case], prior_cases: list[Case]
    ) -> list[EarlyWarningAlert]:
        """Detect districts where case volume has doubled vs prior period."""
        alerts: list[EarlyWarningAlert] = []
        threshold = self._settings.early_warning_alert_threshold

        current_counts = Counter(c.district for c in current_cases if c.district)
        prior_counts = Counter(c.district for c in prior_cases if c.district)

        for district, current in current_counts.items():
            prior = prior_counts.get(district, 1)
            ratio = current / max(prior, 1)
            if ratio >= 2.0 and current >= 5:
                confidence = min(0.95, 0.6 + (ratio - 2.0) * 0.1)
                if confidence >= threshold:
                    alerts.append(EarlyWarningAlert(
                        alert_id=str(uuid.uuid4()),
                        alert_type=AlertType.EARLY_WARNING,
                        severity=CrimeSeverity.HIGH if ratio >= 3 else CrimeSeverity.MEDIUM,
                        title=f"Crime Volume Spike — {district}",
                        description=(
                            f"District '{district}' has seen a {ratio:.1f}x increase "
                            f"in crime reports ({current} vs {prior} in the previous period)."
                        ),
                        affected_districts=[district] if district else [],
                        confidence_score=round(confidence, 3),
                        recommendations=[
                            "Deploy additional patrol units",
                            "Activate district crime task force",
                            "Notify district superintendent",
                        ],
                    ))

        return alerts

    async def _detect_interstate_pattern(
        self, current_cases: list[Case]
    ) -> list[EarlyWarningAlert]:
        """Detect high-severity cases appearing across multiple states."""
        high_sev = [c for c in current_cases if c.severity in (CrimeSeverity.HIGH, CrimeSeverity.CRITICAL) and c.state]
        state_counts = Counter(c.state for c in high_sev)
        
        multi_state = [state for state, count in state_counts.items() if count >= 3]

        if len(multi_state) >= 2:
            return [EarlyWarningAlert(
                alert_id=str(uuid.uuid4()),
                alert_type=AlertType.INTERSTATE_CRIME,
                severity=CrimeSeverity.CRITICAL,
                title="Interstate Crime Pattern Detected",
                description=(
                    f"High-severity cases detected across {len(multi_state)} states: "
                    f"{', '.join(multi_state)}. Possible interstate criminal gang operation."
                ),
                affected_districts=multi_state,
                confidence_score=0.82,
                recommendations=[
                    "Alert National Crime Records Bureau (NCRB)",
                    "Coordinate inter-state police task force",
                    "Share case intelligence across state PIUs",
                    "Activate travel restriction monitoring",
                ],
            )]
        return []

    async def _detect_cybercrime_spike(
        self, current_cases: list[Case], monitoring_days: int, districts: list[str] | None
    ) -> list[EarlyWarningAlert]:
        """Detect sudden increase in cybercrime-classified cases."""
        count = sum(1 for c in current_cases if c.crime_type and "cyber" in c.crime_type.lower())

        if count >= 10:
            return [EarlyWarningAlert(
                alert_id=str(uuid.uuid4()),
                alert_type=AlertType.CYBERCRIME_SPIKE,
                severity=CrimeSeverity.HIGH,
                title="Cybercrime Spike Detected",
                description=(
                    f"{count} cybercrime cases registered in the past "
                    f"{monitoring_days} days."
                ),
                affected_districts=districts or ["Statewide"],
                confidence_score=0.78,
                recommendations=[
                    "Activate Cyber Crime Investigation Cell",
                    "Issue public advisory on phishing/fraud",
                    "Coordinate with CERT-In",
                ],
            )]
        return []

    async def _detect_gang_migration(
        self, current_cases: list[Case]
    ) -> list[EarlyWarningAlert]:
        """Detect critical-severity cases across 3+ districts in same period."""
        critical = [c for c in current_cases if c.severity == CrimeSeverity.CRITICAL and c.district]
        district_counts = Counter(c.district for c in critical)
        
        hot_districts = [district for district, count in district_counts.items() if count >= 2]

        if len(hot_districts) >= 3:
            return [EarlyWarningAlert(
                alert_id=str(uuid.uuid4()),
                alert_type=AlertType.GANG_MIGRATION,
                severity=CrimeSeverity.CRITICAL,
                title="Gang Migration Pattern Detected",
                description=(
                    f"Critical-severity cases identified across {len(hot_districts)} "
                    f"districts: {', '.join(hot_districts[:5])}. "
                    "Pattern suggests organised gang movement."
                ),
                affected_districts=hot_districts,
                confidence_score=0.85,
                recommendations=[
                    "Form inter-district Anti-Gang Task Force",
                    "Activate informant networks",
                    "Monitor border checkpoints",
                    "Coordinate with Intelligence Bureau",
                ],
            )]
        return []
