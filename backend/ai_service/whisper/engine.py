"""
ai_service/whisper/engine.py
─────────────────────────────────────────────────────────────────────────────
100% Zoho Catalyst-Native Speech-to-Text Transcription Engine.
Replaces Groq Whisper / local OpenAI Whisper models with native
Zoho Catalyst Zia Speech-to-Text Service.
─────────────────────────────────────────────────────────────────────────────
"""
import io
import logging
from typing import Any
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

def run_whisper(file_data: Any, model_size: str = "base") -> str:
    """100% Catalyst Zia Speech-to-Text audio transcription."""
    db = CatalystDBClient()
    stream, file_handle = None, None
    try:
        zia = db.get_zia_service()
        stream, file_handle = _get_stream(file_data)
        # Call Catalyst Zia Speech-to-Text
        result = zia.transcribe_audio(stream, language="en-US")
        if isinstance(result, dict):
            return str(result.get("text", result.get("transcript", ""))).strip()
        return str(result).strip()
    except Exception as exc:
        logger.warning("Catalyst Zia Speech transcription failed: %s", exc)
        return ""
    finally:
        if file_handle and hasattr(file_handle, "close"):
            file_handle.close()
