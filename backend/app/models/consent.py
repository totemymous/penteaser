"""Consent model for consent-as-code authorization"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, JSON, ForeignKey
from sqlalchemy.orm import relationship

from ..database import Base


class Consent(Base):
    """Signed consent document for authorized testing"""

    __tablename__ = "consents"

    id = Column(Integer, primary_key=True, index=True)
    target_id = Column(Integer, ForeignKey("targets.id"), nullable=False)

    # Authorization details
    authorized_by = Column(String, nullable=False)
    authorization_email = Column(String, nullable=False)
    authorization_date = Column(DateTime, nullable=False)
    expiry_date = Column(DateTime, nullable=False)

    # Scope of testing (JSON array of allowed operations)
    scope = Column(JSON, nullable=False)  # e.g., ["xss_testing", "dom_analysis", "payload_testing"]

    # Digital signature for verification
    signature = Column(Text, nullable=False)
    signature_algorithm = Column(String, default="SHA256-RSA")

    # Consent document (full JSON)
    document = Column(JSON, nullable=True)

    # Audit
    created_at = Column(DateTime, default=datetime.utcnow)
    verified_at = Column(DateTime, nullable=True)
    is_valid = Column(Integer, default=True)  # Can be revoked

    # Relationships
    target = relationship("Target", back_populates="consent")
