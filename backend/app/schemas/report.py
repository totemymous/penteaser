"""Report schemas"""

from pydantic import BaseModel
from datetime import datetime
from typing import List
from .finding import FindingDetail


class ReportCreate(BaseModel):
    """Create report for session"""
    session_id: int
    format: str = "markdown"  # markdown or pdf
    include_evidence: bool = True
    include_remediation: bool = True


class ReportResponse(BaseModel):
    """Report response schema"""
    session_id: int
    target_name: str
    target_url: str
    session_name: str | None
    started_at: datetime
    completed_at: datetime
    duration_seconds: int
    findings_count: int
    findings: List[FindingDetail]
    generated_at: datetime


class ReportExport(BaseModel):
    """Exported report"""
    format: str
    content: str
    filename: str
