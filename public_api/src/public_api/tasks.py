"""
Worker tasks for RQ.
"""

import logging
import uuid
import httpx
from google import genai
from peewee import DoesNotExist

from public_api.app_logging import setup_logging
from public_api.models import IPCheck
from public_api.config import settings

setup_logging()

logger = logging.getLogger(__name__)


VERDICT_PROMPT = (
    "CONTEXT: You are a specialized Cybersecurity Analyst. "
    "DATA: {raw_data} "
    "TASK: Analyze the provided IP report and provide a verdict. "
    "REQUIREMENTS: \n"
    "1. Start with a simple verdict: The IP address [ip_adress] "
    "is considered [MALICIOUS], [SUSPICIOUS] or [HARMLESS]. \n"
    "2. Follow with a single-sentence technical justification. \n"
    "3. STRICT CONSTRAINT: Provide raw text only. No markdown, no bolding (**), "
    "no bullet points, and no headers."
)


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


def get_gemini_verdict(raw_data: dict) -> str:
    """
    Get a verdict from Gemini based on the raw report data.
    """
    client = genai.Client(api_key=settings.api_key_gemini)

    prompt = VERDICT_PROMPT.format(raw_data=raw_data)

    logger.info(
        "Requesting Gemini verdict for raw data for IP: %s", raw_data["data"]["id"]
    )
    response = client.models.generate_content(
        model=settings.gemini_model, contents=prompt
    )
    return response.text


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
        verdict = get_gemini_verdict(report_data)

        record.raw_data = report_data
        record.verdict = verdict
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
