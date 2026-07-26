"""
app/routers/assistant.py
─────────────────────────────────────────────────────────────────────────────
AI assistant router.

Endpoints:
  POST /api/v1/assistant/chat    — RAG-powered crime intelligence Q&A
  GET  /api/v1/assistant/health  — LLM provider connectivity check
─────────────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import logging
import time

from fastapi import APIRouter, HTTPException, status

from app.config import get_settings
from app.models.schemas import ChatRequest, ChatResponse

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/assistant",
    tags=["AI Assistant"],
)


# ─────────────────────────────────────────────────────────────────────────────
# POST /assistant/chat  — RAG Chat
# ─────────────────────────────────────────────────────────────────────────────

@router.post(
    "/chat",
    response_model=ChatResponse,
    status_code=status.HTTP_200_OK,
    summary="Submit a natural-language query to the crime intelligence assistant",
    response_description=(
        "LLM-generated answer grounded in Qdrant vector context "
        "and Neo4j graph relationships."
    ),
)
async def chat(payload: ChatRequest) -> ChatResponse:
    """
    Execute the full LangGraph RAG pipeline:

    1. **Sanitise** query through the prompt injection firewall.
    2. **Retrieve** semantically similar cases from Qdrant.
    3. **Fetch** entity graph paths from Neo4j.
    4. **Assemble** grounded prompt with system instructions.
    5. **Invoke** the configured LLM (OpenAI / Google / Ollama).
    6. **Return** a structured response with cited sources.
    """
    logger.info(
        "Assistant chat | query_len=%d case_scope=%s",
        len(payload.query),
        payload.case_context_id,
    )

    try:
        from ai_service.llm.rag import run_rag
        response = await run_rag(payload)
    except ValueError as exc:
        # Prompt injection detected by firewall
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    except Exception as exc:
        logger.error("Assistant chat error: %s", exc, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="The intelligence assistant encountered an internal error.",
        ) from exc

    return response


# ─────────────────────────────────────────────────────────────────────────────
# GET /assistant/health  — LLM Provider Health Check
# ─────────────────────────────────────────────────────────────────────────────

@router.get(
    "/health",
    status_code=status.HTTP_200_OK,
    summary="Check LLM provider connectivity",
)
async def assistant_health() -> dict:
    """
    Perform a lightweight connectivity check against the configured LLM provider.
    Does NOT consume meaningful tokens — uses a minimal prompt.
    """
    settings = get_settings()
    start = time.monotonic()
    status_info: dict = {
        "provider": settings.llm_provider,
        "model": getattr(settings, f"{settings.llm_provider}_model", "unknown"),
        "status": "unknown",
        "latency_ms": 0.0,
    }

    try:
        if settings.llm_provider == "openai":
            from langchain_openai import ChatOpenAI
            llm = ChatOpenAI(
                model=settings.openai_model,
                api_key=settings.openai_api_key,
                max_tokens=5,
            )
        elif settings.llm_provider == "google":
            from langchain_google_genai import ChatGoogleGenerativeAI  # type: ignore[import]
            llm = ChatGoogleGenerativeAI(
                model=settings.google_model,
                google_api_key=settings.google_api_key,
            )
        else:
            from langchain_community.chat_models import ChatOllama
            llm = ChatOllama(
                model=settings.ollama_model,
                base_url=settings.ollama_base_url,
            )

        from langchain_core.messages import HumanMessage
        await llm.ainvoke([HumanMessage(content="ping")])
        status_info["status"] = "healthy"

    except Exception as exc:
        status_info["status"] = f"degraded: {exc}"

    status_info["latency_ms"] = round((time.monotonic() - start) * 1000, 2)
    return status_info
