"""
app/assistant/rag_graph.py
─────────────────────────────────────────────────────────────────────────────
LangGraph StateGraph RAG workflow for the crime intelligence assistant.

Pipeline (nodes in execution order):
  1. sanitize_query     — firewall check + text cleaning
  2. retrieve_vectors   — Qdrant semantic search
  3. fetch_graph_context — Neo4j relational path extraction
  4. assemble_prompt    — merge all context into final prompt
  5. llm_call           — call configured LLM provider
  6. format_output      — structure the ChatResponse

State flows through a TypedDict; each node receives and returns the full state.
The graph is compiled once at startup and reused for all requests.
─────────────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import logging
import time
from typing import Any, TypedDict

from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import END, StateGraph

from app.assistant.prompt_templates import SYSTEM_PROMPT, build_rag_prompt
from app.config import get_settings
from app.db.neo4j_client import get_driver
from app.db.qdrant_client import get_client
from app.intelligence.firewall import check_or_raise
from app.models.schemas import ChatRequest, ChatResponse, SourceDocument
from app.services.embedding_service import get_embedding_service
from app.services.graph_service import GraphService

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# Typed State
# ─────────────────────────────────────────────────────────────────────────────

class RAGState(TypedDict, total=False):
    # Input
    query: str
    case_context_id: str | None
    top_k: int

    # Intermediate
    sanitized_query: str
    vector_sources: list[dict[str, Any]]
    graph_paths: list[str]
    assembled_prompt: str

    # Output
    answer: str
    sources: list[dict[str, Any]]
    error: str | None
    start_time: float


# ─────────────────────────────────────────────────────────────────────────────
# Node functions
# ─────────────────────────────────────────────────────────────────────────────

def _sanitize_query(state: RAGState) -> RAGState:
    """Node 1 — firewall check and query cleaning."""
    query = state["query"]
    try:
        sanitized = check_or_raise(query, field_name="chat_query")
    except ValueError as exc:
        return {**state, "error": str(exc), "sanitized_query": ""}
    return {**state, "sanitized_query": sanitized.strip(), "error": None}


async def _retrieve_vectors(state: RAGState) -> RAGState:
    """Node 2 — semantic vector retrieval from Qdrant."""
    if state.get("error"):
        return state

    query = state["sanitized_query"]
    top_k = state.get("top_k", 5)
    settings = get_settings()

    try:
        embedder = get_embedding_service()
        vector = await embedder.embed(query)

        qdrant = get_client()
        hits = await qdrant.search(
            collection_name=settings.qdrant_collection,
            query_vector=vector,
            limit=top_k,
            score_threshold=settings.pattern_match_score_threshold,
            with_payload=True,
            with_vectors=False,
        )

        sources = []
        for hit in hits:
            payload = hit.payload or {}
            sources.append({
                "case_id": str(payload.get("case_id", hit.id)),
                "fir_number": str(payload.get("fir_number", "UNKNOWN")),
                "title": payload.get("title", ""),
                "description": payload.get("description", "")[:300],
                "severity": payload.get("severity", ""),
                "status": payload.get("status", ""),
                "score": round(float(hit.score), 4),
            })

        return {**state, "vector_sources": sources}

    except Exception as exc:
        logger.error("RAG: vector retrieval failed — %s", exc, exc_info=True)
        return {**state, "vector_sources": [], "error": f"Vector retrieval error: {exc}"}


async def _fetch_graph_context(state: RAGState) -> RAGState:
    """Node 3 — graph relationship extraction from Neo4j."""
    if state.get("error"):
        return state

    sources = state.get("vector_sources", [])
    case_id = state.get("case_context_id")
    graph_service = GraphService(get_driver())
    all_paths: list[str] = []

    try:
        # If a specific case_id is requested, pull its graph context directly
        if case_id:
            paths = await graph_service.get_case_context(case_id, depth=2)
            all_paths.extend(paths)

        # Additionally pull graph for top vector results
        seen_firs: set[str] = {case_id} if case_id else set()
        for src in sources[:3]:  # Limit to top-3 to control query volume
            fir = src.get("fir_number", "")
            if fir and fir not in seen_firs:
                paths = await graph_service.get_case_context(fir, depth=2)
                all_paths.extend(paths)
                seen_firs.add(fir)

    except Exception as exc:
        logger.warning("RAG: graph context fetch failed (non-fatal) — %s", exc)
        # Non-fatal: proceed without graph context

    return {**state, "graph_paths": all_paths}


def _assemble_prompt(state: RAGState) -> RAGState:
    """Node 4 — merge all context into the final RAG prompt."""
    if state.get("error"):
        return state

    prompt = build_rag_prompt(
        user_query=state["sanitized_query"],
        vector_sources=state.get("vector_sources", []),
        graph_paths=state.get("graph_paths", []),
    )
    return {**state, "assembled_prompt": prompt}


async def _llm_call(state: RAGState) -> RAGState:
    """Node 5 — invoke the configured LLM provider."""
    if state.get("error"):
        return state

    settings = get_settings()
    prompt_text = state["assembled_prompt"]

    try:
        llm = _get_llm(settings)
        messages = [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=prompt_text),
        ]
        response = await llm.ainvoke(messages)
        answer = response.content if hasattr(response, "content") else str(response)
        return {**state, "answer": answer}

    except Exception as exc:
        logger.error("RAG: LLM call failed — %s", exc, exc_info=True)
        return {
            **state,
            "answer": "The intelligence assistant encountered an error processing your query.",
            "error": str(exc),
        }


def _format_output(state: RAGState) -> RAGState:
    """Node 6 — final state cleanup (no-op transformer, kept for extensibility)."""
    return state


# ─────────────────────────────────────────────────────────────────────────────
# LLM factory
# ─────────────────────────────────────────────────────────────────────────────

def _get_llm(settings: Any) -> Any:
    """Instantiate the correct LangChain LLM based on configured provider."""
    if settings.llm_provider == "openai":
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            model=settings.openai_model,
            api_key=settings.openai_api_key,
            temperature=0.1,
            max_tokens=2048,
        )
    elif settings.llm_provider == "google":
        from langchain_google_genai import ChatGoogleGenerativeAI  # type: ignore[import]
        return ChatGoogleGenerativeAI(
            model=settings.google_model,
            google_api_key=settings.google_api_key,
            temperature=0.1,
        )
    elif settings.llm_provider == "ollama":
        from langchain_community.chat_models import ChatOllama
        return ChatOllama(
            model=settings.ollama_model,
            base_url=settings.ollama_base_url,
            temperature=0.1,
        )
    elif settings.llm_provider == "nvidia":
        from langchain_nvidia_ai_endpoints import ChatNVIDIA
        return ChatNVIDIA(
            model=settings.nvidia_model,
            api_key=settings.nvidia_api_key,
            temperature=0.1,
            max_tokens=2048,
        )
    else:
        raise ValueError(f"Unknown LLM provider: {settings.llm_provider}")


# ─────────────────────────────────────────────────────────────────────────────
# Graph compilation
# ─────────────────────────────────────────────────────────────────────────────

def _build_rag_graph() -> Any:
    """Build and compile the LangGraph StateGraph."""
    workflow = StateGraph(RAGState)

    # Register nodes
    workflow.add_node("sanitize_query", _sanitize_query)
    workflow.add_node("retrieve_vectors", _retrieve_vectors)
    workflow.add_node("fetch_graph_context", _fetch_graph_context)
    workflow.add_node("assemble_prompt", _assemble_prompt)
    workflow.add_node("llm_call", _llm_call)
    workflow.add_node("format_output", _format_output)

    # Define edges (sequential pipeline)
    workflow.set_entry_point("sanitize_query")
    workflow.add_edge("sanitize_query", "retrieve_vectors")
    workflow.add_edge("retrieve_vectors", "fetch_graph_context")
    workflow.add_edge("fetch_graph_context", "assemble_prompt")
    workflow.add_edge("assemble_prompt", "llm_call")
    workflow.add_edge("llm_call", "format_output")
    workflow.add_edge("format_output", END)

    return workflow.compile()


# Compiled graph singleton — built once at module import time
_rag_graph = _build_rag_graph()


# ─────────────────────────────────────────────────────────────────────────────
# Public interface
# ─────────────────────────────────────────────────────────────────────────────

async def run_rag(request: ChatRequest) -> ChatResponse:
    """
    Execute the full RAG pipeline for a chat request.
    This is the sole public entry point called by the assistant router.
    """
    start_time = time.monotonic()

    initial_state: RAGState = {
        "query": request.query,
        "case_context_id": str(request.case_context_id) if request.case_context_id else None,
        "top_k": request.top_k,
        "start_time": start_time,
        "vector_sources": [],
        "graph_paths": [],
    }

    final_state: RAGState = await _rag_graph.ainvoke(initial_state)

    elapsed_ms = (time.monotonic() - start_time) * 1000

    # Build SourceDocument list from vector hits
    raw_sources = final_state.get("vector_sources", [])
    source_docs = [
        SourceDocument(
            case_id=src["case_id"],
            fir_number=src["fir_number"],
            similarity_score=src["score"],
            excerpt=src.get("description", ""),
        )
        for src in raw_sources
    ]

    return ChatResponse(
        query=request.query,
        answer=final_state.get("answer", "No answer generated."),
        sources=source_docs,
        graph_paths=final_state.get("graph_paths", []),
        processing_time_ms=round(elapsed_ms, 2),
    )
