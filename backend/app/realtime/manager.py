"""In-process WebSocket connection manager for live metrics (single-instance safe).

Broadcasts are best-effort: publish() never raises so deep call sites stay safe.
"""

import json
import logging

from fastapi import WebSocket

logger = logging.getLogger("opensignal.realtime")


class ConnectionManager:
    def __init__(self) -> None:
        self._connections: list[WebSocket] = []

    async def connect(self, ws: WebSocket) -> None:
        await ws.accept()
        self._connections.append(ws)

    def disconnect(self, ws: WebSocket) -> None:
        if ws in self._connections:
            self._connections.remove(ws)

    async def broadcast(self, event_type: str, payload: dict) -> None:
        message = json.dumps({"type": event_type, "payload": payload})
        for ws in list(self._connections):
            try:
                await ws.send_text(message)
            except Exception:  # noqa: BLE001
                self.disconnect(ws)


manager = ConnectionManager()


async def publish(event_type: str, payload: dict) -> None:
    try:
        await manager.broadcast(event_type, payload)
    except Exception:  # noqa: BLE001
        logger.debug("Metrics broadcast failed for %s", event_type)
