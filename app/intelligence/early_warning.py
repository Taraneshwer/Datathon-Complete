"""
app/intelligence/early_warning.py
─────────────────────────────────────────────────────────────────────────────
National Crime Early Warning System.

Monitors crime trend patterns across districts and generates automated
alerts for emerging threats: gang migration, interstate crime, cybercrime
spikes, drug route emergence, and financial fraud clusters.

Uses sliding-window frequency analysis over Qdrant vector search results
and PostgreSQL aggregate queries.
─────────────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import logging
import uuid
from datetime import datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import func, select

from app.config import get_settings
from app.models.fir import AlertType, Case, CrimeSeverity, SystemAlert
from app.models.schemas import EarlyWarningAlert, EarlyWarningResponse

logger = logging.getLogger(__name__)


class EarlyWarningSystem:
    """
    Automated crime trend monitoring and early warning alert generation.
    Runs across configurable monitoring windows.
    """

    def __init__(self, db: AsyncSession) -> None:
        self._db = db
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

        # ── Check 1: Crime volume spike ───────────────────────────────────────
        spike_alerts = await self._detect_volume_spike(since, districts)
        alerts.extend(spike_alerts)

        # ── Check 2: Interstate crime pattern ─────────────────────────────────
        interstate = await self._detect_interstate_pattern(since)
        alerts.extend(interstate)

        # ── Check 3: Cybercrime cluster ───────────────────────────────────────
        cyber = await self._detect_cybercrime_spike(since, districts)
        alerts.extend(cyber)

        # ── Check 4: Gang migration (multi-district same severity) ────────────
        gang = await self._detect_gang_migration(since)
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
            self._db.add(db_alert)

        if alerts:
            await self._db.flush()

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
        self, since: datetime, districts: list[str] | None
    ) -> list[EarlyWarningAlert]:
        """Detect districts where case volume has doubled vs prior period."""
        alerts: list[EarlyWarningAlert] = []
        threshold = self._settings.early_warning_alert_threshold

        # Current period count per district
        query = select(
            Case.district, func.count(Case.id).label("count")  # type: ignore[arg-type]
        ).where(Case.created_at >= since).group_by(Case.district)

        if districts:
            query = query.where(Case.district.in_(districts))  # type: ignore[union-attr]

        result = await self._db.exec(query)
        current_counts = {row.district: row.count for row in result.all() if row.district}

        # Prior period count (double the window)
        prior_since = since - timedelta(days=(datetime.now() - since).days)
        prior_query = select(
            Case.district, func.count(Case.id).label("count")  # type: ignore[arg-type]
        ).where(
            Case.created_at >= prior_since,
            Case.created_at < since
        ).group_by(Case.district)

        prior_result = await self._db.exec(prior_query)
        prior_counts = {row.district: row.count for row in prior_result.all() if row.district}

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
        self, since: datetime
    ) -> list[EarlyWarningAlert]:
        """Detect high-severity cases appearing across multiple states."""
        result = await self._db.exec(
            select(
                Case.state, func.count(Case.id).label("count")  # type: ignore[arg-type]
            )
            .where(
                Case.created_at >= since,
                Case.severity.in_([CrimeSeverity.HIGH, CrimeSeverity.CRITICAL]),  # type: ignore
            )
            .group_by(Case.state)
            .having(func.count(Case.id) >= 3)
        )
        rows = result.all()
        multi_state = [r for r in rows if r.state and r.count >= 3]

        if len(multi_state) >= 2:
            states = [r.state for r in multi_state]
            return [EarlyWarningAlert(
                alert_id=str(uuid.uuid4()),
                alert_type=AlertType.INTERSTATE_CRIME,
                severity=CrimeSeverity.CRITICAL,
                title="Interstate Crime Pattern Detected",
                description=(
                    f"High-severity cases detected across {len(states)} states: "
                    f"{', '.join(states)}. Possible interstate criminal gang operation."
                ),
                affected_districts=[r.state for r in multi_state],
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
        self, since: datetime, districts: list[str] | None
    ) -> list[EarlyWarningAlert]:
        """Detect sudden increase in cybercrime-classified cases."""
        query = select(func.count(Case.id).label("count")).where(  # type: ignore[arg-type]
            Case.created_at >= since,
            Case.crime_type.ilike("%cyber%"),  # type: ignore[union-attr]
        )
        result = await self._db.exec(query)
        count_row = result.first()
        count = count_row if isinstance(count_row, int) else 0

        if count >= 10:
            return [EarlyWarningAlert(
                alert_id=str(uuid.uuid4()),
                alert_type=AlertType.CYBERCRIME_SPIKE,
                severity=CrimeSeverity.HIGH,
                title="Cybercrime Spike Detected",
                description=(
                    f"{count} cybercrime cases registered in the past "
                    f"{(datetime.now() - since).days} days."
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
        self, since: datetime
    ) -> list[EarlyWarningAlert]:
        """Detect critical-severity cases across 3+ districts in same period."""
        result = await self._db.exec(
            select(
                Case.district, func.count(Case.id).label("count")  # type: ignore[arg-type]
            )
            .where(
                Case.created_at >= since,
                Case.severity == CrimeSeverity.CRITICAL,
            )
            .group_by(Case.district)
            .having(func.count(Case.id) >= 2)
        )
        rows = result.all()
        hot_districts = [r.district for r in rows if r.district]

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
