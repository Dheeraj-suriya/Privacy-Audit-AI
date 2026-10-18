"""Report generation routes."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from ...database.database import get_db
from ...database.models import User, Analysis, Finding, Organization, Report
from ...schemas.reports import ReportGenerateRequest, ReportResponse
from ...services.report_service import report_service
from ...core.security import get_current_user, require_privacy_officer

router = APIRouter(prefix="/reports", tags=["Reports"])

@router.post("/generate", response_model=ReportResponse)
def generate_report(
    data: ReportGenerateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_privacy_officer),
):
    analysis = db.query(Analysis).filter(
        Analysis.id == data.analysis_id,
        Analysis.organization_id == current_user.organization_id
    ).first()
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")

    org = db.query(Organization).filter(Organization.id == current_user.organization_id).first()
    findings = db.query(Finding).filter(Finding.analysis_id == analysis.id).all()

    findings_dicts = [{
        "title": f.title,
        "description": f.description,
        "severity": f.severity.value,
        "risk_score": f.risk_score,
        "recommendation": f.recommendation,
    } for f in findings]

    compliance_dicts = [{
        "control_id": f.control_id or "UNKNOWN",
        "title": f.title,
        "category": f.category,
        "status": f.status.value,
        "explanation": f.description,
    } for f in findings]

    risk_result = {
        "severity": "HIGH" if analysis.risk_score > 50 else "MEDIUM",
        "risk_distribution": {
            "CRITICAL": sum(1 for f in findings if f.severity.value == "CRITICAL"),
            "HIGH": sum(1 for f in findings if f.severity.value == "HIGH"),
            "MEDIUM": sum(1 for f in findings if f.severity.value == "MEDIUM"),
            "LOW": sum(1 for f in findings if f.severity.value == "LOW"),
        }
    }

    score_data = {"score": analysis.compliance_score}

    filepath = report_service.generate_pdf_report(
        analysis_id=analysis.id,
        organization_id=org.id,
        organization_name=org.name,
        findings=findings_dicts,
        compliance_results=compliance_dicts,
        risk_result=risk_result,
        score_data=score_data,
        processing_activities=[],
        data_flows=[],
        pii_summary={},
    )

    report = Report(
        organization_id=org.id,
        analysis_id=analysis.id,
        filename=filepath.split("/")[-1],
        report_type="pdf",
    )
    db.add(report)
    db.commit()
    db.refresh(report)

    return ReportResponse(
        id=report.id,
        organization_id=org.id,
        analysis_id=analysis.id,
        filename=report.filename,
        report_type=report.report_type,
        created_at=report.created_at,
        download_url=f"/api/reports/{report.id}/download",
    )

@router.get("", response_model=List[ReportResponse])
def list_reports(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    reports = db.query(Report).filter(
        Report.organization_id == current_user.organization_id
    ).order_by(Report.created_at.desc()).all()
    return [ReportResponse.model_validate(r) for r in reports]

@router.get("/{report_id}/download")
def download_report(
    report_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    from fastapi.responses import FileResponse
    report = db.query(Report).filter(
        Report.id == report_id,
        Report.organization_id == current_user.organization_id
    ).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    file_path = report_service.get_report_path(report.filename)
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Report file not found")

    return FileResponse(
        str(file_path),
        filename=report.filename,
        media_type="application/pdf",
    )
