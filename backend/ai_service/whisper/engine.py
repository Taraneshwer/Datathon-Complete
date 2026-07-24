import logging

logger = logging.getLogger(__name__)

_whisper_model = None

def run_whisper(file_path: str, model_size: str = "base") -> str:
    """OpenAI Whisper speech-to-text transcription."""
    global _whisper_model
    try:
        from faster_whisper import WhisperModel
        if _whisper_model is None:
            _whisper_model = WhisperModel(
                model_size,
                device="cpu", 
                compute_type="int8"
            )
        segments, info = _whisper_model.transcribe(file_path)
        result_text = " ".join([segment.text for segment in segments])
        return result_text
    except Exception as exc:
        logger.warning("Whisper transcription failed: %s", exc)
        return ""
