"""
app/routers/ingest.py
─────────────────────────────────────────────────────────────────────────────
FIR ingestion router.

Endpoints:
  POST /api/v1/ingest              — ingest a new FIR + evidence + graph entities
  POST /api/v1/ingest/match        — find similar cases (pattern matching)
  POST /api/v1/ingest/hotspots     — predict geographic crime hotspots
─────────────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException, Request, status

from app.dependencies import (
    ActorDep,
    ClientIPDep,
    HotspotPredictorDep,
    IngestServiceDep,
    PatternMatcherDep,
)
from app.models.schemas import (
    FIRIngestRequest,
    HotspotRequest,
    HotspotResponse,
    IngestResponse,
    PatternMatchResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/ingest",
    tags=["Ingestion"],
)


# ─────────────────────────────────────────────────────────────────────────────
# POST /ingest  — FIR Ingestion
# ─────────────────────────────────────────────────────────────────────────────

@router.post(
    "",
    response_model=IngestResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Ingest a new FIR with evidence and graph entities",
    response_description="Confirmation with IDs for all three storage backends.",
)
async def ingest_fir(
    payload: FIRIngestRequest,
    service: IngestServiceDep,
    actor: ActorDep,
    client_ip: ClientIPDep,
) -> IngestResponse:
    """
    Ingest a First Information Report (FIR) into the crime intelligence system.

    This endpoint concurrently:
    - Stores core case details in **PostgreSQL**
    - Writes entity nodes and relationships to **Neo4j**
    - Embeds the crime description and upserts into **Qdrant**

    Returns identifiers for all three backend records.
    """
    logger.info(
        "Ingest request | fir=%s actor=%s ip=%s",
        payload.fir_number,
        actor,
        client_ip,
    )
    try:
        result = await service.ingest(
            payload=payload,
            actor=actor,
            ip_address=client_ip,
        )
    except ValueError as exc:
        # Business logic errors (e.g., duplicate FIR)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc
    except RuntimeError as exc:
        # Database write failures
        logger.error("Ingest failed: %s", exc, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Ingestion failed due to a storage error: {exc}",
        ) from exc

    return result


# ─────────────────────────────────────────────────────────────────────────────
# POST /ingest/match  — Pattern Matching
# ─────────────────────────────────────────────────────────────────────────────

@router.post(
    "/match",
    response_model=PatternMatchResponse,
    status_code=status.HTTP_200_OK,
    summary="Find historically similar crime cases",
    response_description="Ranked list of similar cases with cosine similarity scores.",
)
async def find_similar_cases(
    request: Request,
    matcher: PatternMatcherDep,
    query_text: str,
    top_k: int = 5,
) -> PatternMatchResponse:
    """
    Embed `query_text` and return the top-K most similar historical cases
    from Qdrant based on cosine similarity.
    """
    if not query_text.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="query_text must not be empty.",
        )
    try:
        return await matcher.find_similar(text=query_text, top_k=top_k)
    except RuntimeError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc


# ─────────────────────────────────────────────────────────────────────────────
# POST /ingest/hotspots  — Geographic Hotspot Prediction
# ─────────────────────────────────────────────────────────────────────────────

@router.post(
    "/hotspots",
    response_model=HotspotResponse,
    status_code=status.HTTP_200_OK,
    summary="Predict geographic crime hotspots using DBSCAN clustering",
    response_description="Cluster centroids, member counts, and noise point count.",
)
async def predict_hotspots(
    payload: HotspotRequest,
    predictor: HotspotPredictorDep,
) -> HotspotResponse:
    """
    Run DBSCAN geo-clustering on the provided coordinates.
    Returns cluster centroids and member point indices.
    Requires at least 3 coordinate points.
    """
    try:
        return await predictor.predict(payload.coordinates)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc
    except Exception as exc:
        logger.error("Hotspot prediction failed: %s", exc, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Hotspot prediction encountered an internal error.",
        ) from exc
