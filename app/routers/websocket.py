"""
app/routers/websocket.py
─────────────────────────────────────────────────────────────────────────────
WebSocket alert streaming router.

Endpoints:
  WS  /api/v1/ws/alerts              — real-time alert stream for a client
  POST /api/v1/ws/broadcast          — admin-triggered broadcast (internal)
  GET  /api/v1/ws/status             — connection count + active client list
─────────────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import asyncio
import logging
import uuid
from datetime import datetime

from fastapi import APIRouter, HTTPException, Query, WebSocket, WebSocketDisconnect, status

from app.config import get_settings
from app.models.schemas import AlertPayload
from app.websocket.connection_manager import manager

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/ws",
    tags=["WebSocket / Real-time"],
)


# ─────────────────────────────────────────────────────────────────────────────
# WS /ws/alerts  — Client Alert Stream
# ─────────────────────────────────────────────────────────────────────────────

@router.websocket("/alerts")
async def websocket_alerts(
    websocket: WebSocket,
    client_id: str = Query(default_factory=lambda: str(uuid.uuid4())),
    topics: str = Query(default="", description="Comma-separated topic filters"),
) -> None:
    """
    WebSocket endpoint for real-time crime alert streaming.

    Query Parameters:
      - `client_id`: Optional stable client identifier (auto-generated if omitted).
      - `topics`: Comma-separated alert topic filters (e.g. `high_severity,new_case`).
                  Empty = subscribe to all topics.

    Protocol:
      - Server sends JSON messages: `{"event": "...", "payload": {...}}`
      - Client may send `{"type": "ping"}` for keep-alive; server echoes `pong`.
      - Server sends heartbeat `{"event": "ping"}` every `WS_HEARTBEAT_INTERVAL` seconds.
    """
    settings = get_settings()
    parsed_topics: set[str] = {
        t.strip() for t in topics.split(",") if t.strip()
    } if topics else set()

    await manager.connect(
        websocket=websocket,
        client_id=client_id,
        subscriptions=parsed_topics,
    )

    logger.info(
        "WS client connected | id=%s topics=%s",
        client_id,
        parsed_topics or "all",
    )

    heartbeat_task = asyncio.create_task(
        _heartbeat_loop(client_id, settings.ws_heartbeat_interval)
    )

    try:
        while True:
            # Await incoming message (keep-alive pings from client)
            try:
                data = await asyncio.wait_for(
                    websocket.receive_json(),
                    timeout=float(settings.ws_heartbeat_interval) * 2,
                )
                if isinstance(data, dict) and data.get("type") == "ping":
                    await manager.send_personal_json(
                        client_id,
                        {"event": "pong", "timestamp": datetime.now().isoformat()},
                    )
            except asyncio.TimeoutError:
                # Client hasn't pinged in 2x heartbeat interval — check alive
                alive = await manager.send_personal_json(
                    client_id,
                    {"event": "ping", "timestamp": datetime.now().isoformat()},
                )
                if not alive:
                    break
            except WebSocketDisconnect:
                break

    except WebSocketDisconnect:
        logger.info("WS client disconnected | id=%s", client_id)
    except Exception as exc:
        logger.error("WS error for client %s: %s", client_id, exc, exc_info=True)
    finally:
        heartbeat_task.cancel()
        await manager.disconnect(client_id)


async def _heartbeat_loop(client_id: str, interval: int) -> None:
    """Background coroutine that sends periodic heartbeat pings to a client."""
    try:
        while True:
            await asyncio.sleep(interval)
            await manager.send_personal_json(
                client_id,
                {"event": "heartbeat", "timestamp": datetime.now().isoformat()},
            )
    except asyncio.CancelledError:
        pass  # Normal shutdown


# ─────────────────────────────────────────────────────────────────────────────
# POST /ws/broadcast  — Admin Broadcast
# ─────────────────────────────────────────────────────────────────────────────

@router.post(
    "/broadcast",
    status_code=status.HTTP_200_OK,
    summary="Broadcast an alert to all connected WebSocket clients",
    tags=["WebSocket / Real-time"],
)
async def broadcast_alert(payload: AlertPayload) -> dict:
    """
    Broadcast a structured alert message to all active WebSocket connections.
    Optionally filtered by severity topic.

    In production, protect this endpoint with an API key or service-to-service
    authentication header.
    """
    message = {
        "event": "alert",
        "payload": payload.model_dump(mode="json"),
        "broadcast_at": datetime.now().isoformat(),
    }

    # Use severity as a topic filter if provided
    topic = payload.severity.value if payload.severity else None

    sent_count = await manager.broadcast(data=message, topic=topic)

    logger.info(
        "Broadcast sent | event=%s sent_to=%d topic=%s",
        payload.event_type,
        sent_count,
        topic,
    )

    return {
        "status": "broadcasted",
        "recipients": sent_count,
        "active_connections": manager.active_connection_count,
    }


# ─────────────────────────────────────────────────────────────────────────────
# GET /ws/status  — Connection Status
# ─────────────────────────────────────────────────────────────────────────────

@router.get(
    "/status",
    status_code=status.HTTP_200_OK,
    summary="WebSocket connection pool status",
)
async def websocket_status() -> dict:
    """Return the count and IDs of all currently connected WebSocket clients."""
    return {
        "active_connections": manager.active_connection_count,
        "client_ids": manager.client_ids,
    }
