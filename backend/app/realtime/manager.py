"""In-process WebSocket connection manager for live metrics (single-instance safe).

Broadcasts are best-effort and scoped to the authenticated user: publish() never
raises so deep call sites stay safe, and events only reach the owner's sockets.
"""

import json
import logging
import uuid

from fastapi import WebSocket

logger = logging.getLogger("opensignal.realtime")


class ConnectionManager:
    def __init__(self) -> None:
        self._connections: list[tuple[WebSocket, str]] = []

    async def connect(self, ws: WebSocket, user_id: str) -> None:
        await ws.accept()
        self._connections.append((ws, user_id))

    def disconnect(self, ws: WebSocket) -> None:
        self._connections = [(w, uid) for (w, uid) in self._connections if w is not ws]

    async def broadcast_to_user(self, user_id: str, event_type: str, payload: dict) -> None:
        message = json.dumps({"type": event_type, "payload": payload})
        for ws, uid in list(self._connections):
            if uid != user_id:
                continue
            try:
                await ws.send_text(message)
            except Exception:  # noqa: BLE001
                self.disconnect(ws)


manager = ConnectionManager()


async def publish(event_type: str, payload: dict, user_id: uuid.UUID | str | None) -> None:
    if user_id is None:
        return
    try:
        await manager.broadcast_to_user(str(user_id), event_type, payload)
    except Exception:  # noqa: BLE001
        logger.debug("Metrics broadcast failed for %s", event_type)
