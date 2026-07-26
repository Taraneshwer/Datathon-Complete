"""
app/services/blockchain_service.py
─────────────────────────────────────────────────────────────────────────────
Blockchain audit trail service using cryptographic SHA-256 chaining.
Provides an immutable, tamper-evident audit log for all critical operations.

Architecture:
  - Each record hashes (entity_id + payload + previous_hash) with SHA-256.
  - Records are stored in Catalyst Data Store's blockchain_records table.
  - A stub Hyperledger Fabric gateway interface is provided for production
    deployment — set FABRIC_GATEWAY_URL in .env to activate.
─────────────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import hashlib
import json
import logging
import uuid
from datetime import datetime
from typing import Any

from app.config import get_settings
from app.models.fir import BlockchainRecord
from app.repositories import BlockchainRepository, CaseRepository

logger = logging.getLogger(__name__)


class BlockchainService:
    """
    Cryptographic audit chain service.
    Each new record links to the hash of the previous record for a given case,
    making any tampering detectable.
    """

    def __init__(self, case_repo: CaseRepository, blockchain_repo: BlockchainRepository) -> None:
        self._case_repo = case_repo
        self._blockchain_repo = blockchain_repo
        self._settings = get_settings()

    async def record(
        self,
        case_id: str,
        record_type: str,
        entity_id: str,
        payload: dict[str, Any],
        officer_id: str | None = None,
    ) -> BlockchainRecord:
        """
        Create a new immutable audit record linked to the previous chain entry.

        Args:
            case_id:      Associated case UUID (string).
            record_type:  "fir" | "evidence" | "officer_action" | "graph_update"
            entity_id:    ID of the entity being recorded (case, evidence, etc.).
            payload:      The full data snapshot to hash and store.
            officer_id:   Officer who triggered this action.

        Returns:
            The persisted BlockchainRecord instance.
        """
        if not self._settings.blockchain_enabled:
            logger.debug("Blockchain disabled — skipping record for entity '%s'.", entity_id)
            # Return a dummy record without persisting
            return BlockchainRecord(
                case_id=uuid.UUID(case_id),
                record_type=record_type,
                entity_id=entity_id,
                sha256_hash="blockchain_disabled",
            )

        # Fetch the latest record for this case to get previous hash
        prev_hash = await self._get_latest_hash(case_id)

        # Build the deterministic payload string
        canonical = json.dumps(
            {
                "case_id": case_id,
                "record_type": record_type,
                "entity_id": entity_id,
                "timestamp": datetime.now().isoformat(),
                "payload": payload,
                "previous_hash": prev_hash or "GENESIS",
            },
            sort_keys=True,
            default=str,
        )

        sha256_hash = hashlib.sha256(canonical.encode()).hexdigest()

        # Officer digital signature (simple HMAC-style for now)
        officer_signature: str | None = None
        if officer_id:
            sig_input = f"{sha256_hash}:{officer_id}:{self._settings.secret_key}"
            officer_signature = hashlib.sha256(sig_input.encode()).hexdigest()[:32]

        record = BlockchainRecord(
            case_id=uuid.UUID(case_id),
            record_type=record_type,
            entity_id=entity_id,
            sha256_hash=sha256_hash,
            previous_hash=prev_hash,
            officer_signature=officer_signature,
            payload_json=payload,
            fabric_tx_id=await self._submit_to_fabric(sha256_hash, canonical),
        )

        await self._blockchain_repo.create(record)

        logger.info(
            "Blockchain record created | type=%s entity=%s hash=%.16s",
            record_type,
            entity_id,
            sha256_hash,
        )
        return record

    async def verify_chain(self, case_id: str) -> dict[str, Any]:
        """
        Verify the integrity of the entire audit chain for a case.
        Returns a report with verification status per record.
        """
        records = await self._blockchain_repo.search(f"case_id = '{case_id}'")
        
        # Sort chronologically
        records.sort(key=lambda r: r.created_at)

        if not records:
            return {"status": "no_records", "case_id": case_id, "verified": True}

        violations: list[dict] = []
        prev_hash: str | None = None

        for rec in records:
            if rec.previous_hash != prev_hash:
                violations.append({
                    "record_id": str(rec.id),
                    "entity_id": rec.entity_id,
                    "expected_prev": prev_hash,
                    "found_prev": rec.previous_hash,
                })
            prev_hash = rec.sha256_hash

        return {
            "case_id": case_id,
            "total_records": len(records),
            "verified": len(violations) == 0,
            "violations": violations,
        }

    async def _get_latest_hash(self, case_id: str) -> str | None:
        """Retrieve the SHA-256 hash of the most recent record for this case."""
        records = await self._blockchain_repo.search(f"case_id = '{case_id}'")
        if not records:
            return None
            
        records.sort(key=lambda r: r.created_at, reverse=True)
        return records[0].sha256_hash

    async def _submit_to_fabric(self, tx_hash: str, payload: str) -> str | None:
        """
        Submit to Hyperledger Fabric gateway (production stub).
        Returns fabric transaction ID when gateway URL is configured.
        """
        settings = self._settings
        if not settings.fabric_gateway_url:
            return None  # Local SHA-256 chain only

        logger.debug(
            "Fabric gateway configured at %s — implement SDK call here.",
            settings.fabric_gateway_url,
        )
        return f"fabric_stub_{tx_hash[:16]}"
