"""
ai_service/ocr/engine.py
─────────────────────────────────────────────────────────────────────────────
100% Zoho Catalyst-Native OCR Engine.
Replaces third-party Vision OCR (Groq / EasyOCR / Tesseract) with native
Zoho Catalyst Zia OCR & Document Analysis service.
─────────────────────────────────────────────────────────────────────────────
"""
import io
import logging
from typing import Any, List
from app.db.catalyst import CatalystDBClient

logger = logging.getLogger(__name__)

def _get_stream(file_data: Any):
    if isinstance(file_data, bytes):
        return io.BytesIO(file_data), None
    elif isinstance(file_data, str):
        f = open(file_data, "rb")
        return f, f
    elif hasattr(file_data, "read"):
        return file_data, None
    raise ValueError("Unsupported file data type")

def run_ocr(file_data: Any, languages: List[str] = ["en"]) -> str:
    """100% Catalyst Zia OCR text extraction from images or PDF documents."""
    db = CatalystDBClient()
    stream, file_handle = None, None
    try:
        zia = db.get_zia_service()
        stream, file_handle = _get_stream(file_data)
        # Call Catalyst Zia OCR service
        result = zia.extract_optical_character_recognition(stream, language="ENG")
        if isinstance(result, dict):
            return str(result.get("text", result.get("content", ""))).strip()
        return str(result).strip()
    except Exception as exc:
        logger.warning("Catalyst Zia OCR extraction failed: %s", exc)
        return ""
    finally:
        if file_handle and hasattr(file_handle, "close"):
            file_handle.close()
