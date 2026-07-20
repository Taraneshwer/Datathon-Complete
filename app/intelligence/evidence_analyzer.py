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
from pathlib import Path
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
        self._ocr_reader: Any = None        # EasyOCR reader (lazy-loaded)
        self._whisper_model: Any = None     # Whisper model (lazy-loaded)

    async def analyze(
        self,
        evidence_id: str,
        evidence_type: EvidenceType,
        file_path: str,
    ) -> EvidenceAnalysisResult:
        """
        Dispatch evidence to the correct AI analysis pipeline.

        Args:
            evidence_id:    DB ID of the EvidenceItem.
            evidence_type:  Enum type determining the pipeline.
            file_path:      Absolute path to the uploaded file.

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
                result = await self._analyze_image(evidence_id, evidence_type, file_path)
            elif evidence_type == EvidenceType.AUDIO:
                result = await self._analyze_audio(evidence_id, evidence_type, file_path)
            elif evidence_type == EvidenceType.VIDEO:
                result = await self._analyze_video(evidence_id, evidence_type, file_path)
            elif evidence_type in (EvidenceType.DOCUMENT, EvidenceType.PHYSICAL):
                result = await self._analyze_document(evidence_id, evidence_type, file_path)
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
        self, evidence_id: str, ev_type: EvidenceType, file_path: str
    ) -> EvidenceAnalysisResult:
        detected_objects, face_count = await asyncio.to_thread(
            self._run_image_pipeline, file_path
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
        self, evidence_id: str, ev_type: EvidenceType, file_path: str
    ) -> EvidenceAnalysisResult:
        transcription = await asyncio.to_thread(
            self._run_whisper, file_path
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
        self, evidence_id: str, ev_type: EvidenceType, file_path: str
    ) -> EvidenceAnalysisResult:
        """Sample frames and run image pipeline on each."""
        detected_objects, face_count = await asyncio.to_thread(
            self._run_video_pipeline, file_path
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
        self, evidence_id: str, ev_type: EvidenceType, file_path: str
    ) -> EvidenceAnalysisResult:
        ocr_text = await asyncio.to_thread(self._run_ocr, file_path)
        return EvidenceAnalysisResult(
            evidence_id=evidence_id,
            evidence_type=ev_type,
            ocr_text=ocr_text,
            summary=f"Document OCR extracted {len(ocr_text)} characters of text.",
            confidence=0.90 if ocr_text else 0.3,
        )

    # ── Synchronous ML runners (thread pool) ──────────────────────────────────

    def _run_image_pipeline(self, file_path: str) -> tuple[list[str], int]:
        """OpenCV face detection + YOLO object detection."""
        try:
            import cv2
            img = cv2.imread(file_path)
            if img is None:
                return [], 0

            # Face detection using Haar cascade
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            face_cascade = cv2.CascadeClassifier(
                cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
            )
            faces = face_cascade.detectMultiScale(gray, 1.1, 4)
            face_count = len(faces)

            # YOLO object detection (stub — returns simulated labels in dev)
            detected_objects = self._run_yolo_detection(file_path)

            return detected_objects, face_count
        except Exception as exc:
            logger.warning("Image pipeline error: %s", exc)
            return [], 0

    def _run_yolo_detection(self, file_path: str) -> list[str]:
        """
        YOLOv11 object detection.
        In production: load the YOLO model once at startup and run inference.
        Stub returns empty list (no model file in dev).
        """
        # Production integration:
        # from ultralytics import YOLO
        # model = YOLO("yolo11n.pt")
        # results = model(file_path, conf=self._settings.yolo_confidence_threshold)
        # return list({name for r in results for name in r.names.values()})
        logger.debug("YOLO detection stub — load model for production use.")
        return []

    def _run_whisper(self, file_path: str) -> str:
        """OpenAI Whisper speech-to-text transcription."""
        try:
            import whisper
            if self._whisper_model is None:
                self._whisper_model = whisper.load_model(
                    self._settings.whisper_model_size
                )
            result = self._whisper_model.transcribe(file_path)
            return result.get("text", "")
        except Exception as exc:
            logger.warning("Whisper transcription failed: %s", exc)
            return ""

    def _run_ocr(self, file_path: str) -> str:
        """EasyOCR multi-language text extraction."""
        try:
            import easyocr
            if self._ocr_reader is None:
                self._ocr_reader = easyocr.Reader(
                    self._settings.ocr_languages, gpu=False
                )
            results = self._ocr_reader.readtext(file_path)
            return " ".join(text for _, text, confidence in results if confidence > 0.4)
        except Exception as exc:
            logger.warning("OCR failed: %s", exc)
            return ""

    def _run_video_pipeline(self, file_path: str) -> tuple[list[str], int]:
        """Sample every 30th frame and run image analysis."""
        try:
            import cv2
            cap = cv2.VideoCapture(file_path)
            all_objects: set[str] = set()
            total_faces = 0
            frame_idx = 0

            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break
                if frame_idx % 30 == 0:
                    tmp = f"/tmp/frame_{frame_idx}.jpg"
                    cv2.imwrite(tmp, frame)
                    objs, faces = self._run_image_pipeline(tmp)
                    all_objects.update(objs)
                    total_faces = max(total_faces, faces)
                frame_idx += 1

            cap.release()
            return list(all_objects), total_faces
        except Exception as exc:
            logger.warning("Video pipeline failed: %s", exc)
            return [], 0
