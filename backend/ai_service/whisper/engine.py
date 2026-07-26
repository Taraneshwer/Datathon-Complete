import logging
import os
from app.config import get_settings

logger = logging.getLogger(__name__)

_groq_client = None

def run_whisper(file_path: str, model_size: str = "base") -> str:
    """Groq Whisper speech-to-text transcription."""
    global _groq_client
    try:
        from groq import Groq
        settings = get_settings()
        
        if not settings.groq_api_key:
            logger.warning("GROQ_API_KEY is not set. Audio transcription cannot proceed.")
            return ""

        if _groq_client is None:
            _groq_client = Groq(api_key=settings.groq_api_key)
            
        with open(file_path, "rb") as audio_file:
            transcription = _groq_client.audio.transcriptions.create(
                file=(os.path.basename(file_path), audio_file.read()),
                model="whisper-large-v3",
            )
            
        return transcription.text
    except Exception as exc:
        logger.warning("Groq Whisper transcription failed: %s", exc)
        return ""
