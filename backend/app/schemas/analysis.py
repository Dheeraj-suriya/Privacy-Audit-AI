"""Analysis and findings schemas."""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class Severity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class FindingStatus(str, Enum):
    OPEN = "OPEN"
    REVIEWED = "REVIEWED"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    FALSE_POSITIVE = "FALSE_POSITIVE"

class FindingResponse(BaseModel):
    id: int
    analysis_id: int
    organization_id: int
    title: str
    description: str
    category: str
    severity: Severity
    risk_score: float
    status: FindingStatus
    evidence: Optional[str]
    evidence_document: Optional[str]
    evidence_section: Optional[str]
    control_id: Optional[str]
    recommendation: Optional[str]
    reviewed_by: Optional[int]
    reviewed_at: Optional[datetime]
    review_comment: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True

class FindingUpdate(BaseModel):
    status: Optional[FindingStatus] = None
    review_comment: Optional[str] = None

class AnalysisResponse(BaseModel):
    id: int
    document_id: int
    organization_id: int
    status: str
    compliance_score: float
    risk_score: float
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    error_message: Optional[str]
    created_at: datetime
    findings: List[FindingResponse] = []

    class Config:
        from_attributes = True

class AnalysisStartResponse(BaseModel):
    analysis_id: int
    status: str
    message: str

class DashboardSummary(BaseModel):
    privacy_score: float
    critical_risks: int
    high_risks: int
    medium_risks: int
    low_risks: int
    documents_analyzed: int
    processing_activities: int
    open_remediation_tasks: int
    total_remediation_tasks: int
    resolved_tasks: int
    overdue_tasks: int
    posture: str

class RiskDistribution(BaseModel):
    critical: int
    high: int
    medium: int
    low: int

class ComplianceByCategory(BaseModel):
    category: str
    passed: int
    partial: int
    failed: int
    not_assessed: int
    score: float

class RemediationProgress(BaseModel):
    open: int
    in_progress: int
    blocked: int
    resolved: int
    closed: int
    resolution_percentage: float

class DashboardData(BaseModel):
    summary: DashboardSummary
    risk_distribution: RiskDistribution
    compliance_by_category: List[ComplianceByCategory]
    remediation_progress: RemediationProgress
    recent_findings: List[FindingResponse]
    personal_data_categories: Dict[str, int]
