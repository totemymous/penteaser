"""Finding model for security issues discovered during testing"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, JSON, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
import enum

from ..database import Base


class Severity(str, enum.Enum):
    """Finding severity levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class FindingType(str, enum.Enum):
    """Types of security findings"""
    # XSS vulnerabilities (A03:2021 - Injection)
    XSS_REFLECTED = "xss_reflected"
    XSS_STORED = "xss_stored"
    XSS_DOM = "xss_dom"

    # SQL Injection vulnerabilities (A03:2021 - Injection)
    SQLI_ERROR_BASED = "sqli_error_based"
    SQLI_BOOLEAN_BASED = "sqli_boolean_based"
    SQLI_TIME_BASED = "sqli_time_based"
    SQLI_UNION_BASED = "sqli_union_based"

    # Other vulnerabilities
    INPUT_VALIDATION = "input_validation"
    CSP_BYPASS = "csp_bypass"
    WAF_DETECTION = "waf_detection"
    INFO = "info"
    OTHER = "other"


class Finding(Base):
    """Security finding discovered during a session"""

    __tablename__ = "findings"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("sessions.id"), nullable=False)

    # Finding classification
    title = Column(String, nullable=False)
    finding_type = Column(SQLEnum(FindingType), nullable=False)
    severity = Column(SQLEnum(Severity), default=Severity.INFO)

    # Technical details
    description = Column(Text, nullable=False)
    endpoint = Column(String, nullable=True)  # URL where issue was found
    parameter = Column(String, nullable=True)  # Vulnerable parameter
    dom_path = Column(String, nullable=True)  # DOM element path

    # Evidence
    evidence = Column(JSON, nullable=True)  # Screenshots, payloads, responses
    reproduction_steps = Column(Text, nullable=True)

    # Remediation
    remediation = Column(Text, nullable=True)
    references = Column(JSON, nullable=True)  # Links to OWASP, CWE, etc.

    # Verification
    verified = Column(Integer, default=False)
    false_positive = Column(Integer, default=False)

    # Audit
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    session = relationship("Session", back_populates="findings")
