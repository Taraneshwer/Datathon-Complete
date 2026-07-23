"""
app/intelligence/firewall.py
─────────────────────────────────────────────────────────────────────────────
Prompt Injection Firewall — two complementary layers:

1. ASGI Middleware (`PromptInjectionFirewall`):
   - Intercepts every POST/PUT/PATCH request body before routing.
   - Reads the raw body, scans for injection markers.
   - Returns HTTP 400 immediately (or strips markers) based on config.
   - Adds `X-Firewall-Status` header for observability.
   - Enforces maximum payload size.

2. Standalone sanitiser (`sanitize_text`):
   - Called inline by the AI assistant router before text reaches the LLM.
   - Strips / redacts injection patterns from a single string.
─────────────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import logging
import re
import time
from collections.abc import Callable

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from app.config import get_settings

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────────────────────
# Injection signature patterns
# ─────────────────────────────────────────────────────────────────────────────

# Direct instruction-override patterns
_DIRECT_INJECTION_PATTERNS: list[str] = [
    r"ignore\s+(all\s+)?previous\s+instructions?",
    r"disregard\s+(all\s+)?previous\s+instructions?",
    r"forget\s+(all\s+)?previous\s+instructions?",
    r"you\s+are\s+now\s+(?:a|an)\s+\w+",
    r"act\s+as\s+(?:if\s+you\s+are\s+)?(?:a|an)\s+\w+",
    r"pretend\s+(you\s+are|to\s+be)\s+",
    r"override\s+(your\s+)?(safety|system|previous)\s+",
    r"jailbreak",
    r"dan\s+mode",
    r"do\s+anything\s+now",
    r"enable\s+(developer|debug|god)\s+mode",
]

# Delimiter/structural injection patterns
_STRUCTURAL_PATTERNS: list[str] = [
    r"<\s*/?system\s*>",
    r"\[\s*system\s*\]",
    r"#{3,}\s*system",
    r"---+\s*system\s*---+",
    r"\[INST\]",
    r"<<SYS>>",
    r"</?(human|assistant|user|ai)>",
]

# Data exfiltration / SSRF patterns
_EXFIL_PATTERNS: list[str] = [
    r"http[s]?://(?!localhost)(?:\d{1,3}\.){3}\d{1,3}",  # Raw IP URLs
    r"file:///",
    r"data:text/html",
    r"javascript:",
]

# Combine all patterns into compiled regexes (case-insensitive)
_ALL_PATTERNS: list[re.Pattern[str]] = [
    re.compile(p, re.IGNORECASE | re.DOTALL)
    for p in (
        _DIRECT_INJECTION_PATTERNS
        + _STRUCTURAL_PATTERNS
        + _EXFIL_PATTERNS
    )
]

# Patterns used only for sanitisation (strip rather than block)
_STRIP_PATTERNS: list[re.Pattern[str]] = [
    re.compile(p, re.IGNORECASE | re.DOTALL) for p in _STRUCTURAL_PATTERNS
]


def _detect_injection(text: str) -> str | None:
    """
    Scan text against all injection patterns.
    Returns the matched pattern string on first hit, None if clean.
    """
    for pattern in _ALL_PATTERNS:
        m = pattern.search(text)
        if m:
            return m.group(0)
    return None


def sanitize_text(text: str) -> str:
    """
    Strip structural injection markers from `text` without blocking.
    Use this for non-critical fields where stripping is preferred over 400.

    For critical prompt inputs, prefer `check_or_raise()` instead.
    """
    for pattern in _STRIP_PATTERNS:
        text = pattern.sub("[REDACTED]", text)
    return text


def check_or_raise(text: str, field_name: str = "payload") -> str:
    """
    Raise ValueError if injection detected in `text`.
    Otherwise return the text unchanged.
    Called inline by the LLM router before assembling prompts.
    """
    match = _detect_injection(text)
    if match:
        logger.warning(
            "Prompt injection blocked in field='%s' match='%.60s'",
            field_name,
            match,
        )
        raise ValueError(
            f"Prompt injection detected in {field_name!r}. "
            "Request rejected for security reasons."
        )
    return text


# ─────────────────────────────────────────────────────────────────────────────
# ASGI Middleware
# ─────────────────────────────────────────────────────────────────────────────

_INSPECTED_METHODS = {"POST", "PUT", "PATCH"}
_BYPASS_PATHS = {"/health", "/docs", "/openapi.json", "/redoc"}


class PromptInjectionFirewall(BaseHTTPMiddleware):
    """
    Inline ASGI middleware that inspects request bodies for prompt injection.
    Operates on methods that carry a request body (POST / PUT / PATCH).
    """

    def __init__(self, app: ASGIApp) -> None:
        super().__init__(app)
        self._settings = get_settings()

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        settings = self._settings

        if not settings.firewall_enabled:
            return await call_next(request)

        # Only inspect body-carrying methods; skip utility paths
        if (
            request.method not in _INSPECTED_METHODS
            or request.url.path in _BYPASS_PATHS
        ):
            response = await call_next(request)
            response.headers["X-Firewall-Status"] = "bypassed"
            return response

        start = time.monotonic()

        # ── Payload size guard ───────────────────────────────────────────────
        content_length = int(request.headers.get("content-length", 0))
        if content_length > settings.firewall_max_payload_size:
            logger.warning(
                "Firewall: payload too large | size=%d limit=%d path=%s",
                content_length,
                settings.firewall_max_payload_size,
                request.url.path,
            )
            return JSONResponse(
                status_code=413,
                content={
                    "status_code": 413,
                    "error": "Payload Too Large",
                    "details": [
                        {
                            "message": (
                                f"Request body exceeds maximum allowed size of "
                                f"{settings.firewall_max_payload_size} bytes."
                            )
                        }
                    ],
                },
            )

        # ── Read + inspect body ──────────────────────────────────────────────
        body = await request.body()
        body_text = body.decode("utf-8", errors="replace")
        matched = _detect_injection(body_text)

        if matched:
            elapsed_ms = (time.monotonic() - start) * 1000
            logger.warning(
                "Prompt injection detected | path=%s match='%.80s' elapsed=%.1fms",
                request.url.path,
                matched,
                elapsed_ms,
            )

            if settings.firewall_block_on_injection:
                return JSONResponse(
                    status_code=400,
                    content={
                        "status_code": 400,
                        "error": "Prompt Injection Detected",
                        "details": [
                            {
                                "message": (
                                    "The request payload contains patterns associated "
                                    "with prompt injection attacks and has been blocked."
                                )
                            }
                        ],
                    },
                    headers={"X-Firewall-Status": "blocked"},
                )
            # Strip mode — replace malicious content and forward
            sanitized = sanitize_text(body_text)
            # Re-inject sanitized body into the ASGI scope for downstream
            async def receive() -> dict:  # type: ignore[return]
                return {"type": "http.request", "body": sanitized.encode(), "more_body": False}

            request = Request(request.scope, receive)

        response = await call_next(request)
        elapsed_ms = (time.monotonic() - start) * 1000
        response.headers["X-Firewall-Status"] = "clean"
        response.headers["X-Firewall-Latency-Ms"] = f"{elapsed_ms:.2f}"
        return response
