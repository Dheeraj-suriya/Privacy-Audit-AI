"""Audit logging service."""
from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session

from ..database.models import AuditLog
from ..core.logging import logger

class AuditLogService:

    def log(self, db: Session, action: str, user_id: Optional[int] = None,
            organization_id: Optional[int] = None, resource_type: Optional[str] = None,
            resource_id: Optional[int] = None, metadata_json: Optional[str] = None,
            ip_address: Optional[str] = None):
        """Create an audit log entry."""
        log = AuditLog(
            user_id=user_id,
            organization_id=organization_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            metadata_json=metadata_json,
            ip_address=ip_address,
        )
        db.add(log)
        db.commit()
        logger.info(f"Audit: {action} by user {user_id} on {resource_type} {resource_id}")

    def get_logs(self, db: Session, organization_id: Optional[int] = None,
                 user_id: Optional[int] = None, skip: int = 0, limit: int = 100) -> list:
        query = db.query(AuditLog)
        if organization_id:
            query = query.filter(AuditLog.organization_id == organization_id)
        if user_id:
            query = query.filter(AuditLog.user_id == user_id)
        return query.order_by(AuditLog.timestamp.desc()).offset(skip).limit(limit).all()

audit_log_service = AuditLogService()
