"""
IP validation router endpoints.
"""

import json
import logging
import uuid

from fastapi import APIRouter, status
from playhouse.shortcuts import model_to_dict

from public_api.models import IPCheck
from public_api.queue import queue, redis_conn
from public_api.tasks import process_ip_check
from public_api import schemas
from public_api.ws import IP_CHECK_STATUS_UPDATES

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ip")


@router.post(
    "/check", status_code=status.HTTP_202_ACCEPTED, response_model=schemas.IpCheck
)
def check_ip(request: schemas.IPCheckRequest):
    """
    Start IP check process.
    """
    record_id = uuid.uuid4()

    ip_check = IPCheck.create(id=record_id, ip_address=str(request.ip_address))

    queue.enqueue(process_ip_check, str(record_id), str(request.ip_address))

    redis_conn.publish(
        IP_CHECK_STATUS_UPDATES, json.dumps(model_to_dict(ip_check), default=str)
    )

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
