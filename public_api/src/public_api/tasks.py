"""
Worker tasks for RQ.
"""

import logging
import uuid
import httpx
from peewee import DoesNotExist

from public_api.app_logging import setup_logging
from public_api.models import IPCheck
from public_api.config import settings

setup_logging()

logger = logging.getLogger(__name__)


def get_virustotal_report(ip_address: str) -> dict:
    """
    Fetch the VirusTotal report for a given IP address.
    """
    url = settings.virustotal_endpoint.format(ip=ip_address)
    headers = {"x-apikey": settings.api_key_virustotal}

    logger.info("Requesting VirusTotal report for IP: %s", ip_address)
    with httpx.Client() as client:
        response = client.get(url, headers=headers)
        response.raise_for_status()
        return response.json()


def process_ip_check(record_id: str, ip_address: str) -> None:
    """
    Background task to check an IP address.
    """
    logger.info("Processing IP: %s (Record: %s)", ip_address, record_id)

    try:
        record = IPCheck.get_by_id(uuid.UUID(record_id))
        record.task_status = "processing"
        record.save()

        report_data = get_virustotal_report(ip_address)

        record.raw_data = report_data
        record.task_status = "success"
        record.save()
        logger.info("Successfully processed IP and stored record: %s", ip_address)

    except Exception as e:  # pylint: disable=broad-exception-caught
        logger.error("Failed to process IP %s: %s", ip_address, e, exc_info=True)
        try:
            record = IPCheck.get_by_id(uuid.UUID(record_id))
            record.task_status = "failed"
            record.save()
        except DoesNotExist:
            logger.error("Record %s not found for error status update", record_id)
