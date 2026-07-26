"""
app/main.py
─────────────────────────────────────────────────────────────────────────────
AI Crime Intelligence & Investigation Platform — FastAPI Application Factory
100% Zoho Catalyst-Native Serverless Runtime Architecture.
Zero external database drivers (Neo4j, Qdrant, MongoDB excised).
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
from fastapi.responses import FileResponse, JSONResponse
try:
    from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
except ImportError:
    FastAPIInstrumentor = None

from app.config import get_settings
from app.db.catalyst import close_catalyst, init_catalyst
from app.intelligence.firewall import PromptInjectionFirewall
from app.models.schemas import ErrorDetail, ErrorResponse
from app.routers import (
    analytics_router,
    assistant_router,
    auth_router,
    core_endpoints_router,
    evidence_router,
    ingest_router,
    websocket_router,
)

# ── Logging ─────────────────────────────────────────────────────────────
def _configure_logging(log_level: str) -> None:
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.dev.ConsoleRenderer() if log_level == "DEBUG" else structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(getattr(logging, log_level, logging.INFO)),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
    )
    logging.basicConfig(level=getattr(logging, log_level, logging.INFO))

# ── Lifespan ────────────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    _configure_logging(settings.log_level)
    logger = logging.getLogger(__name__)

    banner = "=" * 65
    logger.info(banner)
    logger.info("  %s  v%s (100%% Catalyst Native)", settings.app_name, settings.app_version)
    logger.info("  Environment : %s", settings.environment)
    logger.info("  LLM Provider: Zoho Catalyst QuickML (%s)", settings.llm_model)
    logger.info("  Embedding   : Zoho Catalyst QuickML (%s)", settings.embedding_model)
    logger.info("  Databases   : Catalyst Data Store (Relational+Graph), NoSQL, Cache, Stratus")
    logger.info(banner)

    # ── Startup ───────────────────────────────────────────────────────────
    logger.info("[1/1] Initializing Zoho Catalyst Cloud SDK & Serverless Services …")
    await init_catalyst()
    logger.info("✓ 100% Catalyst Native Cloud Services ready — accepting requests.")

    yield

    # ── Shutdown ──────────────────────────────────────────────────────────
    logger.info("Shutting down Catalyst resources …")
    await close_catalyst()
    logger.info("Shutdown complete.")

# ── App factory ─────────────────────────────────────────────────────────
def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description=(
            "AI Crime Intelligence & Investigation Platform (100% Zoho Catalyst-Native Architecture)\n\n"
            "**Organization:** Karnataka State Police (KSP)\n\n"
            "Combines Catalyst QuickML, Zia AI, Data Store Relational Graph Engine, "
            "and Serverless Functions to assist investigators in solving crimes and predicting risks."
        ),
        docs_url="/docs" if not settings.is_production else None,
        redoc_url="/redoc" if not settings.is_production else None,
        openapi_url="/openapi.json" if not settings.is_production else None,
        lifespan=lifespan,
        contact={"name": "Karnataka State Police — AI Division", "email": "ai-crime-intel@ksp.gov.in"},
        license_info={"name": "Government of Karnataka — Internal Use"},
    )

    app.add_middleware(
        CORSMiddleware,
        allow_credentials=True,
        allow_origins=["https://datathon-complete-qzpldrhq.onslate.in", "*"],
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
        response.headers["X-Platform"] = "KSP-AI-CrimeIntel-Catalyst-Native"
        return response

    @app.exception_handler(RequestValidationError)
    async def validation_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
        details = [ErrorDetail(field=" → ".join(str(loc) for loc in err.get("loc", [])), message=err.get("msg", "Validation error")) for err in exc.errors()]
        return JSONResponse(status_code=422, content=ErrorResponse(status_code=422, error="Request Validation Failed", details=details).model_dump())

    @app.exception_handler(HTTPException)
    async def http_handler(request: Request, exc: HTTPException) -> JSONResponse:
        return JSONResponse(status_code=exc.status_code, content=ErrorResponse(status_code=exc.status_code, error=exc.detail if isinstance(exc.detail, str) else "HTTP Error", details=[ErrorDetail(message=str(exc.detail))]).model_dump(), headers=getattr(exc, "headers", None))

    @app.exception_handler(Exception)
    async def unhandled_handler(request: Request, exc: Exception) -> JSONResponse:
        logging.getLogger(__name__).error("Unhandled exception on %s: %s", request.url.path, exc, exc_info=True)
        msg = str(exc) if settings.debug else "An unexpected internal error occurred."
        return JSONResponse(status_code=500, content=ErrorResponse(status_code=500, error="Internal Server Error", details=[ErrorDetail(message=msg)]).model_dump())

    PREFIX = "/api/v1"
    app.include_router(auth_router,      prefix=PREFIX)
    app.include_router(ingest_router,    prefix=PREFIX)
    app.include_router(analytics_router, prefix=PREFIX)
    app.include_router(evidence_router,  prefix=PREFIX)
    app.include_router(assistant_router, prefix=PREFIX)
    app.include_router(websocket_router, prefix=PREFIX)
    app.include_router(core_endpoints_router, prefix=PREFIX)
    app.include_router(core_endpoints_router, prefix="/api")

    @app.get("/health", tags=["Monitoring"])
    @app.get("/api/healthz", tags=["Monitoring"])
    @app.get("/api/v1/healthz", tags=["Monitoring"])
    async def health() -> dict[str, Any]:
        return {"status": "healthy", "platform": settings.app_name, "version": settings.app_version, "environment": settings.environment, "architecture": "100% Zoho Catalyst Native"}

    frontend_dist = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend", "dist", "public")
    if os.path.isdir(frontend_dist):
        assets_dir = os.path.join(frontend_dist, "assets")
        if os.path.isdir(assets_dir):
            app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")
        
        @app.get("/{catchall:path}", include_in_schema=False)
        async def serve_spa(catchall: str):
            file_path = os.path.join(frontend_dist, catchall)
            if os.path.isfile(file_path): return FileResponse(file_path)
            index_path = os.path.join(frontend_dist, "index.html")
            if os.path.isfile(index_path): return FileResponse(index_path)
            return JSONResponse(status_code=404, content={"error": "Not Found"})
    else:
        @app.get("/", include_in_schema=False)
        async def root() -> dict[str, str]:
            return {"platform": settings.app_name, "version": settings.app_version, "docs": "/docs", "health": "/health", "notice": "Frontend build not found."}

    if FastAPIInstrumentor:
        try:
            FastAPIInstrumentor.instrument_app(app)
        except Exception:
            pass

    return app

app = create_app()

def run() -> None:
    import uvicorn
    port = int(os.environ.get("X_ZOHO_CATALYST_LISTEN_PORT", 8000))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=False, workers=1)

if __name__ == "__main__":
    run()