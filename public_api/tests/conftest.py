"""
Shared pytest fixtures and configuration.
"""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from public_api.main import app
from public_api.models import IPCheck
from public_api.db import db


@pytest.fixture
def client():
    """Test client fixture to handle FastAPI lifespan events."""
    # Use context manager to trigger FastAPI lifespan
    with TestClient(app) as c:
        yield c


@pytest.fixture(autouse=True)
def setup_test_db():
    """Setup test database using the app db."""
    db.connect(reuse_if_open=True)
    db.create_tables([IPCheck])
    yield
    db.drop_tables([IPCheck])
    db.close()


@pytest.fixture(autouse=True)
def mock_redis():
    """Mock redis and aioredis globally for all tests."""
    with patch("redis.Redis.from_url") as mock_sync_from_url, patch(
        "redis.asyncio.from_url"
    ) as mock_async_from_url:

        sync_conn = MagicMock()
        mock_sync_from_url.return_value = sync_conn

        async_conn = MagicMock()
        mock_async_from_url.return_value = async_conn

        async_pubsub = MagicMock()
        async_conn.pubsub.return_value = async_pubsub

        async def mock_listen():
            yield {
                "type": "subscribe",
                "channel": b"ip_check_status_updates",
                "data": 1,
            }
            while True:
                await asyncio.sleep(0.1)

        async_pubsub.listen.side_effect = mock_listen

        # Mock async connect/disconnect/etc
        async_conn.subscribe = AsyncMock()
        async_conn.unsubscribe = AsyncMock()
        async_conn.aclose = AsyncMock()
        async_pubsub.subscribe = AsyncMock()
        async_pubsub.unsubscribe = AsyncMock()

        # Handle the one in queue.py and tasks.py and routers/ip.py
        with patch("public_api.queue.redis_conn", sync_conn), patch(
            "public_api.tasks.redis_conn", sync_conn
        ), patch("public_api.routers.ip.redis_conn", sync_conn):
            yield sync_conn
