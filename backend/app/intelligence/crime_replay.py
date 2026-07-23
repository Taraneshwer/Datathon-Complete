"""
app/intelligence/crime_replay.py
─────────────────────────────────────────────────────────────────────────────
Crime Replay Engine — reconstructs a complete investigation timeline
chronologically from all associated data sources (FIR, evidence, audit trail,
GPS events, officer actions) to allow step-by-step replay.
─────────────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import logging

from app.models.schemas import CrimeReplayResponse, TimelineEvent
from app.repositories import AuditRepository, CaseRepository, EvidenceRepository

logger = logging.getLogger(__name__)


class CrimeReplayEngine:
    """
    Reconstructs the full investigation timeline for a case.
    Aggregates events from Data Store and returns a sorted timeline.
    """

    def __init__(self, case_repo: CaseRepository, evidence_repo: EvidenceRepository, audit_repo: AuditRepository) -> None:
        self._case_repo = case_repo
        self._evidence_repo = evidence_repo
        self._audit_repo = audit_repo

    async def build_timeline(self, case_id: str) -> CrimeReplayResponse:
        """
        Build a chronological event timeline for a case.

        Event sources merged:
          - FIR registration (Case.created_at)
          - Crime occurrence (Case.incident_datetime)
          - Evidence collection events (EvidenceItem.collected_at)
          - Officer actions (AuditTrail records)
        """
        # Fetch case
        case = await self._case_repo.get(case_id)
        if not case:
            raise ValueError(f"Case '{case_id}' not found.")

        events: list[TimelineEvent] = []

        # ── Event 1: Crime occurrence ─────────────────────────────────────────
        if case.incident_datetime:
            events.append(TimelineEvent(
                event_id=f"{case_id}:crime_occurrence",
                event_type="CRIME_OCCURRENCE",
                timestamp=case.incident_datetime,
                description=f"Crime occurred: {case.title}",
                location=case.location_name,
            ))

        # ── Event 2: FIR Registration ─────────────────────────────────────────
        events.append(TimelineEvent(
            event_id=f"{case_id}:fir_registered",
            event_type="FIR_REGISTERED",
            timestamp=case.created_at,
            actor=case.reporting_officer_id,
            description=f"FIR registered — {case.fir_number}",
            location=case.location_name,
        ))

        # ── Evidence collection events ────────────────────────────────────────
        evidence_items = await self._evidence_repo.get_by_case(case_id)
        for ev in evidence_items:
            ts = ev.collected_at or ev.created_at
            events.append(TimelineEvent(
                event_id=f"ev:{ev.id}",
                event_type="EVIDENCE_COLLECTED",
                timestamp=ts,
                actor=ev.collected_by,
                description=f"Evidence collected ({ev.evidence_type.value}): "
                            f"{ev.description[:120]}",
                evidence_ids=[str(ev.id)],
            ))

        # ── Audit trail events ────────────────────────────────────────────────
        audit_entries = await self._audit_repo.get_by_case(case_id)
        for entry in audit_entries:
            events.append(TimelineEvent(
                event_id=f"audit:{entry.id}",
                event_type=f"OFFICER_ACTION:{entry.action.value.upper()}",
                timestamp=entry.created_at,
                actor=entry.actor,
                description=entry.detail or f"Action: {entry.action.value}",
            ))

        # Sort all events chronologically
        events.sort(key=lambda e: e.timestamp)

        logger.info(
            "CrimeReplayEngine: built timeline for case '%s' — %d events",
            case_id,
            len(events),
        )

        return CrimeReplayResponse(
            case_id=case_id,
            fir_number=case.fir_number,
            total_events=len(events),
            timeline=events,
        )
