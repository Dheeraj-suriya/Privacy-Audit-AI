"""Audit log routes."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from ...database.database import get_db
from ...database.models import User, AuditLog
from ...core.security import get_current_user, require_admin

router = APIRouter(prefix="/audit", tags=["Audit"])

@router.get("/logs")
def get_logs(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
    skip: int = 0,
    limit: int = 100,
):
    logs = db.query(AuditLog).filter(
        AuditLog.organization_id == current_user.organization_id
    ).order_by(AuditLog.timestamp.desc()).offset(skip).limit(limit).all()
    return [{
        "id": l.id,
        "action": l.action,
        "resource_type": l.resource_type,
        "resource_id": l.resource_id,
        "timestamp": l.timestamp,
        "user_id": l.user_id,
    } for l in logs]
