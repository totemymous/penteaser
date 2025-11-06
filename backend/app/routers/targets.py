"""Target management endpoints with consent validation"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from ..database import get_db
from ..models.target import Target
from ..models.consent import Consent
from ..models.audit_log import AuditLog

router = APIRouter(prefix="/api/v1/targets", tags=["targets"])


# Pydantic schemas (inline for simplicity in scaffold)
from pydantic import BaseModel, HttpUrl


class ConsentCreate(BaseModel):
    """Consent document for target authorization"""
    authorized_by: str
    authorization_email: str
    authorization_date: datetime
    expiry_date: datetime
    scope: List[str]  # e.g., ["xss_testing", "dom_analysis", "payload_testing"]
    signature: str
    signature_algorithm: str = "SHA256-RSA"


class TargetCreate(BaseModel):
    """Create new target with consent"""
    name: str
    url: HttpUrl
    description: str | None = None
    consent: ConsentCreate


class TargetResponse(BaseModel):
    """Target response schema"""
    id: int
    name: str
    url: str
    description: str | None
    is_authorized: bool
    authorization_expires: datetime | None
    created_at: datetime

    class Config:
        from_attributes = True


@router.post("/", response_model=TargetResponse, status_code=status.HTTP_201_CREATED)
async def create_target(
    target_data: TargetCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new authorized target with consent-as-code.

    Requires a signed consent document. The consent is validated
    and stored alongside the target for audit purposes.
    """
    # Validate consent expiry
    if target_data.consent.expiry_date <= datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Consent has expired"
        )

    # Validate scope (must include at least one allowed operation)
    allowed_scopes = ["xss_testing", "dom_analysis", "payload_testing", "waf_analysis"]
    if not any(scope in allowed_scopes for scope in target_data.consent.scope):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid scope. Allowed: {allowed_scopes}"
        )

    # Create target
    db_target = Target(
        name=target_data.name,
        url=str(target_data.url),
        description=target_data.description,
        is_authorized=True,
        authorization_expires=target_data.consent.expiry_date,
    )
    db.add(db_target)
    db.flush()  # Get target ID

    # Create consent
    db_consent = Consent(
        target_id=db_target.id,
        authorized_by=target_data.consent.authorized_by,
        authorization_email=target_data.consent.authorization_email,
        authorization_date=target_data.consent.authorization_date,
        expiry_date=target_data.consent.expiry_date,
        scope=target_data.consent.scope,
        signature=target_data.consent.signature,
        signature_algorithm=target_data.consent.signature_algorithm,
        document=target_data.consent.model_dump(),
        verified_at=datetime.utcnow(),
    )
    db.add(db_consent)

    # Update target with consent ID
    db_target.consent_id = db_consent.id

    # Audit log
    audit = AuditLog(
        user_id=None,  # TODO: Get from authenticated user
        action="target_created",
        resource_type="target",
        resource_id=db_target.id,
        details={
            "target_url": str(target_data.url),
            "authorized_by": target_data.consent.authorized_by,
        },
        consent_reference=f"consent_{db_consent.id}",
    )
    db.add(audit)

    db.commit()
    db.refresh(db_target)

    return db_target


@router.get("/", response_model=List[TargetResponse])
async def list_targets(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    List all authorized targets.

    Returns paginated list of targets with their authorization status.
    """
    targets = db.query(Target).filter(Target.is_active == True).offset(skip).limit(limit).all()
    return targets


@router.get("/{target_id}", response_model=TargetResponse)
async def get_target(
    target_id: int,
    db: Session = Depends(get_db)
):
    """Get target details by ID"""
    target = db.query(Target).filter(Target.id == target_id).first()
    if not target:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Target not found"
        )
    return target


@router.delete("/{target_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_target(
    target_id: int,
    db: Session = Depends(get_db)
):
    """
    Soft delete a target (marks as inactive).

    This preserves audit trail while preventing new sessions.
    """
    target = db.query(Target).filter(Target.id == target_id).first()
    if not target:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Target not found"
        )

    target.is_active = False

    # Audit log
    audit = AuditLog(
        user_id=None,  # TODO: Get from authenticated user
        action="target_deleted",
        resource_type="target",
        resource_id=target.id,
        details={"target_url": target.url},
    )
    db.add(audit)

    db.commit()
