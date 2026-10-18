"""Remediation task routes."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from ...database.database import get_db
from ...database.models import User, RemediationTask
from ...schemas.remediation import RemediationTaskCreate, RemediationTaskUpdate, RemediationTaskResponse
from ...services.remediation_service import remediation_service
from ...core.security import get_current_user, require_privacy_officer

router = APIRouter(prefix="/remediation", tags=["Remediation"])

@router.post("", response_model=RemediationTaskResponse)
def create_task(
    data: RemediationTaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_privacy_officer),
):
    task = remediation_service.create_task(db, data, current_user.organization_id)
    return RemediationTaskResponse.model_validate(task)

@router.get("", response_model=List[RemediationTaskResponse])
def list_tasks(
    status: str = None,
    assigned_to: int = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    tasks = remediation_service.get_tasks(
        db, current_user.organization_id, status=status, assigned_to=assigned_to
    )
    return [RemediationTaskResponse.model_validate(t) for t in tasks]

@router.get("/progress")
def get_progress(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return remediation_service.get_progress(db, current_user.organization_id)

@router.get("/{task_id}", response_model=RemediationTaskResponse)
def get_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task = remediation_service.get_task(db, task_id, current_user.organization_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return RemediationTaskResponse.model_validate(task)

@router.patch("/{task_id}", response_model=RemediationTaskResponse)
def update_task(
    task_id: int,
    data: RemediationTaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task = remediation_service.update_task(db, task_id, data, current_user.organization_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return RemediationTaskResponse.model_validate(task)

@router.delete("/{task_id}")
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_privacy_officer),
):
    success = remediation_service.delete_task(db, task_id, current_user.organization_id)
    if not success:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"success": True}
