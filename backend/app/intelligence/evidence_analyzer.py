"""
app/intelligence/evidence_analyzer.py
─────────────────────────────────────────────────────────────────────────────
Evidence Intelligence Engine.

AI-powered analysis pipeline for uploaded evidence files:
  - Images:    Object detection (YOLO stub) + face detection (OpenCV)
  - Documents/PDFs: OCR via EasyOCR
  - Audio:     Speech-to-text via OpenAI Whisper
  - Video:     Frame sampling + object detection

All heavy ML operations run in asyncio.to_thread() to avoid event loop blocking.
─────────────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import asyncio
import logging
from typing import Any

from app.config import get_settings
from app.models.fir import EvidenceType
from app.models.schemas import EvidenceAnalysisResult

logger = logging.getLogger(__name__)


class EvidenceAnalyzer:
    """
    AI evidence analysis pipeline.
    Routes files to the appropriate analysis sub-pipeline based on evidence type.
    """

    def __init__(self) -> None:
        self._settings = get_settings()

    async def analyze(
        self,
        evidence_id: str,
        evidence_type: EvidenceType,
        file_data: Any,
    ) -> EvidenceAnalysisResult:
        """
        Dispatch evidence to the correct AI analysis pipeline.

        Args:
            evidence_id:    DB ID of the EvidenceItem.
            evidence_type:  Enum type determining the pipeline.
            file_data:      In-memory file bytes or reference.

        Returns:
            EvidenceAnalysisResult with all extracted intelligence.
        """
        import time
        start = time.monotonic()

        result = EvidenceAnalysisResult(
            evidence_id=evidence_id,
            evidence_type=evidence_type,
        )

        try:
            if evidence_type in (EvidenceType.IMAGE, EvidenceType.SURVEILLANCE):
                result = await self._analyze_image(evidence_id, evidence_type, file_data)
            elif evidence_type == EvidenceType.AUDIO:
                result = await self._analyze_audio(evidence_id, evidence_type, file_data)
            elif evidence_type == EvidenceType.VIDEO:
                result = await self._analyze_video(evidence_id, evidence_type, file_data)
            elif evidence_type in (EvidenceType.DOCUMENT, EvidenceType.PHYSICAL):
                result = await self._analyze_document(evidence_id, evidence_type, file_data)
            else:
                result.summary = "No automated analysis available for this evidence type."

        except Exception as exc:
            logger.error(
                "EvidenceAnalyzer: failed for %s — %s", evidence_id, exc, exc_info=True
            )
            result.summary = f"Analysis failed: {exc}"
            result.confidence = 0.0

        result.processing_time_ms = round((time.monotonic() - start) * 1000, 2)
        return result

    # ── Image Analysis ────────────────────────────────────────────────────────

    async def _analyze_image(
        self, evidence_id: str, ev_type: EvidenceType, file_data: Any
    ) -> EvidenceAnalysisResult:
        from ai_service.vision.pipeline import run_image_pipeline
        detected_objects, face_count = await asyncio.to_thread(
            run_image_pipeline, file_data
        )
        summary_parts = []
        if face_count > 0:
            summary_parts.append(f"{face_count} face(s) detected.")
        if detected_objects:
            summary_parts.append(f"Objects: {', '.join(detected_objects[:10])}.")

        return EvidenceAnalysisResult(
            evidence_id=evidence_id,
            evidence_type=ev_type,
            detected_faces=face_count,
            detected_objects=detected_objects,
            summary=" ".join(summary_parts) or "No significant objects detected.",
            confidence=0.82 if detected_objects or face_count > 0 else 0.4,
        )

    # ── Audio Analysis ────────────────────────────────────────────────────────

    async def _analyze_audio(
        self, evidence_id: str, ev_type: EvidenceType, file_data: Any
    ) -> EvidenceAnalysisResult:
        from ai_service.whisper.engine import run_whisper
        transcription = await asyncio.to_thread(
            run_whisper, file_data, getattr(self._settings, "whisper_model_size", "base")
        )
        return EvidenceAnalysisResult(
            evidence_id=evidence_id,
            evidence_type=ev_type,
            transcription=transcription,
            summary=f"Audio transcribed ({len(transcription)} chars).",
            confidence=0.88 if transcription else 0.2,
        )

    # ── Video Analysis ────────────────────────────────────────────────────────

    async def _analyze_video(
        self, evidence_id: str, ev_type: EvidenceType, file_data: Any
    ) -> EvidenceAnalysisResult:
        """Analyze video frames using image pipeline."""
        from ai_service.vision.pipeline import run_video_pipeline
        detected_objects, face_count = await asyncio.to_thread(
            run_video_pipeline, file_data
        )
        return EvidenceAnalysisResult(
            evidence_id=evidence_id,
            evidence_type=ev_type,
            detected_faces=face_count,
            detected_objects=detected_objects,
            summary=(
                f"Video analysis: {face_count} face(s), "
                f"{len(detected_objects)} unique object types detected."
            ),
            confidence=0.75,
        )

    # ── Document / OCR Analysis ───────────────────────────────────────────────

    async def _analyze_document(
        self, evidence_id: str, ev_type: EvidenceType, file_data: Any
    ) -> EvidenceAnalysisResult:
        from ai_service.ocr.engine import run_ocr
        ocr_text = await asyncio.to_thread(run_ocr, file_data, getattr(self._settings, "ocr_languages", ["en"]))
        return EvidenceAnalysisResult(
            evidence_id=evidence_id,
            evidence_type=ev_type,
            ocr_text=ocr_text,
            summary=f"Document OCR extracted {len(ocr_text)} characters of text.",
            confidence=0.90 if ocr_text else 0.3,
        )


