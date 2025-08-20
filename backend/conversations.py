from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from .database import get_db, User, Conversation, Message
from .auth import get_current_user

router = APIRouter()

# Pydantic models
class ConversationCreate(BaseModel):
    title: Optional[str] = "New Conversation"

class ConversationResponse(BaseModel):
    id: str
    title: str
    user_id: str
    created_at: datetime
    updated_at: datetime
    message_count: int
    context: Optional[dict] = None

class MessageResponse(BaseModel):
    id: str
    content: str
    role: str
    timestamp: datetime
    conversation_id: str
    metadata: Optional[dict] = None

class MessageCreate(BaseModel):
    content: str
    role: str = "user"

# Routes
@router.get("/", response_model=List[ConversationResponse])
async def get_conversations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    conversations = db.query(Conversation).filter(
        Conversation.user_id == current_user.id
    ).order_by(Conversation.updated_at.desc()).all()
    
    return [
        ConversationResponse(
            id=str(conv.id),
            title=conv.title,
            user_id=str(conv.user_id),
            created_at=conv.created_at,
            updated_at=conv.updated_at,
            message_count=conv.message_count,
            context={
                "summary": conv.context_summary,
                "entities": conv.context_entities,
                "topics": conv.context_topics
            } if conv.context_summary else None
        )
        for conv in conversations
    ]

@router.post("/", response_model=ConversationResponse)
async def create_conversation(
    conversation_data: ConversationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    conversation = Conversation(
        title=conversation_data.title,
        user_id=current_user.id
    )
    
    db.add(conversation)
    db.commit()
    db.refresh(conversation)
    
    return ConversationResponse(
        id=str(conversation.id),
        title=conversation.title,
        user_id=str(conversation.user_id),
        created_at=conversation.created_at,
        updated_at=conversation.updated_at,
        message_count=0
    )

@router.get("/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(
    conversation_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == current_user.id
    ).first()
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    return ConversationResponse(
        id=str(conversation.id),
        title=conversation.title,
        user_id=str(conversation.user_id),
        created_at=conversation.created_at,
        updated_at=conversation.updated_at,
        message_count=conversation.message_count,
        context={
            "summary": conversation.context_summary,
            "entities": conversation.context_entities,
            "topics": conversation.context_topics
        } if conversation.context_summary else None
    )

@router.get("/{conversation_id}/messages", response_model=List[MessageResponse])
async def get_messages(
    conversation_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Verify conversation ownership
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == current_user.id
    ).first()
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    messages = db.query(Message).filter(
        Message.conversation_id == conversation_id
    ).order_by(Message.timestamp.asc()).all()
    
    return [
        MessageResponse(
            id=str(msg.id),
            content=msg.content,
            role=msg.role,
            timestamp=msg.timestamp,
            conversation_id=str(msg.conversation_id),
            metadata=msg.metadata
        )
        for msg in messages
    ]

@router.delete("/{conversation_id}")
async def delete_conversation(
    conversation_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == current_user.id
    ).first()
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    # Delete all messages first
    db.query(Message).filter(Message.conversation_id == conversation_id).delete()
    
    # Delete conversation
    db.delete(conversation)
    db.commit()
    
    return {"message": "Conversation deleted successfully"}