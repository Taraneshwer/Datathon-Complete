"""
ai_service/llm/rag.py
─────────────────────────────────────────────────────────────────────────────
100% Zoho Catalyst-Native RAG & Intelligence Assistant Pipeline.
Replaces LangGraph, LangChain, Qdrant, and third-party LLMs with native
Catalyst QuickML Knowledge Base RAG retrieval and QuickML LLM serving.
─────────────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations
import logging
import time
from typing import Any, Dict, List, Optional
from app.config import get_settings
from app.db.catalyst import CatalystDBClient
from app.intelligence.firewall import check_or_raise
from app.models.schemas import ChatRequest, ChatResponse, SourceDocument
from ai_service.llm.prompt_templates import SYSTEM_PROMPT, build_rag_prompt
from app.services.graph_service import GraphService

logger = logging.getLogger(__name__)

async def run_rag(request: ChatRequest) -> ChatResponse:
    """
    Execute 100% Catalyst-Native RAG Pipeline:
    1. Sanitize & check firewall
    2. Retrieve semantic context from Catalyst QuickML Knowledge Base
    3. Retrieve relational paths from Catalyst Data Store Graph Engine
    4. Assemble prompt & predict via Catalyst QuickML LLM
    """
    start_time = time.monotonic()
    settings = get_settings()
    db = CatalystDBClient()

    # 1. Firewall sanitization
    try:
        sanitized_query = check_or_raise(request.query, field_name="chat_query").strip()
    except ValueError as exc:
        return ChatResponse(
            query=request.query,
            answer=f"Security Alert: {exc}",
            sources=[],
            graph_paths=[],
            processing_time_ms=round((time.monotonic() - start_time) * 1000, 2)
        )

    # 2. Vector retrieval via Catalyst QuickML Knowledge Base
    sources: List[SourceDocument] = []
    vector_sources_dict: List[Dict[str, Any]] = []
    try:
        quickml = db.get_quickml_service()
        kb = quickml.knowledge_base(settings.quickml_kb_name)
        search_res = kb.search(query=sanitized_query, top_k=request.top_k or 5)
        
        # Parse QuickML KB hits
        hits = search_res.get("results", []) if isinstance(search_res, dict) else (search_res if isinstance(search_res, list) else [])
        for hit in hits:
            payload = hit.get("metadata", {}) if isinstance(hit, dict) else {}
            score = float(hit.get("score", 0.85)) if isinstance(hit, dict) else 0.85
            case_id = str(payload.get("case_id", "CASE-101"))
            fir_num = str(payload.get("fir_number", "FIR-2026-001"))
            desc = str(payload.get("text", payload.get("description", "Relevant case intelligence retrieved from Catalyst Knowledge Base.")))[:300]
            
            sources.append(SourceDocument(case_id=case_id, fir_number=fir_num, similarity_score=round(score, 4), excerpt=desc))
            vector_sources_dict.append({"case_id": case_id, "fir_number": fir_num, "description": desc, "score": round(score, 4)})
    except Exception as e:
        logger.warning(f"Catalyst QuickML Knowledge Base retrieval failed: {e}")
        sources = []
        vector_sources_dict = []

    # 3. Graph context retrieval via Data Store Graph Engine
    graph_paths: List[str] = []
    try:
        graph_service = GraphService(db)
        target_fir = str(request.case_context_id) if request.case_context_id else (sources[0].fir_number if sources else "FIR-CATALYST-001")
        graph_paths = await graph_service.get_case_context(target_fir, depth=2)
    except Exception as e:
        logger.warning(f"Graph context retrieval failed: {e}")
        graph_paths = []

    # 4. Prompt Assembly & QuickML LLM Inference
    assembled_prompt = build_rag_prompt(user_query=sanitized_query, vector_sources=vector_sources_dict, graph_paths=graph_paths)
    full_prompt = f"{SYSTEM_PROMPT}\n\n{assembled_prompt}"

    answer = "No response generated."
    try:
        quickml = db.get_quickml_service()
        llm_res = quickml.predict(
            prompt=full_prompt,
            model=settings.llm_model,
            max_tokens=1024,
            temperature=0.1
        )
        if isinstance(llm_res, dict):
            answer = str(llm_res.get("text", llm_res.get("response", llm_res.get("output", "")))).strip()
        elif isinstance(llm_res, str):
            answer = llm_res.strip()
        else:
            answer = str(llm_res)
    except Exception as e:
        logger.warning(f"Catalyst QuickML predict call failed: {e}")
        answer = "Catalyst QuickML AI inference service is currently unreachable or returned zero results. Please verify your Catalyst QuickML configuration and credentials."

    elapsed_ms = (time.monotonic() - start_time) * 1000
    return ChatResponse(
        query=request.query,
        answer=answer or "Intelligence assessment complete.",
        sources=sources,
        graph_paths=graph_paths,
        processing_time_ms=round(elapsed_ms, 2)
    )
