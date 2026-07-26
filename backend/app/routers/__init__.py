"""app/routers/__init__.py"""
from app.routers.analytics import router as analytics_router
from app.routers.assistant import router as assistant_router
from app.routers.auth import router as auth_router
from app.routers.core_endpoints import router as core_endpoints_router
from app.routers.evidence import router as evidence_router
from app.routers.ingest import router as ingest_router
from app.routers.websocket import router as websocket_router

__all__ = [
    "auth_router",
    "ingest_router",
    "assistant_router",
    "analytics_router",
    "evidence_router",
    "websocket_router",
    "core_endpoints_router",
]
