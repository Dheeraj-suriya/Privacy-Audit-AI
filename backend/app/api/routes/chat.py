"""AI compliance assistant chat routes."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from ...database.database import get_db
from ...database.models import User, ChatConversation, ChatMessage
from ...schemas.chat import ChatMessageRequest, ChatMessageResponse, ChatConversationResponse
from ...services.llm_service import llm_service
from ...services.vector_service import vector_service
from ...core.security import get_current_user

router = APIRouter(prefix="/chat", tags=["Chat"])

@router.post("", response_model=ChatMessageResponse)
def chat(
    data: ChatMessageRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if data.conversation_id:
        conv = db.query(ChatConversation).filter(
            ChatConversation.id == data.conversation_id,
            ChatConversation.organization_id == current_user.organization_id
        ).first()
        if not conv:
            raise HTTPException(status_code=404, detail="Conversation not found")
    else:
        conv = ChatConversation(
            organization_id=current_user.organization_id,
            user_id=current_user.id,
            title=data.message[:50],
        )
        db.add(conv)
        db.commit()
        db.refresh(conv)

    user_msg = ChatMessage(
        conversation_id=conv.id,
        role="user",
        content=data.message,
    )
    db.add(user_msg)
    db.commit()

    chunks = vector_service.query(
        organization_id=current_user.organization_id,
        query_text=data.message,
        n_results=5,
    )
    context_chunks = [c["text"] for c in chunks]

    history = db.query(ChatMessage).filter(
        ChatMessage.conversation_id == conv.id
    ).order_by(ChatMessage.created_at).all()
    history_dicts = [{"role": m.role, "content": m.content} for m in history[-6:]]

    result = llm_service.chat_response(data.message, context_chunks, history_dicts)

    assistant_msg = ChatMessage(
        conversation_id=conv.id,
        role="assistant",
        content=result["response"],
        sources=str(result.get("sources", [])),
    )
    db.add(assistant_msg)
    db.commit()
    db.refresh(assistant_msg)

    return ChatMessageResponse(
        id=assistant_msg.id,
        conversation_id=conv.id,
        role="assistant",
        content=result["response"],
        sources=result.get("sources"),
        created_at=assistant_msg.created_at,
    )

@router.get("/conversations", response_model=List[ChatConversationResponse])
def list_conversations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    convs = db.query(ChatConversation).filter(
        ChatConversation.organization_id == current_user.organization_id,
        ChatConversation.user_id == current_user.id,
    ).order_by(ChatConversation.created_at.desc()).all()
    return [ChatConversationResponse.model_validate(c) for c in convs]
