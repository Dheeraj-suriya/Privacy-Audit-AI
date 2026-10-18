"""Remediation task schemas."""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum

class RemediationStatus(str, Enum):
    OPEN = "OPEN"
    IN_PROGRESS = "IN_PROGRESS"
    BLOCKED = "BLOCKED"
    RESOLVED = "RESOLVED"
    CLOSED = "CLOSED"

class Priority(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class RemediationTaskCreate(BaseModel):
    finding_id: int
    title: str = Field(..., min_length=3, max_length=500)
    description: Optional[str] = None
    priority: Priority = Priority.MEDIUM
    assigned_to: Optional[int] = None
    due_date: Optional[datetime] = None

class RemediationTaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[Priority] = None
    status: Optional[RemediationStatus] = None
    assigned_to: Optional[int] = None
    due_date: Optional[datetime] = None
    comments: Optional[str] = None

class RemediationTaskResponse(BaseModel):
    id: int
    finding_id: int
    organization_id: int
    title: str
    description: Optional[str] = None
    priority: Priority
    status: RemediationStatus
    assigned_to: Optional[int] = None
    assignee_name: Optional[str] = None
    due_date: Optional[datetime] = None
    comments: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    finding_title: Optional[str] = None

    class Config:
        from_attributes = True
