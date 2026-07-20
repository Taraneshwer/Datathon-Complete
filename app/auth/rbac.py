"""
app/auth/rbac.py
─────────────────────────────────────────────────────────────────────────────
Role-Based Access Control (RBAC) for the crime intelligence platform.
Uses FastAPI dependency injection to enforce role requirements on routes.
─────────────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import logging
from typing import Annotated

from fastapi import Depends, HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError

from app.auth.jwt_handler import decode_token
from app.models.fir import OfficerRole

logger = logging.getLogger(__name__)
bearer = HTTPBearer(auto_error=True)

# Role hierarchy: each role includes all permissions of roles below it
ROLE_HIERARCHY: dict[OfficerRole, int] = {
    OfficerRole.FIELD_OFFICER: 1,
    OfficerRole.FORENSIC_EXPERT: 2,
    OfficerRole.COURT_LIAISON: 2,
    OfficerRole.ANALYST: 3,
    OfficerRole.INVESTIGATING_OFFICER: 4,
    OfficerRole.DISTRICT_ADMIN: 5,
    OfficerRole.SUPER_ADMIN: 6,
}

# Endpoint-level permission matrix
PERMISSIONS: dict[str, list[OfficerRole]] = {
    "ingest_fir": [
        OfficerRole.FIELD_OFFICER,
        OfficerRole.INVESTIGATING_OFFICER,
        OfficerRole.DISTRICT_ADMIN,
        OfficerRole.SUPER_ADMIN,
    ],
    "query_patterns": [
        OfficerRole.ANALYST,
        OfficerRole.INVESTIGATING_OFFICER,
        OfficerRole.DISTRICT_ADMIN,
        OfficerRole.SUPER_ADMIN,
    ],
    "view_graph": [
        OfficerRole.ANALYST,
        OfficerRole.INVESTIGATING_OFFICER,
        OfficerRole.DISTRICT_ADMIN,
        OfficerRole.SUPER_ADMIN,
    ],
    "upload_evidence": [
        OfficerRole.INVESTIGATING_OFFICER,
        OfficerRole.FORENSIC_EXPERT,
        OfficerRole.DISTRICT_ADMIN,
        OfficerRole.SUPER_ADMIN,
    ],
    "submit_to_court": [
        OfficerRole.COURT_LIAISON,
        OfficerRole.DISTRICT_ADMIN,
        OfficerRole.SUPER_ADMIN,
    ],
    "manage_officers": [
        OfficerRole.DISTRICT_ADMIN,
        OfficerRole.SUPER_ADMIN,
    ],
    "ai_assistant": [
        OfficerRole.ANALYST,
        OfficerRole.INVESTIGATING_OFFICER,
        OfficerRole.DISTRICT_ADMIN,
        OfficerRole.SUPER_ADMIN,
    ],
}


class CurrentOfficer:
    """Parsed JWT claims for the authenticated officer."""

    def __init__(self, officer_id: str, badge: str, role: OfficerRole, district: str | None):
        self.officer_id = officer_id
        self.badge = badge
        self.role = role
        self.district = district

    def has_permission(self, permission: str) -> bool:
        allowed = PERMISSIONS.get(permission, [])
        return self.role in allowed

    def has_min_role(self, min_role: OfficerRole) -> bool:
        return ROLE_HIERARCHY.get(self.role, 0) >= ROLE_HIERARCHY.get(min_role, 0)


async def get_current_officer(
    credentials: HTTPAuthorizationCredentials = Security(bearer),
) -> CurrentOfficer:
    """Extract and validate the JWT bearer token from the Authorization header."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired authentication token.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_token(credentials.credentials)
        if payload.get("type") != "access":
            raise credentials_exception
        officer_id: str = payload.get("sub", "")
        role_str: str = payload.get("role", OfficerRole.FIELD_OFFICER.value)
        role = OfficerRole(role_str)
        return CurrentOfficer(
            officer_id=officer_id,
            badge=payload.get("badge", ""),
            role=role,
            district=payload.get("district"),
        )
    except (JWTError, ValueError) as exc:
        logger.warning("JWT validation failed: %s", exc)
        raise credentials_exception from exc


def require_roles(*roles: OfficerRole):
    """
    FastAPI dependency factory that enforces role-based access.

    Usage:
        @router.post("/sensitive", dependencies=[Depends(require_roles(OfficerRole.ANALYST))])
    """
    async def checker(
        officer: CurrentOfficer = Depends(get_current_officer),
    ) -> CurrentOfficer:
        if officer.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    f"Access denied. Required roles: "
                    f"{[r.value for r in roles]}. "
                    f"Your role: {officer.role.value}."
                ),
            )
        return officer
    return checker


def require_min_role(min_role: OfficerRole):
    """Dependency that requires at least `min_role` in the hierarchy."""
    async def checker(
        officer: CurrentOfficer = Depends(get_current_officer),
    ) -> CurrentOfficer:
        if not officer.has_min_role(min_role):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    f"Minimum role required: {min_role.value}. "
                    f"Your role: {officer.role.value}."
                ),
            )
        return officer
    return checker


# Typed aliases for common use
CurrentOfficerDep = Annotated[CurrentOfficer, Depends(get_current_officer)]
