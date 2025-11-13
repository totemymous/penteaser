"""Target model for authorized testing endpoints"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.orm import relationship

from ..database import Base


class Target(Base):
    """Authorized target for security testing"""

    __tablename__ = "targets"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    url = Column(String, nullable=False)
    description = Column(Text, nullable=True)

    # Consent tracking
    consent_id = Column(Integer, nullable=True)  # Foreign key to Consent
    is_authorized = Column(Boolean, default=False)
    authorization_expires = Column(DateTime, nullable=True)

    # Status
    is_active = Column(Boolean, default=True)

    # Audit
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    sessions = relationship("Session", back_populates="target")
    consent = relationship("Consent", back_populates="target", uselist=False)
