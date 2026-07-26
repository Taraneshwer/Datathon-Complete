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

import io
import uuid

from fastapi import APIRouter, File, Form, HTTPException, Query, UploadFile, status
from fastapi.responses import StreamingResponse

from app.dependencies import ActorDep, EvidenceRepoDep, StorageServiceDep
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
    evidence_repo: EvidenceRepoDep,
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

    # Pass in-memory file content directly to Zia AI analyzer (Zero local disk writing)
    result = await _analyzer.analyze(
        evidence_id=evidence_id,
        evidence_type=evidence_type,
        file_data=content,
    )

    # Persist AI analysis back to EvidenceItem
    ev = await evidence_repo.get(evidence_id)
    if ev:
        ev.ai_analysis = result.model_dump(exclude={"evidence_id", "evidence_type"})
        ev.status = EvidenceStatus.ANALYZED
        await evidence_repo.update(ev)

    return result


@router.get(
    "/case/{case_id}",
    summary="List all evidence items for a case",
)
async def list_evidence(case_id: str, evidence_repo: EvidenceRepoDep) -> list[dict]:
    """Retrieve all evidence items linked to a case with their AI analysis results."""
    items = await evidence_repo.get_by_case(case_id)
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

@router.post("/upload", summary="Upload evidence to Catalyst Stratus")
async def upload_evidence_file(
    actor: ActorDep,
    evidence_repo: EvidenceRepoDep,
    storage_service: StorageServiceDep,
    case_id: str = Form(...),
    evidence_type: EvidenceType = Form(...),
    description: str = Form(...),
    file: UploadFile = File(...)
) -> dict:
    from app.config import get_settings
    settings = get_settings()

    content = await file.read()
    if len(content) > settings.evidence_max_file_size_mb * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File exceeds maximum size of {settings.evidence_max_file_size_mb} MB.",
        )
    if not content:
        raise HTTPException(status_code=400, detail="Empty file upload.")

    # 1. Upload to Catalyst Stratus Object Storage
    try:
        storage_meta = await storage_service.upload_evidence(content, file.filename or "unknown", case_id)
    except Exception as e:
        logger.error(f"Stratus upload failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to upload file to storage.")

    # 2. Save metadata to Catalyst Data Store
    ev = EvidenceItem(
        case_id=uuid.UUID(case_id),
        evidence_type=evidence_type,
        status=EvidenceStatus.COLLECTED,
        description=description,
        collected_by=actor,
        original_filename=file.filename,
        object_name=storage_meta["object_name"],
        bucket_name=storage_meta["bucket_name"],
        sha256_hash=storage_meta["sha256_hash"],
        file_size_bytes=storage_meta["file_size_bytes"],
        mime_type=file.content_type,
        upload_status=storage_meta["upload_status"],
        upload_time=storage_meta["upload_time"],
        file_reference=storage_meta["catalyst_file_id"]
    )
    
    try:
        created_ev = await evidence_repo.create(ev)
        return {"message": "Evidence uploaded successfully", "evidence_id": str(created_ev.id)}
    except Exception as e:
        # Rollback Stratus upload if DB insertion fails
        logger.error(f"Failed to save evidence metadata, rolling back Stratus upload: {e}")
        await storage_service.delete_evidence(storage_meta["catalyst_file_id"])
        raise HTTPException(status_code=500, detail="Failed to save evidence metadata. Upload rolled back.")

@router.get("/{id}", summary="Get evidence details")
async def get_evidence(id: str, evidence_repo: EvidenceRepoDep) -> dict:
    ev = await evidence_repo.get(id)
    if not ev:
        raise HTTPException(status_code=404, detail="Evidence not found.")
    
    return ev.model_dump(mode="json")

@router.get("/{id}/download-url", summary="Generate a time-limited download URL")
async def get_download_url(id: str, actor: ActorDep, evidence_repo: EvidenceRepoDep, storage_service: StorageServiceDep) -> dict:
    ev = await evidence_repo.get(id)
    if not ev or not ev.file_reference:
        raise HTTPException(status_code=404, detail="Evidence or file not found.")
        
    token = storage_service.generate_download_token(id, ev.file_reference, actor)
    return {"download_url": f"/evidence/{id}/download?token={token}"}

@router.get("/{id}/download", summary="Download evidence file from Catalyst Stratus")
async def download_evidence_file(id: str, token: str, evidence_repo: EvidenceRepoDep, storage_service: StorageServiceDep):
    # Verify token
    payload = storage_service.verify_download_token(token, id)
    
    ev = await evidence_repo.get(id)
    if not ev or not ev.file_reference:
        raise HTTPException(status_code=404, detail="Evidence or file not found.")
        
    try:
        content = await storage_service.download_evidence(ev.file_reference)
        return StreamingResponse(
            io.BytesIO(content),
            media_type=ev.mime_type or "application/octet-stream",
            headers={"Content-Disposition": f'attachment; filename="{ev.original_filename or "evidence.bin"}"'}
        )
    except Exception as e:
        logger.error(f"Failed to download evidence {id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to download file.")

@router.delete("/{id}", summary="Delete evidence from Storage and Data Store")
async def delete_evidence(id: str, evidence_repo: EvidenceRepoDep, storage_service: StorageServiceDep):
    ev = await evidence_repo.get(id)
    if not ev:
        raise HTTPException(status_code=404, detail="Evidence not found.")
        
    if ev.file_reference:
        # Delete from Stratus Object Storage
        await storage_service.delete_evidence(ev.file_reference)
        
    # Delete from Data Store
    success = await evidence_repo.delete(id)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete evidence metadata.")
        
    return {"message": "Evidence deleted successfully."}
