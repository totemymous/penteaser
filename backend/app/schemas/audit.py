"""Audit log schemas"""

from pydantic import BaseModel
from datetime import datetime


class AuditLogResponse(BaseModel):
    """Audit log response schema"""
    id: int
    user_id: int | None
    action: str
    resource_type: str
    resource_id: int | None
    details: dict | None
    consent_reference: str | None
    ip_address: str | None
    created_at: datetime

    class Config:
        from_attributes = True
