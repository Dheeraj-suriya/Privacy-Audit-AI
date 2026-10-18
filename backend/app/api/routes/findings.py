"""Finding management routes."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from ...database.database import get_db
from ...database.models import User, Finding
from ...schemas.analysis import FindingResponse, FindingUpdate
from ...core.security import get_current_user, require_privacy_officer

router = APIRouter(prefix="/findings", tags=["Findings"])


# List all findings
@router.get("/", response_model=List[FindingResponse])
def list_findings(
    severity: Optional[str] = None,
    status: Optional[str] = None,
    category: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Finding).filter(
        Finding.organization_id == current_user.organization_id
    )

    if severity:
        query = query.filter(Finding.severity == severity)

    if status:
        query = query.filter(Finding.status == status)

    if category:
        query = query.filter(Finding.category == category)

    findings = query.order_by(Finding.created_at.desc()).all()

    return [FindingResponse.model_validate(f) for f in findings]


# Get a single finding
@router.get("/{finding_id}", response_model=FindingResponse)
def get_finding(
    finding_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    print("========== FINDING DEBUG ==========")
    print("Requested Finding ID:", finding_id)
    print("Current User ID:", current_user.id)
    print("Current User Organization:", current_user.organization_id)

    finding = db.query(Finding).filter(
        Finding.id == finding_id
    ).first()

    print("Finding exists:", finding is not None)

    if finding:
        print("Finding DB ID:", finding.id)
        print("Finding DB Organization:", finding.organization_id)
        print("Finding Title:", finding.title)

    print("===================================")

    if not finding:
        raise HTTPException(
            status_code=404,
            detail="Finding not found"
        )

    if finding.organization_id != current_user.organization_id:
        raise HTTPException(
            status_code=404,
            detail="Finding not found"
        )

    return FindingResponse.model_validate(finding)


# Update a finding
@router.patch("/{finding_id}", response_model=FindingResponse)
def update_finding(
    finding_id: int,
    data: FindingUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_privacy_officer),
):
    finding = db.query(Finding).filter(
        Finding.id == finding_id,
        Finding.organization_id == current_user.organization_id
    ).first()

    if not finding:
        raise HTTPException(
            status_code=404,
            detail="Finding not found"
        )

    if data.status:
        finding.status = data.status

    if data.review_comment:
        finding.review_comment = data.review_comment
        finding.reviewed_by = current_user.id

    db.commit()
    db.refresh(finding)

    return FindingResponse.model_validate(finding)