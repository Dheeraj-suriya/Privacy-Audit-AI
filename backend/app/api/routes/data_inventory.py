"""Data inventory and processing activities routes."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from ...database.database import get_db
from ...database.models import User, ProcessingActivity, DataFlow
from ...schemas.risks import ProcessingActivityResponse, DataFlowResponse, ProcessingActivityCreate, DataFlowCreate
from ...core.security import get_current_user, require_privacy_officer

router = APIRouter(prefix="/data-inventory", tags=["Data Inventory"])

@router.get("/processing-activities", response_model=List[ProcessingActivityResponse])
def list_activities(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    activities = db.query(ProcessingActivity).filter(
        ProcessingActivity.organization_id == current_user.organization_id
    ).order_by(ProcessingActivity.created_at.desc()).all()
    return [ProcessingActivityResponse.model_validate(a) for a in activities]

@router.post("/processing-activities", response_model=ProcessingActivityResponse)
def create_activity(
    data: ProcessingActivityCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_privacy_officer),
):
    activity = ProcessingActivity(
        organization_id=current_user.organization_id,
        **data.model_dump(),
    )
    db.add(activity)
    db.commit()
    db.refresh(activity)
    return ProcessingActivityResponse.model_validate(activity)

@router.get("/data-flows", response_model=List[DataFlowResponse])
def list_flows(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    flows = db.query(DataFlow).filter(
        DataFlow.organization_id == current_user.organization_id
    ).order_by(DataFlow.created_at.desc()).all()
    return [DataFlowResponse.model_validate(f) for f in flows]

@router.post("/data-flows", response_model=DataFlowResponse)
def create_flow(
    data: DataFlowCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_privacy_officer),
):
    flow = DataFlow(
        organization_id=current_user.organization_id,
        **data.model_dump(),
    )
    db.add(flow)
    db.commit()
    db.refresh(flow)
    return DataFlowResponse.model_validate(flow)
