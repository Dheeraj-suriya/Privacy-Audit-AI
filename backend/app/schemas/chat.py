"""AI compliance assistant chat schemas."""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class ChatMessageRequest(BaseModel):
    conversation_id: Optional[int] = None
    message: str = Field(..., min_length=1, max_length=4000)

class SourceReference(BaseModel):
    document_name: str
    section: Optional[str]
    snippet: str

class ChatMessageResponse(BaseModel):
    id: int
    conversation_id: int
    role: str
    content: str
    sources: Optional[List[SourceReference]]
    created_at: datetime

    class Config:
        from_attributes = True

class ChatConversationResponse(BaseModel):
    id: int
    organization_id: int
    user_id: int
    title: Optional[str]
    created_at: datetime
    messages: List[ChatMessageResponse] = []

    class Config:
        from_attributes = True
