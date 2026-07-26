"""
app/routers/core_endpoints.py
─────────────────────────────────────────────────────────────────────────────
FastAPI router for core platform data endpoints.
100% Zoho Catalyst-Native implementation querying DataStore via ZCQL/SQL.
Zero mock data, zero simulation datasets, zero hardcoded responses.
─────────────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException, Query, status

from app.services.catalyst_datastore_service import CatalystDataStoreService

router = APIRouter(tags=["Core Reference Data"])
datastore_service = CatalystDataStoreService()


@router.get("/healthz", summary="Health check")
async def health_check() -> Dict[str, Any]:
    return {"status": "healthy", "service": "CIPA Core API (100% Zoho Catalyst Native)"}


@router.get("/districts", summary="List all districts with crime stats")
async def list_districts() -> List[Dict[str, Any]]:
    return await datastore_service.get_districts()


@router.get("/hotspots", summary="Get hotspot heatmap data")
async def list_hotspots(
    districtId: Optional[str] = Query(None),
    timeOfDay: Optional[int] = Query(None),
    crimeType: Optional[str] = Query(None),
    blindSpot: Optional[bool] = Query(None),
) -> List[Dict[str, Any]]:
    results = await datastore_service.get_hotspots(district_id=districtId)
    if crimeType:
        results = [h for h in results if h.get("category", "").lower() == crimeType.lower()]
    if timeOfDay is not None:
        results = [h for h in results if h.get("timeOfDay") == timeOfDay]
    if blindSpot is not None:
        results = [h for h in results if h.get("isAnomaly") == blindSpot]
    return results


@router.get("/cases", summary="List crime cases")
async def list_cases(
    districtId: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
) -> List[Dict[str, Any]]:
    results = await datastore_service.get_cases(limit=500)
    if districtId:
        results = [c for c in results if c.get("districtId") == districtId]
    if status:
        results = [c for c in results if c.get("status", "").lower() == status.lower()]
    return results


@router.get("/cases/summary", summary="Get case counts summary")
async def get_case_summary() -> Dict[str, Any]:
    return await datastore_service.get_cases_summary()


@router.get("/cases/{id}", summary="Get case details by ID")
async def get_case(id: str) -> Dict[str, Any]:
    case_data = await datastore_service.get_case(id)
    if not case_data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Case {id} not found in Zoho Catalyst DataStore")
    return case_data


@router.get("/suspects", summary="List suspects")
async def list_suspects(caseId: Optional[str] = Query(None)) -> List[Dict[str, Any]]:
    results = await datastore_service.get_suspects()
    if caseId:
        results = [s for s in results if caseId in s.get("caseIds", [])]
    return results


@router.get("/suspects/{id}", summary="Get suspect details by ID")
async def get_suspect(id: str) -> Dict[str, Any]:
    suspect_data = await datastore_service.get_suspect(id)
    if not suspect_data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Suspect {id} not found in Zoho Catalyst DataStore")
    return suspect_data


@router.get("/victims", summary="List victims")
async def list_victims(caseId: Optional[str] = Query(None)) -> List[Dict[str, Any]]:
    return await datastore_service.get_victims(case_id=caseId)


@router.get("/graph/nodes", summary="List knowledge graph nodes")
async def list_graph_nodes(caseId: Optional[str] = Query(None)) -> List[Dict[str, Any]]:
    results = await datastore_service.get_nodes(case_id=caseId)
    if caseId:
        results = [n for n in results if n["id"] == caseId or caseId in n.get("linkedCaseIds", [])]
    return results


@router.get("/graph/edges", summary="List knowledge graph edges")
async def list_graph_edges(caseId: Optional[str] = Query(None)) -> List[Dict[str, Any]]:
    results = await datastore_service.get_edges(case_id=caseId)
    if caseId:
        results = [e for e in results if caseId in (e.get("source"), e.get("target"))]
    return results


@router.get("/patterns", summary="List behavioral patterns")
async def list_patterns(districtId: Optional[str] = Query(None)) -> List[Dict[str, Any]]:
    return await datastore_service.get_patterns(district_id=districtId)


@router.get("/patterns/{id}", summary="Get pattern by ID")
async def get_pattern(id: str) -> Dict[str, Any]:
    pattern_data = await datastore_service.get_pattern(id)
    if not pattern_data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Pattern {id} not found in Zoho Catalyst DataStore")
    return pattern_data


@router.get("/analytics/dashboard", summary="Get dashboard analytics")
async def get_dashboard_analytics() -> Dict[str, Any]:
    return await datastore_service.get_dashboard_analytics()


@router.get("/analytics/crime-trend", summary="Get crime trend")
async def get_crime_trend() -> List[Dict[str, Any]]:
    return await datastore_service.get_crime_trend()


@router.get("/analytics/risk-forecast", summary="Get risk forecast")
async def get_risk_forecast() -> List[Dict[str, Any]]:
    return await datastore_service.get_risk_forecast()


@router.get("/analytics/bias", summary="Get bias audit")
async def get_bias_audit() -> Dict[str, Any]:
    return await datastore_service.get_bias_audit()


@router.get("/alerts", summary="List alerts")
async def list_alerts(
    districtId: Optional[str] = Query(None),
    severity: Optional[str] = Query(None),
) -> List[Dict[str, Any]]:
    return await datastore_service.list_alerts(district_id=districtId, severity=severity)


@router.get("/cases/{id}/timeline", summary="Get case timeline events")
async def get_case_timeline(id: str) -> List[Dict[str, Any]]:
    return await datastore_service.get_case_timeline(id)


@router.get("/cases/{id}/evidence", summary="Get case evidence items")
async def get_case_evidence(id: str) -> List[Dict[str, Any]]:
    return await datastore_service.get_case_evidence(id)


@router.get("/audit/access-log", summary="Get audit access log")
async def list_access_log() -> List[Dict[str, Any]]:
    return await datastore_service.list_access_log()


@router.get("/audit/ledger-status", summary="Get ledger status")
async def get_ledger_status() -> Dict[str, Any]:
    return await datastore_service.get_ledger_status()


# ─────────────────────────────────────────────────────────────────────────────
# KSP Specific Endpoints for Page Components
# ─────────────────────────────────────────────────────────────────────────────

@router.get("/alerts/national", summary="Get national early warning alerts")
async def get_national_alerts() -> List[Dict[str, Any]]:
    return await datastore_service.get_national_alerts()


@router.get("/blockchain/ledger", summary="Get blockchain ledger records")
async def get_blockchain_ledger() -> List[Dict[str, Any]]:
    return await datastore_service.get_blockchain_ledger()


@router.get("/evidence/items", summary="Get evidence center items")
async def get_evidence_center_items() -> List[Dict[str, Any]]:
    return await datastore_service.get_evidence_center_items()


@router.get("/investigations/cases", summary="Get active investigations cases")
async def get_investigations_cases() -> List[Dict[str, Any]]:
    return await datastore_service.get_investigation_cases()


@router.get("/replay/path", summary="Get crime replay timeline path")
async def get_replay_path() -> List[Dict[str, Any]]:
    return await datastore_service.get_replay_path()


@router.get("/graph/ksp", summary="Get KSP investigative knowledge graph")
async def get_ksp_graph() -> Dict[str, Any]:
    return await datastore_service.get_ksp_graph()


@router.get("/identity/credentials", summary="Get decentralized identity credentials")
async def get_identity_credentials() -> List[Dict[str, Any]]:
    return await datastore_service.get_credentials()


@router.get("/assistant/history", summary="Get AI assistant conversation history")
async def get_assistant_history() -> List[Dict[str, Any]]:
    return await datastore_service.get_assistant_history()


@router.get("/assistant/blocked", summary="Get AI assistant prompt firewall blocked logs")
async def get_assistant_blocked() -> List[Dict[str, Any]]:
    return await datastore_service.get_assistant_blocked()
