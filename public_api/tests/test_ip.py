"""
Tests for the IP validation endpoints.
"""

import logging
import uuid
from datetime import datetime, timezone, timedelta
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from public_api.main import app
from public_api.models import IPCheck
from public_api.tasks import process_ip_check


@pytest.fixture
def client():
    """Test client fixture to handle FastAPI lifespan events."""
    # Use context manager to trigger FastAPI lifespan
    with TestClient(app) as c:
        yield c


@pytest.fixture
def mock_queue():
    """Fixture to mock the RQ queue for background tasks."""
    with patch("public_api.routers.ip.queue") as mock_q:
        yield mock_q


@pytest.mark.parametrize(
    "ip_address",
    [
        "0.0.0.0",
        "192.168.1.1",
        "8.8.8.8",
        "2001:4860:4860::8888",
        "2001:db8::2:1",
    ],
)
def test_check_ip_valid(
    ip_address, caplog, client, mock_queue
):  # pylint: disable=redefined-outer-name
    """Test valid IP addresses."""
    caplog.set_level(logging.INFO)
    response = client.post("/ip/check", json={"ip_address": ip_address})

    assert response.status_code == 202
    data = response.json()
    assert data["ip_address"] == ip_address
    assert "id" in data
    record_id = data["id"]

    record = IPCheck.get_by_id(uuid.UUID(record_id))
    assert record.ip_address == ip_address

    mock_queue.enqueue.assert_called_once_with(process_ip_check, record_id, ip_address)

    assert (
        f"[Task Queued] IP: {ip_address} | RecordID: {record_id} | Status: Pending"
        in caplog.text
    )


@pytest.mark.parametrize(
    "ip_address", ["invalid_ip", "", "   ", None, "256.256.256.256"]
)
def test_check_ip_invalid(
    ip_address, caplog, client, mock_queue
):  # pylint: disable=redefined-outer-name
    """Test invalid IP addresses."""
    caplog.set_level(logging.INFO)
    response = client.post("/ip/check", json={"ip_address": ip_address})

    assert response.status_code == 422
    assert (
        response.json()["detail"][0]["msg"]
        == "value is not a valid IPv4 or IPv6 address"
    )
    assert "[Task Queued]" not in caplog.text
    mock_queue.enqueue.assert_not_called()


def test_list_ip_checks(client):  # pylint: disable=redefined-outer-name
    """Test listing IP check records."""
    now = datetime.now(timezone.utc)
    IPCheck.create(
        id=uuid.uuid4(), ip_address="1.1.1.1", created_at=now - timedelta(minutes=1)
    )
    IPCheck.create(id=uuid.uuid4(), ip_address="2.2.2.2", created_at=now)

    response = client.get("/ip/list")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 2

    # The newest should be first.
    record_ips = [item["ip_address"] for item in data]
    # "2.2.2.2" should appear before "1.1.1.1"
    idx2 = record_ips.index("2.2.2.2")
    idx1 = record_ips.index("1.1.1.1")
    assert idx2 < idx1
