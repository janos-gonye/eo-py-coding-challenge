"""
Tests for background worker tasks.
"""

import uuid
from unittest.mock import MagicMock, patch

import pytest
from public_api.models import IPCheck
from public_api.tasks import process_ip_check, get_virustotal_report, get_gemini_verdict


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


def test_get_gemini_verdict_success(caplog):
    """Test successful retrieval of Gemini verdict."""
    mock_response = MagicMock()
    mock_response.text = "This IP is harmless."

    with patch("google.genai.Client") as mock_client_class:
        mock_client = mock_client_class.return_value
        mock_client.models.generate_content.return_value = mock_response

        verdict = get_gemini_verdict({"data": {"id": "1.1.1.1", "field": "some data"}})
        assert verdict == "This IP is harmless."
        mock_client.models.generate_content.assert_called_once()
        assert "Requesting Gemini verdict for raw data for IP: 1.1.1.1" in caplog.text


def test_get_gemini_verdict_failure(caplog):
    """Test Gemini failure in get_gemini_verdict."""
    with patch("google.genai.Client") as mock_client_class:
        mock_client = mock_client_class.return_value
        mock_client.models.generate_content.side_effect = Exception("Gemini API Error")

        with pytest.raises(Exception):
            get_gemini_verdict({"data": {"id": "1.1.1.1", "field": "some data"}})
        assert "Requesting Gemini verdict for raw data for IP: 1.1.1.1" in caplog.text


def test_process_ip_check_success(caplog):
    """Test successful processing of an IP check task."""
    ip_address = "1.1.1.1"
    record = IPCheck.create(ip_address=ip_address, task_status="pending")
    record_id = str(record.id)

    mock_report = {"harmless": True}
    mock_verdict = "This IP is harmless."

    with patch(
        "public_api.tasks.get_virustotal_report", return_value=mock_report
    ) as mock_get_report, patch(
        "public_api.tasks.get_gemini_verdict", return_value=mock_verdict
    ) as mock_get_verdict:
        process_ip_check(record_id, ip_address)

        mock_get_report.assert_called_once_with(ip_address)
        mock_get_verdict.assert_called_once_with(mock_report)
        updated_record = IPCheck.get_by_id(record.id)
        assert updated_record.task_status == "success"
        assert updated_record.raw_data == mock_report
        assert updated_record.verdict == mock_verdict

        assert f"Processing IP: {ip_address} (Record: {record_id})" in caplog.text
        assert (
            f"Successfully processed IP and stored record: {ip_address}" in caplog.text
        )


def test_process_ip_check_gemini_failure(caplog):
    """Test task failure when the Gemini call fails."""
    ip_address = "1.1.1.1"
    record = IPCheck.create(ip_address=ip_address, task_status="pending")
    record_id = str(record.id)

    mock_report = {"harmless": True}

    with patch(
        "public_api.tasks.get_virustotal_report", return_value=mock_report
    ), patch(
        "public_api.tasks.get_gemini_verdict", side_effect=Exception("Gemini Error")
    ):
        process_ip_check(record_id, ip_address)

        updated_record = IPCheck.get_by_id(record.id)
        assert updated_record.task_status == "failed"
        assert f"Failed to process IP {ip_address}: Gemini Error" in caplog.text


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
