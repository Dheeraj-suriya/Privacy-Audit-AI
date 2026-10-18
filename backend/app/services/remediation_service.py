"""Remediation task management service."""
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from ..database.models import RemediationTask, RemediationStatus, Priority, Finding, User, AuditLog
from ..schemas.remediation import RemediationTaskCreate, RemediationTaskUpdate
from ..core.logging import logger

class RemediationService:

    def create_task(self, db: Session, data: RemediationTaskCreate, org_id: int) -> RemediationTask:
        """Create a remediation task from a finding."""
        # Verify finding exists and belongs to org
        finding = db.query(Finding).filter(
            Finding.id == data.finding_id,
            Finding.organization_id == org_id
        ).first()
        if not finding:
            raise ValueError("Finding not found or access denied")

        task = RemediationTask(
            finding_id=data.finding_id,
            organization_id=org_id,
            title=data.title,
            description=data.description,
            priority=data.priority,
            assigned_to=data.assigned_to,
            due_date=data.due_date,
            status=RemediationStatus.OPEN,
        )
        db.add(task)
        db.commit()
        db.refresh(task)

        logger.info(f"Remediation task created: {task.id}")
        return task

    def get_tasks(self, db: Session, org_id: int, status: Optional[str] = None, 
                  assigned_to: Optional[int] = None, skip: int = 0, limit: int = 100) -> List[RemediationTask]:
        query = db.query(RemediationTask).filter(RemediationTask.organization_id == org_id)
        if status:
            query = query.filter(RemediationTask.status == status)
        if assigned_to:
            query = query.filter(RemediationTask.assigned_to == assigned_to)
        return query.order_by(RemediationTask.created_at.desc()).offset(skip).limit(limit).all()

    def get_task(self, db: Session, task_id: int, org_id: int) -> Optional[RemediationTask]:
        return db.query(RemediationTask).filter(
            RemediationTask.id == task_id,
            RemediationTask.organization_id == org_id
        ).first()

    def update_task(self, db: Session, task_id: int, data: RemediationTaskUpdate, org_id: int) -> Optional[RemediationTask]:
        task = self.get_task(db, task_id, org_id)
        if not task:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(task, field, value)

        task.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(task)

        logger.info(f"Remediation task updated: {task.id}")
        return task

    def delete_task(self, db: Session, task_id: int, org_id: int) -> bool:
        task = self.get_task(db, task_id, org_id)
        if not task:
            return False
        db.delete(task)
        db.commit()
        logger.info(f"Remediation task deleted: {task_id}")
        return True

    def get_progress(self, db: Session, org_id: int) -> Dict[str, Any]:
        """Get remediation progress statistics."""
        tasks = db.query(RemediationTask).filter(RemediationTask.organization_id == org_id).all()

        total = len(tasks)
        open_count = sum(1 for t in tasks if t.status == RemediationStatus.OPEN)
        in_progress = sum(1 for t in tasks if t.status == RemediationStatus.IN_PROGRESS)
        blocked = sum(1 for t in tasks if t.status == RemediationStatus.BLOCKED)
        resolved = sum(1 for t in tasks if t.status == RemediationStatus.RESOLVED)
        closed = sum(1 for t in tasks if t.status == RemediationStatus.CLOSED)

        # Overdue tasks
        overdue = sum(1 for t in tasks if t.due_date and t.due_date < datetime.utcnow() 
                      and t.status not in [RemediationStatus.RESOLVED, RemediationStatus.CLOSED])

        resolution_pct = (resolved + closed) / total * 100 if total > 0 else 0

        return {
            "total": total,
            "open": open_count,
            "in_progress": in_progress,
            "blocked": blocked,
            "resolved": resolved,
            "closed": closed,
            "overdue": overdue,
            "resolution_percentage": round(resolution_pct, 1),
        }

remediation_service = RemediationService()
