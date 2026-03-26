"""
Tests for background worker tasks.
"""

import uuid
from unittest.mock import MagicMock, patch

import pytest
import httpx
from public_api.models import IPCheck
from public_api.tasks import process_ip_check, get_virustotal_report


@pytest.mark.parametrize("ip_address", ["1.1.1.1", "8.8.8.8"])
def test_get_virustotal_report_success(ip_address, caplog):
    """Test successful retrieval of VirusTotal report."""
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "data": {"attributes": {"last_analysis_stats": {"malicious": 0}}}
    }

    with patch("httpx.Client.get", return_value=mock_response) as mock_get:
        report = get_virustotal_report(ip_address)
        assert report == {
            "data": {"attributes": {"last_analysis_stats": {"malicious": 0}}}
        }
        mock_get.assert_called_once()
        assert f"Requesting VirusTotal report for IP: {ip_address}" in caplog.text


def test_get_virustotal_report_failure(caplog):
    """Test API failure in get_virustotal_report."""
    with patch(
        "httpx.Client.get",
        side_effect=httpx.HTTPStatusError(
            "Error", request=MagicMock(), response=MagicMock()
        ),
    ):
        with pytest.raises(Exception):
            get_virustotal_report("1.1.1.1")
        assert "Requesting VirusTotal report for IP: 1.1.1.1" in caplog.text


def test_process_ip_check_success(caplog):
    """Test successful processing of an IP check task."""
    ip_address = "1.1.1.1"
    record = IPCheck.create(ip_address=ip_address, task_status="pending")
    record_id = str(record.id)

    mock_report = {"harmless": True}

    with patch(
        "public_api.tasks.get_virustotal_report", return_value=mock_report
    ) as mock_get_report:
        process_ip_check(record_id, ip_address)

        updated_record = IPCheck.get_by_id(record.id)
        assert updated_record.task_status == "success"
        assert updated_record.raw_data == mock_report
        mock_get_report.assert_called_once_with(ip_address)

        assert f"Processing IP: {ip_address} (Record: {record_id})" in caplog.text
        assert (
            f"Successfully processed IP and stored record: {ip_address}" in caplog.text
        )


def test_process_ip_check_api_failure(caplog):
    """Test task failure when the API call fails."""
    ip_address = "1.1.1.1"
    record = IPCheck.create(ip_address=ip_address, task_status="pending")
    record_id = str(record.id)

    with patch(
        "public_api.tasks.get_virustotal_report", side_effect=Exception("API Error")
    ):
        process_ip_check(record_id, ip_address)

        updated_record = IPCheck.get_by_id(record.id)
        assert updated_record.task_status == "failed"
        assert f"Failed to process IP {ip_address}: API Error" in caplog.text


def test_process_ip_check_record_not_found(caplog):
    """Test task handling when the record ID does not exist."""
    random_id = str(uuid.uuid4())
    # Should not raise exception, but log error
    process_ip_check(random_id, "1.1.1.1")
    assert f"Record {random_id} not found for error status update" in caplog.text
