"""Processing activity and data flow schemas."""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

class Severity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class ProcessingActivityCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=255)
    purpose: Optional[str] = None
    data_subjects: Optional[str] = None
    data_categories: Optional[str] = None
    collection_source: Optional[str] = None
    storage_location: Optional[str] = None
    retention_period: Optional[str] = None
    external_processors: Optional[str] = None
    cross_border_transfer: bool = False
    legal_basis: Optional[str] = None
    risk_level: Severity = Severity.LOW
    owner: Optional[str] = None
    status: str = "active"

class ProcessingActivityResponse(BaseModel):
    id: int
    organization_id: int
    name: str
    purpose: Optional[str]
    data_subjects: Optional[str]
    data_categories: Optional[str]
    collection_source: Optional[str]
    storage_location: Optional[str]
    retention_period: Optional[str]
    external_processors: Optional[str]
    cross_border_transfer: bool
    legal_basis: Optional[str]
    risk_level: Severity
    owner: Optional[str]
    status: str
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True

class DataFlowCreate(BaseModel):
    source: str = Field(..., min_length=1, max_length=255)
    destination: str = Field(..., min_length=1, max_length=255)
    data_categories: Optional[str] = None
    purpose: Optional[str] = None
    risk_level: Severity = Severity.LOW
    retention_period: Optional[str] = None
    deletion_mechanism: Optional[str] = None

class DataFlowResponse(BaseModel):
    id: int
    organization_id: int
    source: str
    destination: str
    data_categories: Optional[str]
    purpose: Optional[str]
    risk_level: Severity
    retention_period: Optional[str]
    deletion_mechanism: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True
