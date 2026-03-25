"""
Worker tasks for RQ.
"""

import logging
import uuid
from peewee import DoesNotExist

from public_api.models import IPCheck

logger = logging.getLogger(__name__)


def process_ip_check(record_id: str, ip_address: str) -> None:
    """
    Background task to check an IP address.
    """
    logger.info("Processing IP: %s (Record: %s)", ip_address, record_id)

    try:
        record = IPCheck.get_by_id(uuid.UUID(record_id))
        record.task_status = "processing"
        record.save()

        record.task_status = "success"
        record.save()
        logger.info("Successfully processed IP: %s", ip_address)
    except Exception as e:  # pylint: disable=broad-exception-caught
        logger.error("Failed to process IP %s: %s", ip_address, e)
        try:
            record = IPCheck.get_by_id(uuid.UUID(record_id))
            record.task_status = "failed"
            record.save()
        except DoesNotExist:
            pass
