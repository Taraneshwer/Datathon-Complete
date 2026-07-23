"""
app/main.py
─────────────────────────────────────────────────────────────────────────────
AI Crime Intelligence & Investigation Platform — FastAPI Application Factory

Startup sequence (lifespan):
  1. PostgreSQL engine + table creation
  2. Neo4j driver + schema bootstrap
  3. Qdrant client + collection bootstrap
  4. Embedding model warm-up (BGE-M3)

Middleware: CORS → GZip → PromptInjectionFirewall → Timing
─────────────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import logging
import os
import time
from contextlib import asynccontextmanager
from typing import Any

import structlog
from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

from app.config import get_settings
from app.db.neo4j_client import close_neo4j, init_neo4j
from app.db.postgres import close_engine, create_db_tables, init_engine
from app.db.qdrant_client import close_qdrant, init_qdrant
from app.intelligence.firewall import PromptInjectionFirewall
from app.models.schemas import ErrorDetail, ErrorResponse
from app.routers import (
    analytics_router,
    assistant_router,
    auth_router,
    evidence_router,
    ingest_router,
    websocket_router,
)
from app.services.embedding_service import init_embedding_service


# ─────────────────────────────────────────────────────────────────────────────
# Logging
# ─────────────────────────────────────────────────────────────────────────────

def _configure_logging(log_level: str) -> None:
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.dev.ConsoleRenderer()
            if log_level == "DEBUG"
            else structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(
            getattr(logging, log_level, logging.INFO)
        ),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
    )
    logging.basicConfig(level=getattr(logging, log_level, logging.INFO))


# ─────────────────────────────────────────────────────────────────────────────
# Lifespan
# ─────────────────────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    _configure_logging(settings.log_level)
    logger = logging.getLogger(__name__)

    banner = "=" * 65
    logger.info(banner)
    logger.info("  %s  v%s", settings.app_name, settings.app_version)
    logger.info("  Environment : %s", settings.environment)
    logger.info("  LLM Provider: %s  (%s)", settings.llm_provider,
                getattr(settings, f"{settings.llm_provider}_model", "?"))
    logger.info("  Embedding   : %s", settings.embedding_model)
    logger.info(banner)

    # ── Startup ───────────────────────────────────────────────────────────────
    logger.info("[1/4] PostgreSQL …")
    await init_engine()
    await create_db_tables()

    logger.info("[2/4] Neo4j …")
    await init_neo4j()

    logger.info("[3/4] Qdrant …")
    await init_qdrant()

    logger.info("[4/4] Loading embedding model (%s) …", settings.embedding_model)
    await init_embedding_service()

    logger.info("✓ All services ready — accepting requests.")

    yield

    # ── Shutdown ──────────────────────────────────────────────────────────────
    logger.info("Shutting down …")
    await close_qdrant()
    await close_neo4j()
    await close_engine()
    logger.info("Shutdown complete.")


# ─────────────────────────────────────────────────────────────────────────────
# App factory
# ─────────────────────────────────────────────────────────────────────────────

def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description=(
            "AI Crime Intelligence & Investigation Platform\n\n"
            "**Organization:** Karnataka State Police (KSP)\n\n"
            "Combines AI, ML, Knowledge Graphs, Geospatial Analytics, "
            "Blockchain, and Explainable AI to assist investigators in "
            "solving crimes, predicting risks, and enabling proactive policing."
        ),
        docs_url="/docs" if not settings.is_production else None,
        redoc_url="/redoc" if not settings.is_production else None,
        openapi_url="/openapi.json" if not settings.is_production else None,
        lifespan=lifespan,
        contact={
            "name": "Karnataka State Police — AI Division",
            "email": "ai-crime-intel@ksp.gov.in",
        },
        license_info={"name": "Government of Karnataka — Internal Use"},
    )

    # ── Middleware stack ───────────────────────────────────────────────────────
    app.add_middleware(
        CORSMiddleware,
        allow_credentials=True,
        allow_origin_regex=r"https?://(10\.\d{1,3}\.\d{1,3}\.\d{1,3}|172\.(1[6-9]|2\d|3[0-1])\.\d{1,3}\.\d{1,3}|192\.168\.\d{1,3}\.\d{1,3}|localhost|127\.0\.0\.1):(5173|3000|3001)$",
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(GZipMiddleware, minimum_size=1024)
    app.add_middleware(PromptInjectionFirewall)

    @app.middleware("http")
    async def add_timing_header(request: Request, call_next):
        t0 = time.monotonic()
        response = await call_next(request)
        ms = (time.monotonic() - t0) * 1000
        response.headers["X-Response-Time-Ms"] = f"{ms:.2f}"
        response.headers["X-Platform"] = "KSP-AI-CrimeIntel"
        return response

    # ── Exception handlers ────────────────────────────────────────────────────

    @app.exception_handler(RequestValidationError)
    async def validation_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        details = [
            ErrorDetail(
                field=" → ".join(str(loc) for loc in err.get("loc", [])),
                message=err.get("msg", "Validation error"),
            )
            for err in exc.errors()
        ]
        return JSONResponse(
            status_code=422,
            content=ErrorResponse(
                status_code=422, error="Request Validation Failed", details=details
            ).model_dump(),
        )

    @app.exception_handler(HTTPException)
    async def http_handler(request: Request, exc: HTTPException) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content=ErrorResponse(
                status_code=exc.status_code,
                error=exc.detail if isinstance(exc.detail, str) else "HTTP Error",
                details=[ErrorDetail(message=str(exc.detail))],
            ).model_dump(),
            headers=getattr(exc, "headers", None),
        )

    @app.exception_handler(Exception)
    async def unhandled_handler(request: Request, exc: Exception) -> JSONResponse:
        logging.getLogger(__name__).error(
            "Unhandled exception on %s: %s", request.url.path, exc, exc_info=True
        )
        msg = str(exc) if settings.debug else "An unexpected internal error occurred."
        return JSONResponse(
            status_code=500,
            content=ErrorResponse(
                status_code=500,
                error="Internal Server Error",
                details=[ErrorDetail(message=msg)],
            ).model_dump(),
        )

    # ── Routers ───────────────────────────────────────────────────────────────
    PREFIX = "/api/v1"

    app.include_router(auth_router,      prefix=PREFIX)
    app.include_router(ingest_router,    prefix=PREFIX)
    app.include_router(analytics_router, prefix=PREFIX)
    app.include_router(evidence_router,  prefix=PREFIX)
    app.include_router(assistant_router, prefix=PREFIX)
    app.include_router(websocket_router, prefix=PREFIX)

    # ── Utility endpoints ─────────────────────────────────────────────────────

    @app.get("/health", tags=["Monitoring"])
    async def health() -> dict[str, Any]:
        return {
            "status": "healthy",
            "platform": settings.app_name,
            "version": settings.app_version,
            "environment": settings.environment,
        }

    frontend_dist = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend", "dist", "public")
    if os.path.isdir(frontend_dist):
        assets_dir = os.path.join(frontend_dist, "assets")
        if os.path.isdir(assets_dir):
            app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")
        
        @app.get("/{catchall:path}", include_in_schema=False)
        async def serve_spa(catchall: str):
            file_path = os.path.join(frontend_dist, catchall)
            if os.path.isfile(file_path):
                return FileResponse(file_path)
            
            index_path = os.path.join(frontend_dist, "index.html")
            if os.path.isfile(index_path):
                return FileResponse(index_path)
            
            return JSONResponse(status_code=404, content={"error": "Not Found"})
    else:
        @app.get("/", include_in_schema=False)
        async def root() -> dict[str, str]:
            return {
                "platform": settings.app_name,
                "version": settings.app_version,
                "docs": "/docs",
                "health": "/health",
                "notice": "Frontend build not found.",
            }

    # OpenTelemetry instrumentation
    try:
        FastAPIInstrumentor.instrument_app(app)
    except Exception:
        pass

    return app


# ─────────────────────────────────────────────────────────────────────────────
# ASGI app entry point
# ─────────────────────────────────────────────────────────────────────────────

app = create_app()


def run() -> None:
    import uvicorn
    s = get_settings()
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=s.debug,
        log_level=s.log_level.lower(),
        workers=1 if s.debug else 4,
        access_log=True,
    )


if __name__ == "__main__":
    run()
