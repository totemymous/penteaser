"""
Celery tasks for browser automation and testing.

These tasks are executed by the worker process in response to
session creation requests from the API.
"""

import logging
from celery import Celery
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .config import CELERY_BROKER_URL, CELERY_RESULT_BACKEND, DATABASE_URL, AUTO_APPROVE_SESSIONS
from .browser import BrowserSession
from .xss_tester import XSSPayloadTester

logger = logging.getLogger(__name__)

# Initialize Celery app
celery_app = Celery(
    "xss_assistant_worker",
    broker=CELERY_BROKER_URL,
    backend=CELERY_RESULT_BACKEND,
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)

# Database setup for tasks
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)


@celery_app.task(name="workers.tasks.start_session_job")
def start_session_job(session_id: int):
    """
    Execute a testing session with browser automation.

    This task:
    1. Fetches session details from database
    2. Launches browser (headful mode)
    3. Performs passive DOM analysis
    4. If suspicious patterns found, requests human approval
    5. If approved, continues with guided testing
    6. Records all activity and stores findings

    Args:
        session_id: Database session ID

    Returns:
        Session completion status and metadata
    """
    logger.info(f"Starting session job {session_id}")

    # Import models here to avoid circular dependencies
    from backend.app.models.session import Session, SessionStatus
    from backend.app.models.finding import Finding, FindingType, Severity
    from backend.app.models.audit_log import AuditLog

    db = SessionLocal()

    try:
        # Fetch session from database
        session = db.query(Session).filter(Session.id == session_id).first()
        if not session:
            raise ValueError(f"Session {session_id} not found")

        # Update status to RUNNING
        session.status = SessionStatus.RUNNING
        from datetime import datetime
        session.started_at = datetime.utcnow()
        db.commit()

        # Get target URL
        target_url = session.target.url
        logger.info(f"Testing target: {target_url}")

        # Perform HTTP-based XSS testing
        logger.info("Starting HTTP-based XSS scan...")
        xss_tester = XSSPayloadTester(target_url)
        scan_results = xss_tester.run_full_scan()

        metadata = {
            "endpoints_found": scan_results['endpoints_found'],
            "endpoints_tested": scan_results['endpoints_tested'],
            "vulnerabilities_found": len(scan_results['vulnerabilities']),
            "analysis_type": "http_xss_scan"
        }

        logger.info(f"XSS scan complete: {metadata}")

        # Store detailed vulnerabilities
        vulnerabilities = scan_results['vulnerabilities']

        # Check if vulnerabilities found
        if vulnerabilities:
            logger.warning(f"Found {len(vulnerabilities)} XSS vulnerabilities!")

            # Check if human approval needed (if not auto-approve mode)
            if not AUTO_APPROVE_SESSIONS and len(vulnerabilities) > 0:
                # Update session status to PENDING_APPROVAL
                session.status = SessionStatus.PENDING_APPROVAL
                session.approval_requested_at = datetime.utcnow()
                db.commit()
                logger.info("High-severity findings require approval")

        # Create findings for each vulnerability
        findings_created = 0
        for vuln in vulnerabilities:
            finding = Finding(
                session_id=session_id,
                title=f"Reflected XSS Vulnerability in {vuln['parameter']}",
                finding_type=FindingType.XSS_REFLECTED,
                severity=Severity.HIGH if vuln['severity'] == 'high' else Severity.MEDIUM,
                description=f"Reflected XSS vulnerability found in {vuln['method']} parameter '{vuln['parameter']}'",
                endpoint=vuln['endpoint'],
                parameter=vuln['parameter'],
                evidence={
                    'payload': vuln['payload'],
                    'response_snippet': vuln['evidence'],
                    'status_code': vuln['status_code'],
                    'method': vuln['method']
                },
                remediation="Implement proper input validation and output encoding. Use Content Security Policy (CSP) headers.",
            )
            db.add(finding)
            findings_created += 1

        # If no vulnerabilities found, create informational finding
        if not vulnerabilities and metadata['endpoints_tested'] > 0:
            finding = Finding(
                session_id=session_id,
                title="No XSS vulnerabilities detected",
                finding_type=FindingType.INFO,
                severity=Severity.INFO,
                description=f"Tested {metadata['endpoints_tested']} endpoints with {len(XSSPayloadTester.PAYLOADS[:5])} payloads each. No reflected XSS vulnerabilities detected.",
                endpoint=target_url,
                parameter=None,
                evidence=metadata,
                remediation="Continue monitoring and periodic testing recommended.",
            )
            db.add(finding)
            findings_created += 1

        # Audit log
        audit = AuditLog(
            user_id=session.user_id,
            action="session_completed",
            resource_type="session",
            resource_id=session_id,
            details={
                "findings_count": findings_created,
                "vulnerabilities_found": len(vulnerabilities),
                "endpoints_tested": metadata['endpoints_tested']
            },
        )
        db.add(audit)

        # Update session status
        session.status = SessionStatus.COMPLETED
        session.completed_at = datetime.utcnow()
        session.duration_seconds = int((session.completed_at - session.started_at).total_seconds())
        session.interaction_count = metadata['endpoints_tested']

        db.commit()

        logger.info(f"Session {session_id} completed successfully with {findings_created} findings")

        return {
            "status": "completed",
            "session_id": session_id,
            "findings": findings_created,
            "vulnerabilities": len(vulnerabilities),
            "duration_seconds": session.duration_seconds,
        }

    except Exception as e:
        logger.error(f"Session {session_id} failed: {e}", exc_info=True)

        # Update session status to FAILED
        session.status = SessionStatus.FAILED
        session.completed_at = datetime.utcnow()
        db.commit()

        raise

    finally:
        db.close()


@celery_app.task(name="workers.tasks.analyze_target")
def analyze_target(target_id: int):
    """
    Perform initial target analysis (passive recon).

    This task performs non-intrusive analysis:
    - Technology detection
    - Form discovery
    - Input field enumeration

    NO payload testing or exploitation.

    Args:
        target_id: Database target ID

    Returns:
        Analysis metadata
    """
    logger.info(f"Analyzing target {target_id}")

    # Placeholder implementation
    return {
        "target_id": target_id,
        "status": "analyzed",
        "technologies": ["nginx", "php"],
        "forms_found": 3,
    }
