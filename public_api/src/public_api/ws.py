"""
WebSocket management and event broadcasting.
"""

import json
import logging
import redis.asyncio as aioredis
from fastapi import WebSocket, WebSocketDisconnect

from public_api.config import settings

IP_CHECK_STATUS_UPDATES = "ip_check_status_updates"


logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manages active WebSocket connections."""

    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        """Accept a new WebSocket connection."""
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        """Remove a WebSocket connection."""
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        """Send a message to all connected clients."""
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:  # pylint: disable=broad-exception-caught
                logger.error(
                    "Failed to send message to client %s", message, exc_info=True
                )


manager = ConnectionManager()


async def redis_listener():
    """Listen for IP status updates from Redis and broadcast to clients."""
    async_redis = aioredis.from_url(settings.redis_url)
    pubsub = async_redis.pubsub()
    await pubsub.subscribe(IP_CHECK_STATUS_UPDATES)
    try:
        async for message in pubsub.listen():
            if message["type"] == "message":
                data = json.loads(message["data"])
                await manager.broadcast(data)
    except Exception:  # pylint: disable=broad-exception-caught
        logger.error("Failed to process IP check status update", exc_info=True)
    finally:
        await pubsub.unsubscribe(IP_CHECK_STATUS_UPDATES)
        await async_redis.aclose()


async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates."""
    await manager.connect(websocket)
    try:
        while True:
            # Keep the connection alive by waiting for any potential incoming data (not expected)
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
