"""
IP validation router endpoints.
"""

import logging

from fastapi import APIRouter
from pydantic import BaseModel, IPvAnyAddress

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ip")


class IPCheckRequest(BaseModel):
    """Request model for IP check."""

    ip_address: IPvAnyAddress


@router.post("/check")
async def check_ip(request: IPCheckRequest):
    """Check if the provided IP address is valid."""
    logger.info("Checked IP address: %s", request.ip_address)
    return {
        "message": "The provided IP address is valid.",
        "ip_address": str(request.ip_address),
    }
