"""
IP validation router endpoints.
"""

import logging
import uuid
from datetime import datetime

from fastapi import APIRouter, status

from public_api.models import IPCheck
from public_api.queue import queue
from public_api.tasks import process_ip_check
from public_api import schemas


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ip")


@router.post("/check", status_code=status.HTTP_202_ACCEPTED, response_model=schemas.IpCheck)
def check_ip(request: schemas.IPCheckRequest):
    """
    Start IP check process.
    """
    record_id = uuid.uuid4()

    ip_check = IPCheck.create(id=record_id, ip_address=str(request.ip_address))

    queue.enqueue(process_ip_check, str(record_id), str(request.ip_address))

    logger.info(
        "[Task Queued] IP: %s | RecordID: %s | Status: Pending",
        request.ip_address,
        record_id,
    )

    return ip_check


@router.get("/list", response_model=list[schemas.IpCheck])
def list_ip_checks():
    """
    List all IP check records.
    """
    return list(IPCheck.select().order_by(IPCheck.created_at.desc()))
