"""
app/websocket/connection_manager.py
─────────────────────────────────────────────────────────────────────────────
WebSocket connection manager supporting:
  - Multi-client fan-out broadcasts
  - Per-client metadata tagging (client_id, connected_at, remote_addr)
  - Graceful stale-connection cleanup on send failure
  - JSON and raw-text message variants
─────────────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import asyncio
import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from fastapi import WebSocket, WebSocketDisconnect
from starlette.websockets import WebSocketState

logger = logging.getLogger(__name__)


@dataclass
class ConnectedClient:
    websocket: WebSocket
    client_id: str
    remote_addr: str
    connected_at: datetime = field(default_factory=datetime.now)
    subscriptions: set[str] = field(default_factory=set)  # topic filters


class ConnectionManager:
    """
    Thread-safe WebSocket connection manager.
    All public methods are async and safe to call from multiple coroutines.
    """

    def __init__(self) -> None:
        self._clients: dict[str, ConnectedClient] = {}
        self._lock = asyncio.Lock()

    # ── Connection lifecycle ──────────────────────────────────────────────────

    async def connect(
        self,
        websocket: WebSocket,
        client_id: str,
        subscriptions: set[str] | None = None,
    ) -> None:
        """Accept and register a new WebSocket connection."""
        await websocket.accept()
        remote_addr = (
            f"{websocket.client.host}:{websocket.client.port}"
            if websocket.client
            else "unknown"
        )
        client = ConnectedClient(
            websocket=websocket,
            client_id=client_id,
            remote_addr=remote_addr,
            subscriptions=subscriptions or set(),
        )
        async with self._lock:
            self._clients[client_id] = client

        logger.info(
            "WebSocket client connected | id=%s addr=%s total=%d",
            client_id,
            remote_addr,
            len(self._clients),
        )
        # Send welcome handshake
        await self._send_json(
            websocket,
            {
                "event": "connected",
                "client_id": client_id,
                "timestamp": datetime.now().isoformat(),
            },
        )

    async def disconnect(self, client_id: str) -> None:
        """Deregister a client; close socket if still open."""
        async with self._lock:
            client = self._clients.pop(client_id, None)

        if client:
            if client.websocket.client_state != WebSocketState.DISCONNECTED:
                try:
                    await client.websocket.close()
                except Exception:
                    pass
            logger.info(
                "WebSocket client disconnected | id=%s remaining=%d",
                client_id,
                len(self._clients),
            )

    # ── Messaging ─────────────────────────────────────────────────────────────

    async def send_personal_json(self, client_id: str, data: dict[str, Any]) -> bool:
        """Send a JSON message to a single client. Returns False if not found."""
        async with self._lock:
            client = self._clients.get(client_id)
        if not client:
            return False
        success = await self._send_json(client.websocket, data)
        if not success:
            await self.disconnect(client_id)
        return success

    async def broadcast(
        self,
        data: dict[str, Any],
        topic: str | None = None,
        exclude: set[str] | None = None,
    ) -> int:
        """
        Broadcast a JSON message to all connected clients.
        Optionally filter by topic subscription and/or exclude specific IDs.
        Returns the number of clients successfully reached.
        """
        async with self._lock:
            snapshot = list(self._clients.values())

        stale: list[str] = []
        sent_count = 0

        await asyncio.gather(
            *[
                self._broadcast_one(c, data, topic, exclude, stale)
                for c in snapshot
            ],
            return_exceptions=True,
        )

        # Clean up stale connections outside gather
        for cid in stale:
            await self.disconnect(cid)

        sent_count = len(snapshot) - len(stale)
        if exclude:
            sent_count -= len(exclude)
        return max(sent_count, 0)

    async def _broadcast_one(
        self,
        client: ConnectedClient,
        data: dict[str, Any],
        topic: str | None,
        exclude: set[str] | None,
        stale: list[str],
    ) -> None:
        if exclude and client.client_id in exclude:
            return
        if topic and client.subscriptions and topic not in client.subscriptions:
            return
        success = await self._send_json(client.websocket, data)
        if not success:
            stale.append(client.client_id)

    async def broadcast_text(self, text: str) -> int:
        """Broadcast a raw text message to all clients."""
        async with self._lock:
            snapshot = list(self._clients.values())

        stale: list[str] = []
        for client in snapshot:
            try:
                if client.websocket.client_state == WebSocketState.CONNECTED:
                    await client.websocket.send_text(text)
            except Exception:
                stale.append(client.client_id)

        for cid in stale:
            await self.disconnect(cid)
        return len(snapshot) - len(stale)

    # ── Utility ───────────────────────────────────────────────────────────────

    @staticmethod
    async def _send_json(websocket: WebSocket, data: dict[str, Any]) -> bool:
        """Send a JSON payload; returns False on any send error."""
        try:
            if websocket.client_state == WebSocketState.CONNECTED:
                await websocket.send_text(json.dumps(data, default=str))
                return True
        except (WebSocketDisconnect, RuntimeError, Exception) as exc:
            logger.debug("WebSocket send failed: %s", exc)
        return False

    @property
    def active_connection_count(self) -> int:
        return len(self._clients)

    @property
    def client_ids(self) -> list[str]:
        return list(self._clients.keys())

    async def ping_all(self) -> None:
        """Send a heartbeat ping to all connected clients."""
        await self.broadcast(
            {"event": "ping", "timestamp": datetime.now().isoformat()}
        )


# Module-level singleton used by all routers
manager = ConnectionManager()
