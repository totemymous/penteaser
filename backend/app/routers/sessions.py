"""Session management endpoints for testing operations"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session as DBSession
from typing import List
from datetime import datetime

from ..database import get_db
from ..models.session import Session, SessionStatus
from ..models.target import Target
from ..models.audit_log import AuditLog
from ..config import settings
from ..schemas.session import SessionCreate, SessionResponse, SessionApproval

router = APIRouter(prefix="/api/v1/sessions", tags=["sessions"])


@router.post("/", response_model=SessionResponse, status_code=status.HTTP_201_CREATED)
async def create_session(
    session_data: SessionCreate,
    db: DBSession = Depends(get_db)
):
    """
    Create a new testing session.

    If REQUIRE_CONSENT=true, target must have valid consent.
    If REQUIRE_CONSENT=false (lab mode), consent check is skipped.
    """
    # Verify target exists
    target = db.query(Target).filter(
        Target.id == session_data.target_id,
        Target.is_active == True
    ).first()

    if not target:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Target not found or inactive"
        )

    # Check consent only if required
    if settings.require_consent:
        if not target.is_authorized:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Target not authorized. Valid consent required (REQUIRE_CONSENT=true)."
            )

        # Check consent expiry
        if target.authorization_expires and target.authorization_expires <= datetime.utcnow():
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Target authorization has expired"
            )

    # Create session
    db_session = Session(
        target_id=session_data.target_id,
        user_id=None,  # TODO: Get from authenticated user
        name=session_data.name,
        description=session_data.description,
        status=SessionStatus.PENDING,
        config=session_data.config,
    )
    db.add(db_session)

    # Audit log (only if minimal_logging is false)
    if not settings.minimal_logging:
        audit = AuditLog(
            user_id=None,  # TODO: Get from authenticated user
            action="session_created",
            resource_type="session",
            resource_id=db_session.id,
            details={
                "target_id": target.id,
                "target_url": target.url,
                "consent_required": settings.require_consent,
            },
            consent_reference=f"consent_{target.consent_id}" if target.consent_id else None,
        )
        db.add(audit)

    db.commit()
    db.refresh(db_session)

    # Enqueue job to worker (Celery task)
    try:
        import sys
        from pathlib import Path
        # Add parent directory to path to access workers module
        parent_dir = str(Path(__file__).parent.parent.parent.parent)
        if parent_dir not in sys.path:
            sys.path.insert(0, parent_dir)

        from workers.tasks import start_session_job
        start_session_job.delay(db_session.id)
    except Exception as e:
        # If Celery/Redis not available, log but don't fail
        print(f"Warning: Could not enqueue worker task: {e}")
        print("Session created but worker not started. Check Celery/Redis configuration.")

    return db_session


@router.get("/", response_model=List[SessionResponse])
async def list_sessions(
    skip: int = 0,
    limit: int = 100,
    status_filter: SessionStatus | None = None,
    db: DBSession = Depends(get_db)
):
    """
    List all sessions with optional status filtering.

    Returns paginated list of sessions.
    """
    query = db.query(Session)

    if status_filter:
        query = query.filter(Session.status == status_filter)

    sessions = query.order_by(Session.created_at.desc()).offset(skip).limit(limit).all()
    return sessions


@router.get("/{session_id}", response_model=SessionResponse)
async def get_session(
    session_id: int,
    db: DBSession = Depends(get_db)
):
    """Get session details by ID"""
    session = db.query(Session).filter(Session.id == session_id).first()
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    return session


@router.post("/{session_id}/approve", response_model=SessionResponse)
async def approve_session(
    session_id: int,
    approval: SessionApproval,
    db: DBSession = Depends(get_db)
):
    """
    Human-in-the-loop approval for deep testing.

    When worker requests approval (status=PENDING_APPROVAL),
    operator can approve or reject the session.
    """
    session = db.query(Session).filter(Session.id == session_id).first()
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )

    if session.status != SessionStatus.PENDING_APPROVAL:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Session not pending approval (current status: {session.status})"
        )

    # Update session status
    if approval.approved:
        session.status = SessionStatus.APPROVED
        session.approved_at = datetime.utcnow()
        session.approved_by = None  # TODO: Get from authenticated user
    else:
        session.status = SessionStatus.CANCELLED

    # Audit log (only if minimal_logging is false)
    if not settings.minimal_logging:
        audit = AuditLog(
            user_id=None,  # TODO: Get from authenticated user
            action="session_approved" if approval.approved else "session_rejected",
            resource_type="session",
            resource_id=session.id,
            details={
                "notes": approval.notes,
                "decision": "approved" if approval.approved else "rejected",
            },
        )
        db.add(audit)

    db.commit()
    db.refresh(session)

    # TODO: Notify worker to continue (via Redis pub/sub or task queue)

    return session


@router.delete("/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def cancel_session(
    session_id: int,
    db: DBSession = Depends(get_db)
):
    """
    Cancel a running session.

    This stops the worker and marks session as cancelled.
    """
    session = db.query(Session).filter(Session.id == session_id).first()
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )

    if session.status in [SessionStatus.COMPLETED, SessionStatus.CANCELLED]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Session already finished"
        )

    session.status = SessionStatus.CANCELLED
    session.completed_at = datetime.utcnow()

    # Audit log (only if minimal_logging is false)
    if not settings.minimal_logging:
        audit = AuditLog(
            user_id=None,  # TODO: Get from authenticated user
            action="session_cancelled",
            resource_type="session",
            resource_id=session.id,
        )
        db.add(audit)

    db.commit()

    # TODO: Signal worker to stop (via task revoke or flag in Redis)
