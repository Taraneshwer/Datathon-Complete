import logging

logger = logging.getLogger(__name__)

_ocr_reader = None

def run_ocr(file_path: str, languages: list[str] = ["en"]) -> str:
    """EasyOCR multi-language text extraction."""
    global _ocr_reader
    try:
        import easyocr
        if _ocr_reader is None:
            _ocr_reader = easyocr.Reader(languages, gpu=False)
        results = _ocr_reader.readtext(file_path)
        return " ".join(text for _, text, confidence in results if confidence > 0.4)
    except Exception as exc:
        logger.warning("OCR failed: %s", exc)
        return ""
