"""Report generation endpoints"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session as DBSession
from datetime import datetime

from ..database import get_db
from ..models.session import Session
from ..models.finding import Finding
from ..models.target import Target
from ..schemas.report import ReportCreate, ReportResponse, ReportExport
from ..schemas.finding import FindingDetail

router = APIRouter(prefix="/api/v1/reports", tags=["reports"])


@router.post("/", response_model=ReportResponse)
async def generate_report(
    report_data: ReportCreate,
    db: DBSession = Depends(get_db)
):
    """
    Generate a report for a completed session.

    Returns structured report data with findings and session details.
    """
    # Fetch session
    session = db.query(Session).filter(Session.id == report_data.session_id).first()
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )

    # Fetch target
    target = db.query(Target).filter(Target.id == session.target_id).first()

    # Fetch findings
    findings = db.query(Finding).filter(Finding.session_id == session.id).all()

    # Build response
    report = ReportResponse(
        session_id=session.id,
        target_name=target.name,
        target_url=target.url,
        session_name=session.name,
        started_at=session.started_at,
        completed_at=session.completed_at,
        duration_seconds=session.duration_seconds or 0,
        findings_count=len(findings),
        findings=[FindingDetail.from_orm(f) for f in findings],
        generated_at=datetime.utcnow()
    )

    return report


@router.post("/export", response_model=ReportExport)
async def export_report(
    report_data: ReportCreate,
    db: DBSession = Depends(get_db)
):
    """
    Export report to Markdown or PDF format.

    Generates a formatted report file that can be downloaded.
    """
    # Generate report data first
    session = db.query(Session).filter(Session.id == report_data.session_id).first()
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )

    target = db.query(Target).filter(Target.id == session.target_id).first()
    findings = db.query(Finding).filter(Finding.session_id == session.id).all()

    if report_data.format == "markdown":
        content = _generate_markdown_report(session, target, findings, report_data)
        filename = f"report_session_{session.id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.md"
    elif report_data.format == "pdf":
        # TODO: Implement PDF generation (requires reportlab or weasyprint)
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="PDF export not yet implemented. Use markdown format."
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported format: {report_data.format}. Use 'markdown' or 'pdf'."
        )

    return ReportExport(
        format=report_data.format,
        content=content,
        filename=filename
    )


def _generate_markdown_report(session, target, findings, config: ReportCreate) -> str:
    """Generate Markdown formatted report"""

    # Header
    markdown = f"""# Security Testing Report

## Session Information

- **Session ID**: {session.id}
- **Session Name**: {session.name or 'N/A'}
- **Target**: {target.name}
- **Target URL**: {target.url}
- **Started**: {session.started_at.isoformat() if session.started_at else 'N/A'}
- **Completed**: {session.completed_at.isoformat() if session.completed_at else 'N/A'}
- **Duration**: {session.duration_seconds or 0} seconds
- **Status**: {session.status}

---

## Executive Summary

- **Total Findings**: {len(findings)}
"""

    # Count by severity
    severity_counts = {}
    for finding in findings:
        severity_counts[finding.severity.value] = severity_counts.get(finding.severity.value, 0) + 1

    markdown += "\n### Findings by Severity\n\n"
    for severity in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW', 'INFO']:
        count = severity_counts.get(severity.lower(), 0)
        markdown += f"- **{severity}**: {count}\n"

    markdown += "\n---\n\n## Detailed Findings\n\n"

    # Findings
    for idx, finding in enumerate(findings, 1):
        markdown += f"### Finding #{idx}: {finding.title}\n\n"
        markdown += f"- **Type**: {finding.finding_type.value}\n"
        markdown += f"- **Severity**: {finding.severity.value.upper()}\n"
        markdown += f"- **Endpoint**: {finding.endpoint or 'N/A'}\n"
        markdown += f"- **Parameter**: {finding.parameter or 'N/A'}\n"
        markdown += f"- **Verified**: {'Yes' if finding.verified else 'No'}\n\n"

        markdown += f"**Description:**\n\n{finding.description}\n\n"

        if config.include_evidence and finding.reproduction_steps:
            markdown += f"**Reproduction Steps:**\n\n{finding.reproduction_steps}\n\n"

        if config.include_remediation and finding.remediation:
            markdown += f"**Remediation:**\n\n{finding.remediation}\n\n"

        if finding.references:
            markdown += "**References:**\n\n"
            for ref in finding.references:
                markdown += f"- {ref}\n"

        markdown += "\n---\n\n"

    # Footer
    markdown += f"""
## Report Metadata

- **Generated**: {datetime.utcnow().isoformat()}
- **Tool**: XSS Assistant v0.1.0
- **Report Format**: Markdown

---

**Disclaimer**: This report is generated for authorized security testing purposes only.
The information contained herein should be treated as confidential and used solely for
improving the security posture of the tested application.
"""

    return markdown


@router.get("/sessions/{session_id}", response_model=ReportResponse)
async def get_session_report(
    session_id: int,
    db: DBSession = Depends(get_db)
):
    """Get report for a specific session"""
    report_data = ReportCreate(session_id=session_id)
    return await generate_report(report_data, db)
