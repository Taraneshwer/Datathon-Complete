"""
app/config.py
─────────────────────────────────────────────────────────────────────────────
Centralised settings for the AI Crime Intelligence & Investigation Platform.
All values loaded from environment variables / .env — zero os.getenv() calls.
─────────────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        str_strip_whitespace=True,
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── Application ──────────────────────────────────────────────────────────
    environment: Literal["development", "staging", "production"] = "development"
    app_name: str = "AI Crime Intelligence & Investigation Platform"
    app_version: str = "2.0.0"
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    secret_key: str = Field(..., min_length=32)
    api_prefix: str = "/api/v1"

    # ── Zoho Catalyst Data Store ──────────────────────────────────────────────
    zoho_catalyst_project_id: str | None = None
    zoho_catalyst_environment: Literal["Development", "Production"] = "Development"
    zoho_catalyst_client_id: str | None = None
    zoho_catalyst_client_secret: str | None = None
    zoho_catalyst_app_name: str = "crime_intel"

    # ── Catalyst QuickML & Knowledge Base ─────────────────────────────────────
    quickml_kb_name: str = "rainfall_crime_knowledge_base"
    embedding_model: str = "nemotron-3-embed-1b"
    llm_provider: Literal["catalyst"] = "catalyst"
    llm_model: str = "llama-3.1-70b-instruct"


    # ── Authentication & RBAC ─────────────────────────────────────────────────
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = Field(default=60, ge=5)
    jwt_refresh_token_expire_days: int = Field(default=7, ge=1)
    mfa_issuer: str = "KSP Crime Intelligence Platform"

    # ── Blockchain Audit ─────────────────────────────────────────────────────
    blockchain_enabled: bool = True
    blockchain_network_id: str = "ksp-crime-network"
    fabric_gateway_url: str | None = None
    fabric_channel: str = "crime-channel"
    fabric_chaincode: str = "crime-audit"



    # ── Prompt Injection Firewall ────────────────────────────────────────────
    firewall_enabled: bool = True
    firewall_block_on_injection: bool = True
    firewall_max_payload_size: int = Field(default=65536, ge=1024)

    # ── Intelligence Engines ──────────────────────────────────────────────────
    pattern_match_top_k: int = Field(default=5, ge=1, le=50)
    pattern_match_score_threshold: float = Field(default=0.65, ge=0.0, le=1.0)
    dbscan_eps: float = Field(default=0.5, gt=0.0)
    dbscan_min_samples: int = Field(default=3, ge=2)
    hdbscan_min_cluster_size: int = Field(default=5, ge=2)
    early_warning_alert_threshold: float = Field(default=0.75, ge=0.0, le=1.0)
    bias_confidence_threshold: float = Field(default=0.6, ge=0.0, le=1.0)

    # ── Evidence Processing ───────────────────────────────────────────────────
    evidence_max_file_size_mb: int = Field(default=100, ge=1)
    ocr_languages: list[str] = Field(default_factory=lambda: ["en", "kn"])
    whisper_model_size: Literal["tiny", "base", "small", "medium", "large"] = "base"
    yolo_confidence_threshold: float = Field(default=0.4, ge=0.1, le=1.0)

    # ── WebSocket ─────────────────────────────────────────────────────────────
    ws_heartbeat_interval: int = Field(default=30, ge=5)

    # ── Geospatial ────────────────────────────────────────────────────────────
    h3_resolution: int = Field(default=8, ge=5, le=12)  # ~0.74 km² per cell
    openstreetmap_tile_url: str = "https://tile.openstreetmap.org/{z}/{x}/{y}.png"

    @model_validator(mode="after")
    def validate_llm_credentials(self) -> Settings:
        return self

    @property
    def is_production(self) -> bool:
        return self.environment == "production"

    @property
    def debug(self) -> bool:
        return self.environment == "development"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]
