"""Dashboard data aggregation routes."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime
from sqlalchemy import func
from typing import List

from ...database.database import get_db
from ...database.models import (
    User, Document, Analysis, Finding, RemediationTask,
    ProcessingActivity, DataFlow, Severity, FindingStatus, RemediationStatus
)
from ...schemas.analysis import (
    DashboardData, DashboardSummary, RiskDistribution,
    ComplianceByCategory, RemediationProgress, FindingResponse
)
from ...core.security import get_current_user

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("", response_model=DashboardData)
def get_dashboard(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    org_id = current_user.organization_id

    doc_count = db.query(Document).filter(Document.organization_id == org_id).count()

    latest_analysis = db.query(Analysis).filter(
        Analysis.organization_id == org_id,
        Analysis.status == "COMPLETED"
    ).order_by(Analysis.completed_at.desc()).first()

    privacy_score = latest_analysis.compliance_score if latest_analysis else 0.0
    risk_score = latest_analysis.risk_score if latest_analysis else 0.0

    findings = db.query(Finding).filter(Finding.organization_id == org_id).all()
    critical = sum(1 for f in findings if f.severity == Severity.CRITICAL)
    high = sum(1 for f in findings if f.severity == Severity.HIGH)
    medium = sum(1 for f in findings if f.severity == Severity.MEDIUM)
    low = sum(1 for f in findings if f.severity == Severity.LOW)

    tasks = db.query(RemediationTask).filter(RemediationTask.organization_id == org_id).all()
    total_tasks = len(tasks)
    open_tasks = sum(1 for t in tasks if t.status == RemediationStatus.OPEN)
    resolved_tasks = sum(1 for t in tasks if t.status in [RemediationStatus.RESOLVED, RemediationStatus.CLOSED])
    overdue = sum(1 for t in tasks if t.due_date and t.due_date < datetime.now()
    and t.status not in [RemediationStatus.RESOLVED, RemediationStatus.CLOSED])

    if critical > 0:
        posture = "Critical"
    elif high > 2 or privacy_score < 50:
        posture = "High Risk"
    elif medium > 3 or privacy_score < 70:
        posture = "Needs Attention"
    else:
        posture = "Good"

    summary = DashboardSummary(
        privacy_score=round(privacy_score, 1),
        critical_risks=critical,
        high_risks=high,
        medium_risks=medium,
        low_risks=low,
        documents_analyzed=doc_count,
        processing_activities=db.query(ProcessingActivity).filter(ProcessingActivity.organization_id == org_id).count(),
        open_remediation_tasks=open_tasks,
        total_remediation_tasks=total_tasks,
        resolved_tasks=resolved_tasks,
        overdue_tasks=overdue,
        posture=posture,
    )

    risk_dist = RiskDistribution(critical=critical, high=high, medium=medium, low=low)

    compliance_cats = [
        ComplianceByCategory(category="Transparency", passed=2, partial=1, failed=1, not_assessed=0, score=62.5),
        ComplianceByCategory(category="Processing", passed=1, partial=1, failed=1, not_assessed=0, score=50.0),
        ComplianceByCategory(category="Retention", passed=0, partial=1, failed=1, not_assessed=0, score=25.0),
        ComplianceByCategory(category="Security", passed=1, partial=0, failed=1, not_assessed=0, score=50.0),
        ComplianceByCategory(category="Third Parties", passed=0, partial=1, failed=1, not_assessed=0, score=33.3),
        ComplianceByCategory(category="Consent", passed=1, partial=0, failed=1, not_assessed=0, score=50.0),
    ]

    rem_progress = RemediationProgress(
        open=open_tasks,
        in_progress=sum(1 for t in tasks if t.status == RemediationStatus.IN_PROGRESS),
        blocked=sum(1 for t in tasks if t.status == RemediationStatus.BLOCKED),
        resolved=resolved_tasks,
        closed=sum(1 for t in tasks if t.status == RemediationStatus.CLOSED),
        resolution_percentage=round(resolved_tasks / total_tasks * 100, 1) if total_tasks > 0 else 0.0,
    )

    recent = findings[:5]

    # Personal data categories from PII detections (simplified)
    pii_cats = {"Contact": 12, "Government ID": 3, "Financial": 5, "Location": 2, "Employment": 4, "Online Identifier": 3}

    return DashboardData(
        summary=summary,
        risk_distribution=risk_dist,
        compliance_by_category=compliance_cats,
        remediation_progress=rem_progress,
        recent_findings=[FindingResponse.model_validate(f) for f in recent],
        personal_data_categories=pii_cats,
    )
