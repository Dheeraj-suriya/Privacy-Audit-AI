"""Report generation schemas."""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ReportGenerateRequest(BaseModel):
    analysis_id: int
    report_type: str = "pdf"

class ReportResponse(BaseModel):
    id: int
    organization_id: int
    analysis_id: int
    filename: str
    report_type: str
    created_at: datetime
    download_url: Optional[str]

    class Config:
        from_attributes = True
