"""Document upload and management schemas."""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class DocumentUploadResponse(BaseModel):
    id: int
    original_filename: str
    file_type: str
    file_size: int
    status: str
    sha256: str
    created_at: datetime

    class Config:
        from_attributes = True

class DocumentResponse(BaseModel):
    id: int
    organization_id: int
    uploaded_by: int
    original_filename: str
    file_type: str
    file_size: int
    status: str
    sha256: str
    extraction_method: Optional[str]
    ocr_confidence: Optional[float]
    created_at: datetime

    class Config:
        from_attributes = True

class DocumentListResponse(BaseModel):
    items: List[DocumentResponse]
    total: int
