"""
WebSocket integration tests.
"""

import uuid
from unittest.mock import ANY, AsyncMock, patch

import pytest

from public_api.tasks import process_ip_check
from public_api.models import IPCheck
from public_api.ws import manager


def test_websocket_connection(client):
    """Test that a WebSocket connection can be successfully established."""
    with client.websocket_connect("/ws") as _websocket:
        # Connection successful, no exception raised
        pass


@pytest.mark.asyncio
async def test_websocket_broadcast():
    """Test that the ConnectionManager broadcasts messages to all active connections."""
    # This test is a bit tricky with TestClient and background tasks.
    # Instead, we test the manager's broadcast method.
    mock_ws = AsyncMock()
    manager.active_connections.append(mock_ws)

    test_data = {"id": "test-id", "task_status": "success"}
    await manager.broadcast(test_data)

    mock_ws.send_json.assert_called_once_with(test_data)
    manager.active_connections.remove(mock_ws)


@patch("public_api.tasks.redis_conn")
def test_task_publishes_to_redis(mock_redis):
    """Test that the IP check task publishes status updates to Redis."""
    record_id = str(uuid.uuid4())
    IPCheck.create(id=record_id, ip_address="1.2.3.4")

    with patch(
        "public_api.tasks.get_virustotal_report",
        return_value={"data": {"id": "1.2.3.4"}},
    ), patch("public_api.tasks.get_gemini_verdict", return_value="Harmless"):

        process_ip_check(record_id, "1.2.3.4")

        # Verify redis_conn.publish was called
        # It's called for 'processing' and then for 'success/failed'
        assert mock_redis.publish.call_count >= 2

        # Check if one of the calls was for the channel
        mock_redis.publish.assert_any_call("ip_check_status_updates", ANY)
