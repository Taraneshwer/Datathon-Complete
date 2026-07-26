import logging
import base64
import re
from app.config import get_settings

logger = logging.getLogger(__name__)

_groq_client = None

def run_ocr(file_path: str, languages: list[str] = ["en"]) -> str:
    """Groq Qwen Vision multi-language text extraction."""
    global _groq_client
    try:
        from groq import Groq
        settings = get_settings()
        
        if not settings.groq_api_key:
            logger.warning("GROQ_API_KEY is not set. OCR cannot proceed.")
            return ""

        if _groq_client is None:
            _groq_client = Groq(api_key=settings.groq_api_key)
            
        with open(file_path, "rb") as image_file:
            img_b64 = base64.b64encode(image_file.read()).decode()
            
        lang_str = ", ".join(languages)
        prompt = f"Extract the text from this image. Output only the text. Ensure it is accurate for these languages: {lang_str}."

        response = _groq_client.chat.completions.create(
            model="qwen/qwen3.6-27b",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}}
                    ]
                }
            ],
            temperature=0.1
        )
        
        text = response.choices[0].message.content or ""
        
        # Remove reasoning tags if any
        text = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL).strip()
        
        return text
    except Exception as exc:
        logger.warning("Groq OCR failed: %s", exc)
        return ""
