"""
app/services/ingest_service.py
─────────────────────────────────────────────────────────────────────────────
100% Zoho Catalyst-Native FIR Ingestion Orchestration Service.
Replaces concurrent writes to Neo4j and Qdrant with native writes to
Catalyst Data Store SQL tables (Case, Evidence, Audit, Graph) and QuickML KB.
─────────────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations
import asyncio
import logging
import uuid
from datetime import datetime
from app.config import get_settings
from app.models.fir import AuditAction, AuditTrail, Case, EvidenceItem
from app.models.schemas import FIRIngestRequest, IngestResponse
from app.repositories import AuditRepository, CaseRepository, EvidenceRepository
from app.services.blockchain_service import BlockchainService
from ai_service.embeddings.service import get_embedding_service
from app.services.graph_service import GraphService
from app.services.trust_service import TrustService
from app.db.catalyst import CatalystDBClient

logger = logging.getLogger(__name__)

class IngestService:
    """Orchestrates FIR ingestion natively across Zoho Catalyst Data Store & QuickML."""
    def __init__(
        self,
        case_repo: CaseRepository,
        evidence_repo: EvidenceRepository,
        audit_repo: AuditRepository,
        db_client: Any = None,
        **kwargs: Any,
    ) -> None:
        self._case_repo = case_repo
        self._evidence_repo = evidence_repo
        self._audit_repo = audit_repo
        self.db = db_client if isinstance(db_client, CatalystDBClient) else CatalystDBClient()
        self._graph = GraphService(self.db)
        from app.repositories import BlockchainRepository
        self._blockchain = BlockchainService(self._case_repo, BlockchainRepository())
        self._trust = TrustService()
        self._settings = get_settings()

    async def ingest(
        self,
        payload: FIRIngestRequest,
        actor: str = "api",
        ip_address: str | None = None,
    ) -> IngestResponse:
        """Primary ingestion entry point executing 100% inside Zoho Catalyst Cloud."""
        # Step 1: Data Trust Layer
        trust_report = await self._trust.validate(payload)
        if not trust_report.passed:
            raise ValueError(
                f"Data Trust Layer rejected payload. Score: {trust_report.overall_score:.2f}. Issues: {'; '.join(trust_report.issues)}"
            )

        logger.info("IngestService (Catalyst Native): trust_score=%.2f | fir=%s actor=%s", trust_report.overall_score, payload.fir_number, actor)

        # Step 2: Generate stable IDs
        case_id = uuid.uuid4()
        quickml_kb_doc_id = str(uuid.uuid4())

        # Step 3: Concurrent Catalyst Cloud writes (Data Store Relational + Graph + QuickML KB)
        results = await asyncio.gather(
            self._write_catalyst(payload, case_id, quickml_kb_doc_id, actor, ip_address),
            self._write_catalyst_graph(payload, str(case_id)),
            self._write_quickml_kb(payload, str(case_id), quickml_kb_doc_id),
            return_exceptions=True,
        )

        for i, res in enumerate(results):
            if isinstance(res, BaseException):
                store = ["Catalyst Data Store (Core)", "Catalyst Graph Engine", "Catalyst QuickML KB"][i]
                logger.error("%s write failed for FIR '%s': %s", store, payload.fir_number, res)
                raise RuntimeError(f"{store} write failed: {res}") from res

        evidence_count, nodes_created, _ = results  # type: ignore[misc]

        # Step 4: Blockchain audit record
        bc_record = await self._blockchain.record(
            case_id=str(case_id),
            record_type="fir",
            entity_id=quickml_kb_doc_id,
            payload={"fir_number": payload.fir_number, "severity": payload.severity.value, "trust_score": trust_report.overall_score},
            officer_id=actor,
        )

        case_row = await self._case_repo.get(case_id)
        if case_row:
            case_row.blockchain_tx_id = bc_record.sha256_hash
            await self._case_repo.update(case_row)

        logger.info("Catalyst Ingest complete | fir=%s nodes=%d evidence=%d", payload.fir_number, nodes_created, evidence_count)

        return IngestResponse(
            case_id=case_id,
            fir_number=payload.fir_number,
            qdrant_point_id=quickml_kb_doc_id,
            neo4j_nodes_created=nodes_created,
            evidence_items_stored=evidence_count,
            trust_score=trust_report.overall_score,
            blockchain_hash=bc_record.sha256_hash,
        )

    async def _write_catalyst(
        self, payload: FIRIngestRequest, case_id: uuid.UUID, qdrant_point_id: str, actor: str, ip_address: str | None,
    ) -> int:
        existing = await self._case_repo.get_by_fir_number(payload.fir_number)
        if existing:
            raise ValueError(f"FIR '{payload.fir_number}' already exists.")

        h3_index: str | None = None
        if payload.latitude and payload.longitude:
            try:
                import h3
                h3_index = h3.latlng_to_cell(payload.latitude, payload.longitude, self._settings.h3_resolution)
            except ImportError:
                logger.warning("h3 library not installed; skipping H3 spatial indexing for FIR %s", payload.fir_number)

        case = Case(
            id=case_id, fir_number=payload.fir_number, title=payload.title, description=payload.description,
            status=payload.status, severity=payload.severity, crime_type=payload.crime_type,
            latitude=payload.latitude, longitude=payload.longitude, h3_index=h3_index,
            location_name=payload.location_name, district=payload.district, state=payload.state,
            incident_datetime=payload.incident_datetime, reporting_officer_id=payload.reporting_officer_id,
            station_code=payload.station_code, qdrant_point_id=qdrant_point_id,
        )
        await self._case_repo.create(case)

        evidence_count = 0
        for ev in payload.evidence_items:
            await self._evidence_repo.create(EvidenceItem(
                case_id=case_id, evidence_type=ev.evidence_type, description=ev.description,
                file_reference=ev.file_reference, metadata_json=ev.metadata, collected_by=ev.collected_by, collected_at=ev.collected_at,
            ))
            evidence_count += 1

        await self._audit_repo.create(AuditTrail(
            case_id=case_id, action=AuditAction.INGEST, actor=actor, detail=f"FIR ingested. Evidence: {evidence_count}", ip_address=ip_address,
        ))
        return evidence_count

    async def _write_catalyst_graph(self, payload: FIRIngestRequest, case_id: str) -> int:
        return await self._graph.write_case_graph(fir_number=payload.fir_number, case_id=case_id, entities=payload.graph_entities)

    async def _write_quickml_kb(self, payload: FIRIngestRequest, case_id: str, point_id: str) -> bool:
        try:
            quickml = self.db.get_quickml_service()
            kb = quickml.knowledge_base(self._settings.quickml_kb_name)
            kb.insert(
                doc_id=point_id,
                text=payload.description,
                metadata={
                    "case_id": case_id, "fir_number": payload.fir_number, "title": payload.title,
                    "severity": payload.severity.value, "status": payload.status.value,
                    "crime_type": payload.crime_type, "district": payload.district, "state": payload.state,
                }
            )
        except Exception as e:
            logger.warning(f"Failed to index vector in QuickML Knowledge Base: {e}")
            return False
        return True
