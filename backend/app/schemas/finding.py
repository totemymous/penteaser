"""Finding schemas"""

from pydantic import BaseModel
from datetime import datetime
from ..models.finding import FindingType, Severity


class FindingCreate(BaseModel):
    """Create new finding"""
    session_id: int
    title: str
    finding_type: FindingType
    severity: Severity = Severity.INFO
    description: str
    endpoint: str | None = None
    parameter: str | None = None
    dom_path: str | None = None
    evidence: dict | None = None
    reproduction_steps: str | None = None
    remediation: str | None = None
    references: list | None = None


class FindingUpdate(BaseModel):
    """Update finding"""
    verified: bool | None = None
    false_positive: bool | None = None
    severity: Severity | None = None
    remediation: str | None = None


class FindingResponse(BaseModel):
    """Finding response schema"""
    id: int
    session_id: int
    title: str
    finding_type: FindingType
    severity: Severity
    description: str
    endpoint: str | None
    parameter: str | None
    verified: bool
    false_positive: bool
    created_at: datetime

    class Config:
        from_attributes = True


class FindingDetail(FindingResponse):
    """Detailed finding with evidence"""
    dom_path: str | None
    evidence: dict | None
    reproduction_steps: str | None
    remediation: str | None
    references: list | None

    class Config:
        from_attributes = True
