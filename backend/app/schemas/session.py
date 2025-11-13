"""Session schemas"""

from pydantic import BaseModel
from datetime import datetime
from ..models.session import SessionStatus


class SessionCreate(BaseModel):
    """Create new testing session"""
    target_id: int
    name: str | None = None
    description: str | None = None
    config: dict | None = None


class SessionResponse(BaseModel):
    """Session response schema"""
    id: int
    target_id: int
    user_id: int | None
    name: str | None
    status: SessionStatus
    started_at: datetime | None
    completed_at: datetime | None
    duration_seconds: int | None
    approval_requested_at: datetime | None
    approved_at: datetime | None
    screenshot_count: int
    interaction_count: int
    created_at: datetime

    class Config:
        from_attributes = True


class SessionApproval(BaseModel):
    """Human approval decision"""
    approved: bool
    notes: str | None = None


class SessionStats(BaseModel):
    """Session statistics"""
    total_sessions: int
    pending: int
    running: int
    pending_approval: int
    completed: int
    failed: int
    cancelled: int
