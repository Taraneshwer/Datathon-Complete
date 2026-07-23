"""
app/services/ingest_service.py
─────────────────────────────────────────────────────────────────────────────
FIR ingestion orchestration service.

Pipeline:
  1. Data Trust Layer validation
  2. Concurrent writes: PostgreSQL + Neo4j + Qdrant  (asyncio.gather)
  3. Blockchain audit record
─────────────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import asyncio
import logging
import uuid
from datetime import datetime

import h3
from neo4j import AsyncDriver
from qdrant_client import AsyncQdrantClient
from qdrant_client.models import PointStruct
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.config import get_settings
from app.models.fir import AuditAction, AuditTrail, Case, EvidenceItem
from app.models.schemas import FIRIngestRequest, IngestResponse
from app.services.blockchain_service import BlockchainService
from app.services.embedding_service import get_embedding_service
from app.services.graph_service import GraphService
from app.services.trust_service import TrustService

logger = logging.getLogger(__name__)


class IngestService:
    """Orchestrates FIR ingestion across all storage backends."""

    def __init__(
        self,
        db: AsyncSession,
        neo4j_driver: AsyncDriver,
        qdrant: AsyncQdrantClient,
    ) -> None:
        self._db = db
        self._graph = GraphService(neo4j_driver)
        self._qdrant = qdrant
        self._blockchain = BlockchainService(db)
        self._trust = TrustService()
        self._settings = get_settings()

    async def ingest(
        self,
        payload: FIRIngestRequest,
        actor: str = "api",
        ip_address: str | None = None,
    ) -> IngestResponse:
        """Primary ingestion entry point."""

        # ── Step 1: Data Trust Layer ─────────────────────────────────────────
        trust_report = await self._trust.validate(payload)
        if not trust_report.passed:
            raise ValueError(
                f"Data Trust Layer rejected payload. "
                f"Score: {trust_report.overall_score:.2f}. "
                f"Issues: {'; '.join(trust_report.issues)}"
            )

        logger.info(
            "IngestService: trust_score=%.2f | fir=%s actor=%s",
            trust_report.overall_score, payload.fir_number, actor,
        )

        # ── Step 2: Generate stable IDs ──────────────────────────────────────
        case_id = uuid.uuid4()
        qdrant_point_id = str(uuid.uuid4())

        # ── Step 3: Concurrent 3-DB writes ───────────────────────────────────
        results = await asyncio.gather(
            self._write_postgres(payload, case_id, qdrant_point_id, actor, ip_address),
            self._write_neo4j(payload, str(case_id)),
            self._write_qdrant(payload, str(case_id), qdrant_point_id),
            return_exceptions=True,
        )

        for i, res in enumerate(results):
            if isinstance(res, BaseException):
                store = ["PostgreSQL", "Neo4j", "Qdrant"][i]
                logger.error("%s write failed for FIR '%s': %s", store, payload.fir_number, res)
                raise RuntimeError(f"{store} write failed: {res}") from res

        evidence_count, nodes_created, _ = results  # type: ignore[misc]

        # ── Step 4: Blockchain audit record ──────────────────────────────────
        bc_record = await self._blockchain.record(
            case_id=str(case_id),
            record_type="fir",
            entity_id=qdrant_point_id,
            payload={
                "fir_number": payload.fir_number,
                "severity": payload.severity.value,
                "trust_score": trust_report.overall_score,
            },
            officer_id=actor,
        )

        # Persist blockchain hash back onto the Case row
        case_row = (
            await self._db.exec(select(Case).where(Case.id == case_id))
        ).first()
        if case_row:
            case_row.blockchain_tx_id = bc_record.sha256_hash
            self._db.add(case_row)
            await self._db.commit()

        logger.info(
            "Ingest complete | fir=%s nodes=%d evidence=%d",
            payload.fir_number, nodes_created, evidence_count,
        )

        return IngestResponse(
            case_id=case_id,
            fir_number=payload.fir_number,
            qdrant_point_id=qdrant_point_id,
            neo4j_nodes_created=nodes_created,
            evidence_items_stored=evidence_count,
            trust_score=trust_report.overall_score,
            blockchain_hash=bc_record.sha256_hash,
        )

    # ── PostgreSQL ─────────────────────────────────────────────────────────────

    async def _write_postgres(
        self,
        payload: FIRIngestRequest,
        case_id: uuid.UUID,
        qdrant_point_id: str,
        actor: str,
        ip_address: str | None,
    ) -> int:
        existing = await self._db.exec(
            select(Case).where(Case.fir_number == payload.fir_number)
        )
        if existing.first():
            raise ValueError(f"FIR '{payload.fir_number}' already exists.")

        # Compute H3 index if coordinates are available
        h3_index: str | None = None
        if payload.latitude and payload.longitude:
            h3_index = h3.latlng_to_cell(
                payload.latitude,
                payload.longitude,
                self._settings.h3_resolution,
            )

        case = Case(
            id=case_id,
            fir_number=payload.fir_number,
            title=payload.title,
            description=payload.description,
            status=payload.status,
            severity=payload.severity,
            crime_type=payload.crime_type,
            latitude=payload.latitude,
            longitude=payload.longitude,
            h3_index=h3_index,
            location_name=payload.location_name,
            district=payload.district,
            state=payload.state,
            incident_datetime=payload.incident_datetime,
            reporting_officer_id=payload.reporting_officer_id,
            station_code=payload.station_code,
            qdrant_point_id=qdrant_point_id,
        )
        self._db.add(case)
        await self._db.flush()

        evidence_count = 0
        for ev in payload.evidence_items:
            self._db.add(EvidenceItem(
                case_id=case_id,
                evidence_type=ev.evidence_type,
                description=ev.description,
                file_reference=ev.file_reference,
                metadata_json=ev.metadata,
                collected_by=ev.collected_by,
                collected_at=ev.collected_at,
            ))
            evidence_count += 1

        self._db.add(AuditTrail(
            case_id=case_id,
            action=AuditAction.INGEST,
            actor=actor,
            detail=f"FIR ingested. Evidence: {evidence_count}",
            ip_address=ip_address,
        ))

        await self._db.commit()
        return evidence_count

    # ── Neo4j ──────────────────────────────────────────────────────────────────

    async def _write_neo4j(self, payload: FIRIngestRequest, case_id: str) -> int:
        return await self._graph.write_case_graph(
            fir_number=payload.fir_number,
            case_id=case_id,
            entities=payload.graph_entities,
        )

    # ── Qdrant ─────────────────────────────────────────────────────────────────

    async def _write_qdrant(
        self, payload: FIRIngestRequest, case_id: str, point_id: str
    ) -> bool:
        vector = await get_embedding_service().embed(payload.description)
        await self._qdrant.upsert(
            collection_name=self._settings.qdrant_collection,
            points=[PointStruct(
                id=point_id,
                vector=vector,
                payload={
                    "case_id": case_id,
                    "fir_number": payload.fir_number,
                    "title": payload.title,
                    "description": payload.description[:500],
                    "severity": payload.severity.value,
                    "status": payload.status.value,
                    "crime_type": payload.crime_type,
                    "district": payload.district,
                    "state": payload.state,
                    "location_name": payload.location_name,
                    "latitude": payload.latitude,
                    "longitude": payload.longitude,
                    "ingested_at": datetime.utcnow().isoformat(),
                },
            )],
            wait=True,
        )
        return True
