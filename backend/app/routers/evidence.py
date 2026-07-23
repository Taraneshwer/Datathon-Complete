"""
app/routers/evidence.py
─────────────────────────────────────────────────────────────────────────────
Evidence Intelligence router.

Endpoints:
  POST /evidence/{case_id}/analyze   — AI analysis of uploaded evidence file
  GET  /evidence/{case_id}           — List all evidence for a case
  GET  /evidence/item/{evidence_id}  — Get single evidence with AI results
─────────────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import logging
import uuid

from fastapi import APIRouter, File, HTTPException, UploadFile, status
from sqlmodel import select

from app.dependencies import DBSession
from app.intelligence.evidence_analyzer import EvidenceAnalyzer
from app.models.fir import EvidenceItem, EvidenceStatus, EvidenceType
from app.models.schemas import EvidenceAnalysisResult

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/evidence", tags=["Evidence Intelligence"])
_analyzer = EvidenceAnalyzer()


@router.post(
    "/{case_id}/analyze",
    response_model=EvidenceAnalysisResult,
    summary="Upload and AI-analyze an evidence file",
)
async def analyze_evidence(
    case_id: str,
    evidence_id: str,
    evidence_type: EvidenceType,
    db: DBSession,
    file: UploadFile = File(...),
) -> EvidenceAnalysisResult:
    """
    Upload an evidence file and trigger the AI analysis pipeline:
    - Images: face detection + YOLO object detection
    - Documents: EasyOCR multi-language extraction
    - Audio: Whisper speech-to-text
    - Video: frame sampling + object detection

    Returns extracted intelligence with confidence scores.
    """
    from app.config import get_settings
    settings = get_settings()

    # File size check
    content = await file.read()
    if len(content) > settings.evidence_max_file_size_mb * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File exceeds maximum size of {settings.evidence_max_file_size_mb} MB.",
        )

    # Save to temp path for CV processing
    import tempfile, os
    suffix = os.path.splitext(file.filename or "file")[1] or ".bin"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(content)
        tmp_path = tmp.name

    try:
        result = await _analyzer.analyze(
            evidence_id=evidence_id,
            evidence_type=evidence_type,
            file_path=tmp_path,
        )

        # Persist AI analysis back to EvidenceItem
        ev_result = await db.exec(
            select(EvidenceItem).where(EvidenceItem.id == uuid.UUID(evidence_id))
        )
        ev = ev_result.first()
        if ev:
            ev.ai_analysis = result.model_dump(exclude={"evidence_id", "evidence_type"})
            ev.status = EvidenceStatus.ANALYZED
            db.add(ev)
            await db.commit()

    finally:
        os.unlink(tmp_path)

    return result


@router.get(
    "/{case_id}",
    summary="List all evidence items for a case",
)
async def list_evidence(case_id: str, db: DBSession) -> list[dict]:
    """Retrieve all evidence items linked to a case with their AI analysis results."""
    result = await db.exec(
        select(EvidenceItem).where(EvidenceItem.case_id == uuid.UUID(case_id))
    )
    items = result.all()
    return [
        {
            "id": str(ev.id),
            "type": ev.evidence_type.value,
            "status": ev.status.value,
            "description": ev.description,
            "file_reference": ev.file_reference,
            "collected_by": ev.collected_by,
            "collected_at": ev.collected_at.isoformat() if ev.collected_at else None,
            "ai_analysis": ev.ai_analysis,
            "blockchain_hash": ev.blockchain_hash,
        }
        for ev in items
    ]
