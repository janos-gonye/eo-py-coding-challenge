"""
Data schemas and Pydantic models.
"""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, IPvAnyAddress


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
