"""Target and consent schemas"""

from pydantic import BaseModel, HttpUrl
from datetime import datetime
from typing import List


class ConsentCreate(BaseModel):
    """Consent document for target authorization"""
    authorized_by: str
    authorization_email: str
    authorization_date: datetime
    expiry_date: datetime
    scope: List[str]  # e.g., ["xss_testing", "dom_analysis", "payload_testing"]
    signature: str
    signature_algorithm: str = "SHA256-RSA"


class ConsentResponse(BaseModel):
    """Consent response schema"""
    id: int
    target_id: int
    authorized_by: str
    authorization_email: str
    authorization_date: datetime
    expiry_date: datetime
    scope: List[str]
    is_valid: bool
    created_at: datetime

    class Config:
        from_attributes = True


class TargetCreate(BaseModel):
    """Create new target with optional consent"""
    name: str
    url: HttpUrl
    description: str | None = None
    consent: ConsentCreate | None = None  # Optional - required only if REQUIRE_CONSENT=true


class TargetUpdate(BaseModel):
    """Update target"""
    name: str | None = None
    description: str | None = None
    is_active: bool | None = None


class TargetResponse(BaseModel):
    """Target response schema"""
    id: int
    name: str
    url: str
    description: str | None
    is_authorized: bool
    authorization_expires: datetime | None
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class TargetDetail(TargetResponse):
    """Detailed target response with consent info"""
    consent: ConsentResponse | None = None

    class Config:
        from_attributes = True
