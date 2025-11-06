"""
Celery tasks for browser automation and testing.

These tasks are executed by the worker process in response to
session creation requests from the API.
"""

import logging
from celery import Celery
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .config import CELERY_BROKER_URL, CELERY_RESULT_BACKEND, DATABASE_URL
from .browser import BrowserSession

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

        # Start browser session (async wrapper needed - simplified for scaffold)
        # In real implementation, use asyncio.run() or async task executor
        logger.info("Launching browser...")

        # Placeholder for browser automation (real implementation would be async)
        # browser = BrowserSession(session_id, target_url, session.config)
        # await browser.start()
        # metadata = await browser.analyze_dom()

        # Simulated DOM analysis result
        metadata = {
            "form_count": 3,
            "input_count": 5,
            "suspicious_inputs": [
                {"name": "search", "type": "text", "reason": "text_input_without_sanitization_check"}
            ],
            "analysis_type": "passive_dom_fingerprint"
        }

        logger.info(f"DOM analysis complete: {metadata}")

        # Check if suspicious patterns found
        if metadata.get("suspicious_inputs"):
            logger.warning("Suspicious patterns detected - requesting human approval")

            # Update session status to PENDING_APPROVAL
            session.status = SessionStatus.PENDING_APPROVAL
            session.approval_requested_at = datetime.utcnow()
            db.commit()

            # In real implementation: wait for approval via Redis pub/sub or polling
            # For scaffold: log and continue
            logger.info("Waiting for human approval (simulated)")

            # Simulate approval (in real implementation, this would wait)
            # approved = await browser.wait_for_approval()
            approved = False  # For scaffold, do not auto-approve

            if not approved:
                logger.info("Session not approved - ending")
                session.status = SessionStatus.COMPLETED
                session.completed_at = datetime.utcnow()
                db.commit()
                return {"status": "completed", "approved": False}

        # If approved or no approval needed, continue with testing
        # (This section would contain guided testing logic)
        logger.info("Session approved - would continue with guided testing")

        # Create finding (example)
        finding = Finding(
            session_id=session_id,
            title="Potential XSS vector in search parameter",
            finding_type=FindingType.INPUT_VALIDATION,
            severity=Severity.INFO,
            description="Search input lacks visible sanitization attributes",
            endpoint=target_url,
            parameter="search",
            evidence=metadata,
            remediation="Implement input validation and output encoding",
        )
        db.add(finding)

        # Audit log
        audit = AuditLog(
            user_id=session.user_id,
            action="session_completed",
            resource_type="session",
            resource_id=session_id,
            details={"findings_count": 1},
        )
        db.add(audit)

        # Update session status
        session.status = SessionStatus.COMPLETED
        session.completed_at = datetime.utcnow()
        session.duration_seconds = int((session.completed_at - session.started_at).total_seconds())
        session.interaction_count = 1

        db.commit()

        logger.info(f"Session {session_id} completed successfully")

        return {
            "status": "completed",
            "session_id": session_id,
            "findings": 1,
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
