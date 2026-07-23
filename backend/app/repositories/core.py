"""
app/repositories/core.py
─────────────────────────────────────────────────────────────────────────────
Specific Catalyst Data Store repositories for core entities.
─────────────────────────────────────────────────────────────────────────────
"""
import uuid

from app.models.fir import AuditTrail, BlockchainRecord, Case, EvidenceItem, Officer, SystemAlert
from app.repositories.base import BaseRepository


class OfficerRepository(BaseRepository[Officer]):
    def __init__(self) -> None:
        super().__init__(model_class=Officer, table_name="officers")

    async def get_by_badge(self, badge_number: str) -> Officer | None:
        results = await self.search(f"badge_number = '{badge_number}'")
        return results[0] if results else None

class CaseRepository(BaseRepository[Case]):
    def __init__(self) -> None:
        super().__init__(model_class=Case, table_name="cases")

    async def get_by_fir_number(self, fir_number: str) -> Case | None:
        results = await self.search(f"fir_number = '{fir_number}'")
        return results[0] if results else None

class EvidenceRepository(BaseRepository[EvidenceItem]):
    def __init__(self) -> None:
        super().__init__(model_class=EvidenceItem, table_name="evidence_items")
        
    async def get_by_case(self, case_id: uuid.UUID | str) -> list[EvidenceItem]:
        return await self.search(f"case_id = '{str(case_id)}'")

class BlockchainRepository(BaseRepository[BlockchainRecord]):
    def __init__(self) -> None:
        super().__init__(model_class=BlockchainRecord, table_name="blockchain_records")

    async def get_by_case(self, case_id: uuid.UUID | str) -> list[BlockchainRecord]:
        return await self.search(f"case_id = '{str(case_id)}'")

class AlertRepository(BaseRepository[SystemAlert]):
    def __init__(self) -> None:
        super().__init__(model_class=SystemAlert, table_name="system_alerts")

    async def get_by_case(self, case_id: uuid.UUID | str) -> list[SystemAlert]:
        return await self.search(f"case_id = '{str(case_id)}'")

class AuditRepository(BaseRepository[AuditTrail]):
    def __init__(self) -> None:
        super().__init__(model_class=AuditTrail, table_name="audit_trails")

    async def get_by_case(self, case_id: uuid.UUID | str) -> list[AuditTrail]:
        return await self.search(f"case_id = '{str(case_id)}'")
