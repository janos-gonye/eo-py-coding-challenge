"""
IP validation router endpoints.
"""

import logging
import uuid
from datetime import datetime

from fastapi import APIRouter, status
from pydantic import BaseModel, ConfigDict, IPvAnyAddress

from public_api.models import IPCheck
from public_api.queue import queue
from public_api.tasks import process_ip_check

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ip")


class IPCheckRequest(BaseModel):
    """Request model for IP check."""

    ip_address: IPvAnyAddress


class IpCheck(BaseModel):
    """Response model for IP check."""

    id: uuid.UUID
    ip_address: str
    verdict: str | None = None
    task_status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


@router.post("/check", status_code=status.HTTP_202_ACCEPTED, response_model=IpCheck)
def check_ip(request: IPCheckRequest):
    """
    Check if the provided IP address is valid.

    Note: This is defined as a synchronous function (`def`) instead of
    an asynchronous one (`async def`). Both the SQLite database interaction
    via Peewee and pushing tasks into Redis via RQ are blocking I/O operations.
    If this were fully async, these calls would indefinitely block FastAPI's main
    event loop. By remaining synchronous, FastAPI safely dispatches this request
    to a background threadpool, avoiding overall event loop blockage!

    See documentation --> https://fastapi.tiangolo.com/async/
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
