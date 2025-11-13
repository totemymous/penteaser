"""Audit log model for immutable operation tracking"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, JSON, ForeignKey
from sqlalchemy.orm import relationship

from ..database import Base


class AuditLog(Base):
    """Immutable audit trail for all system operations"""

    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Operation details
    action = Column(String, nullable=False)  # e.g., "target_created", "session_started", "payload_tested"
    resource_type = Column(String, nullable=False)  # e.g., "target", "session", "consent"
    resource_id = Column(Integer, nullable=True)

    # Context
    details = Column(JSON, nullable=True)  # Additional context
    consent_reference = Column(String, nullable=True)  # Link to consent document

    # Network metadata
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)

    # Timestamp (immutable)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="audit_logs")
