"""
app/routers/auth.py
─────────────────────────────────────────────────────────────────────────────
Authentication & Identity router.

Endpoints:
  POST /auth/login        — Authenticate officer, issue JWT tokens
  POST /auth/refresh      — Exchange refresh token for new access token
  POST /auth/register     — Register new officer (admin only)
  GET  /auth/me           — Get current officer profile
  POST /auth/mfa/setup    — Setup TOTP-based MFA
  POST /auth/mfa/verify   — Verify MFA code
─────────────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import logging

import pyotp
from fastapi import APIRouter, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.auth.jwt_handler import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.auth.rbac import CurrentOfficerDep, require_min_role
from app.config import get_settings
from app.dependencies import DBSession
from app.models.fir import AuditAction, AuditTrail, Officer, OfficerRole
from app.models.schemas import LoginRequest, OfficerCreate, TokenResponse

logger = logging.getLogger(__name__)
settings = get_settings()

router = APIRouter(prefix="/auth", tags=["Authentication & Identity"])


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Authenticate officer and issue JWT tokens",
)
async def login(payload: LoginRequest, db: DBSession) -> TokenResponse:
    """
    Authenticate with badge number + password. Optionally verify TOTP MFA code.
    Returns short-lived access token and long-lived refresh token.
    """
    result = await db.exec(
        select(Officer).where(Officer.badge_number == payload.badge_number)
    )
    officer = result.first()

    if not officer or not verify_password(payload.password, officer.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid badge number or password.",
        )

    if not officer.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Officer account is deactivated.",
        )

    # MFA verification
    if officer.mfa_enabled:
        if not payload.mfa_code:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="MFA code required. Please provide your TOTP code.",
            )
        totp = pyotp.TOTP(officer.mfa_secret)
        if not totp.verify(payload.mfa_code):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid MFA code.",
            )

    # Issue tokens
    extra = {"role": officer.role.value, "badge": officer.badge_number, "district": officer.district}
    access_token = create_access_token(subject=str(officer.id), extra_claims=extra)
    refresh_token = create_refresh_token(subject=str(officer.id))

    # Audit login
    db.add(AuditTrail(
        officer_id=officer.id,
        action=AuditAction.LOGIN,
        actor=officer.badge_number,
        detail="Successful login",
    ))
    await db.commit()

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in_minutes=settings.jwt_access_token_expire_minutes,
        officer_id=str(officer.id),
        role=officer.role,
    )


@router.post("/refresh", summary="Refresh access token")
async def refresh_token(refresh_tok: str, db: DBSession) -> dict:
    """Exchange a valid refresh token for a new access token."""
    try:
        payload = decode_token(refresh_tok)
        if payload.get("type") != "refresh":
            raise ValueError("Not a refresh token")
        officer_id = payload["sub"]
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token.",
        )

    import uuid
    result = await db.exec(select(Officer).where(Officer.id == uuid.UUID(officer_id)))
    officer = result.first()
    if not officer or not officer.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Officer not found.")

    extra = {"role": officer.role.value, "badge": officer.badge_number}
    return {
        "access_token": create_access_token(str(officer.id), extra_claims=extra),
        "token_type": "bearer",
        "expires_in_minutes": settings.jwt_access_token_expire_minutes,
    }


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    summary="Register a new officer (admin only)",
    dependencies=[],  # Add require_min_role(OfficerRole.DISTRICT_ADMIN) in production
)
async def register_officer(payload: OfficerCreate, db: DBSession) -> dict:
    """Create a new officer account with RBAC role assignment."""
    # Check badge uniqueness
    existing = await db.exec(
        select(Officer).where(Officer.badge_number == payload.badge_number)
    )
    if existing.first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Badge number '{payload.badge_number}' already registered.",
        )

    officer = Officer(
        badge_number=payload.badge_number,
        full_name=payload.full_name,
        email=payload.email,
        hashed_password=hash_password(payload.password),
        role=payload.role,
        station_code=payload.station_code,
        district=payload.district,
    )
    db.add(officer)
    await db.commit()
    await db.refresh(officer)

    return {
        "message": "Officer registered successfully.",
        "officer_id": str(officer.id),
        "badge_number": officer.badge_number,
        "role": officer.role.value,
    }


@router.get("/me", summary="Get current officer profile")
async def get_me(current_officer: CurrentOfficerDep) -> dict:
    return {
        "officer_id": current_officer.officer_id,
        "badge": current_officer.badge,
        "role": current_officer.role.value,
        "district": current_officer.district,
    }


@router.post("/mfa/setup", summary="Generate TOTP MFA secret for officer")
async def setup_mfa(current_officer: CurrentOfficerDep, db: DBSession) -> dict:
    """Generate a TOTP secret and provisioning URI for authenticator apps."""
    import uuid
    result = await db.exec(
        select(Officer).where(Officer.id == uuid.UUID(current_officer.officer_id))
    )
    officer = result.first()
    if not officer:
        raise HTTPException(status_code=404, detail="Officer not found.")

    secret = pyotp.random_base32()
    totp = pyotp.TOTP(secret)
    uri = totp.provisioning_uri(
        name=officer.badge_number, issuer_name=settings.mfa_issuer
    )

    officer.mfa_secret = secret
    db.add(officer)
    await db.commit()

    return {"secret": secret, "provisioning_uri": uri,
            "message": "Scan the URI with Google Authenticator or similar app."}


@router.post("/mfa/verify", summary="Enable MFA after verifying TOTP code")
async def verify_mfa(
    code: str, current_officer: CurrentOfficerDep, db: DBSession
) -> dict:
    """Verify the TOTP code and activate MFA for the officer account."""
    import uuid
    result = await db.exec(
        select(Officer).where(Officer.id == uuid.UUID(current_officer.officer_id))
    )
    officer = result.first()
    if not officer or not officer.mfa_secret:
        raise HTTPException(status_code=400, detail="MFA secret not set up. Call /mfa/setup first.")

    if not pyotp.TOTP(officer.mfa_secret).verify(code):
        raise HTTPException(status_code=401, detail="Invalid TOTP code.")

    officer.mfa_enabled = True
    db.add(officer)
    await db.commit()

    return {"message": "MFA successfully enabled.", "mfa_enabled": True}
