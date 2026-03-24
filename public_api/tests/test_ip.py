"""
Tests for the IP validation endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from public_api.main import app

client = TestClient(app)


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
def test_check_ip_valid(ip_address, caplog):
    """Test valid IP addresses."""
    response = client.post("/ip/check", json={"ip_address": ip_address})

    assert response.status_code == 200
    assert response.json()["message"] == "The provided IP address is valid."
    assert f"Checked IP address: {ip_address}" in caplog.text


@pytest.mark.parametrize(
    "ip_address", ["invalid_ip", "", "   ", None, "256.256.256.256"]
)
def test_check_ip_invalid(ip_address, caplog):
    """Test invalid IP addresses."""
    response = client.post("/ip/check", json={"ip_address": ip_address})

    assert response.status_code == 422
    assert (
        response.json()["detail"][0]["msg"]
        == "value is not a valid IPv4 or IPv6 address"
    )
    assert f"Checked IP address: {ip_address}" not in caplog.text
