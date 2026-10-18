"""Analysis routes."""
from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException
from sqlalchemy.orm import Session
from typing import List

from ...database.database import get_db
from ...database.models import User, Analysis
from ...schemas.analysis import AnalysisResponse, AnalysisStartResponse
from ...services.analysis_service import analysis_service
from ...core.security import get_current_user, require_privacy_officer

router = APIRouter(prefix="/analysis", tags=["Analysis"])

@router.post("/{document_id}/start", response_model=AnalysisStartResponse)
def start_analysis(
    document_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_privacy_officer),
):
    analysis = analysis_service.start_analysis(db, document_id, current_user.id)
    background_tasks.add_task(run_analysis_task, analysis.id)
    return AnalysisStartResponse(
        analysis_id=analysis.id,
        status="QUEUED",
        message="Analysis started in background. Poll /analysis/{id} for status.",
    )

def run_analysis_task(analysis_id: int):
    from ...database.database import SessionLocal
    db = SessionLocal()
    try:
        analysis_service.run_analysis(db, analysis_id)
    finally:
        db.close()

@router.get("/{analysis_id}", response_model=AnalysisResponse)
def get_analysis(
    analysis_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    analysis = analysis_service.get_analysis(db, analysis_id, current_user.organization_id)
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return AnalysisResponse.model_validate(analysis)

@router.get("/{analysis_id}/findings", response_model=List[dict])
def get_analysis_findings(
    analysis_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    analysis = analysis_service.get_analysis(db, analysis_id, current_user.organization_id)
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return [{"id": f.id, "title": f.title, "severity": f.severity.value, "status": f.status.value} for f in analysis.findings]
