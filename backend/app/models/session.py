"""Session model for tracking testing operations"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, JSON, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
import enum

from ..database import Base


class SessionStatus(str, enum.Enum):
    """Session execution status"""
    PENDING = "pending"
    RUNNING = "running"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Session(Base):
    """Testing session with human-in-the-loop workflow"""

    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, index=True)
    target_id = Column(Integer, ForeignKey("targets.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Nullable for demo/lab mode

    # Session metadata
    name = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    status = Column(SQLEnum(SessionStatus), default=SessionStatus.PENDING)

    # Execution tracking
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    duration_seconds = Column(Integer, nullable=True)

    # Human approval tracking
    approval_requested_at = Column(DateTime, nullable=True)
    approved_at = Column(DateTime, nullable=True)
    approved_by = Column(Integer, nullable=True)  # User ID

    # Session configuration
    config = Column(JSON, nullable=True)  # Browser settings, test parameters

    # Recording metadata
    recording_path = Column(String, nullable=True)
    screenshot_count = Column(Integer, default=0)
    interaction_count = Column(Integer, default=0)

    # Audit
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    target = relationship("Target", back_populates="sessions")
    user = relationship("User", back_populates="sessions")
    findings = relationship("Finding", back_populates="session")
