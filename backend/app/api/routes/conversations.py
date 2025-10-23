"""
Conversation management API routes
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
from app.core.database import get_db
from app.models.conversation import Conversation
from app.models.message import Message
from app.models.user import User

router = APIRouter()


class ConversationCreate(BaseModel):
    title: Optional[str] = None


class ConversationResponse(BaseModel):
    id: int
    title: str
    created_at: datetime
    updated_at: Optional[datetime]
    message_count: int

    class Config:
        from_attributes = True


class MessageCreate(BaseModel):
    content: str
    role: str  # 'user', 'assistant', 'system'
    agent_id: Optional[str] = None
    agent_name: Optional[str] = None
    metadata: Optional[dict] = None


class MessageResponse(BaseModel):
    id: int
    content: str
    role: str
    agent_id: Optional[str]
    agent_name: Optional[str]
    metadata: Optional[dict]
    timestamp: datetime

    class Config:
        from_attributes = True


@router.get("/conversations", response_model=List[ConversationResponse])
async def get_conversations(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """Get all conversations"""
    try:
        result = await db.execute(
            select(Conversation)
            .order_by(Conversation.updated_at.desc())
            .offset(skip)
            .limit(limit)
        )
        conversations = result.scalars().all()
        
        # Add message count to each conversation
        conversation_responses = []
        for conv in conversations:
            message_count_result = await db.execute(
                select(Message).where(Message.conversation_id == conv.id)
            )
            message_count = len(message_count_result.scalars().all())
            
            conversation_responses.append(ConversationResponse(
                id=conv.id,
                title=conv.title or f"Conversation {conv.id}",
                created_at=conv.created_at,
                updated_at=conv.updated_at,
                message_count=message_count
            ))
        
        return conversation_responses
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/conversations", response_model=ConversationResponse)
async def create_conversation(
    conversation: ConversationCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new conversation"""
    try:
        # For now, use a default user ID (in a real app, this would come from authentication)
        default_user_id = 1
        
        db_conversation = Conversation(
            user_id=default_user_id,
            title=conversation.title or "New Conversation"
        )
        
        db.add(db_conversation)
        await db.commit()
        await db.refresh(db_conversation)
        
        return ConversationResponse(
            id=db_conversation.id,
            title=db_conversation.title,
            created_at=db_conversation.created_at,
            updated_at=db_conversation.updated_at,
            message_count=0
        )
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/conversations/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(
    conversation_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific conversation"""
    try:
        result = await db.execute(
            select(Conversation).where(Conversation.id == conversation_id)
        )
        conversation = result.scalar_one_or_none()
        
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        # Get message count
        message_count_result = await db.execute(
            select(Message).where(Message.conversation_id == conversation_id)
        )
        message_count = len(message_count_result.scalars().all())
        
        return ConversationResponse(
            id=conversation.id,
            title=conversation.title or f"Conversation {conversation.id}",
            created_at=conversation.created_at,
            updated_at=conversation.updated_at,
            message_count=message_count
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/conversations/{conversation_id}", response_model=ConversationResponse)
async def update_conversation(
    conversation_id: int,
    conversation: ConversationCreate,
    db: AsyncSession = Depends(get_db)
):
    """Update a conversation"""
    try:
        result = await db.execute(
            select(Conversation).where(Conversation.id == conversation_id)
        )
        db_conversation = result.scalar_one_or_none()
        
        if not db_conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        if conversation.title:
            db_conversation.title = conversation.title
        
        await db.commit()
        await db.refresh(db_conversation)
        
        # Get message count
        message_count_result = await db.execute(
            select(Message).where(Message.conversation_id == conversation_id)
        )
        message_count = len(message_count_result.scalars().all())
        
        return ConversationResponse(
            id=db_conversation.id,
            title=db_conversation.title,
            created_at=db_conversation.created_at,
            updated_at=db_conversation.updated_at,
            message_count=message_count
        )
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/conversations/{conversation_id}")
async def delete_conversation(
    conversation_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Delete a conversation and all its messages"""
    try:
        # Check if conversation exists
        result = await db.execute(
            select(Conversation).where(Conversation.id == conversation_id)
        )
        conversation = result.scalar_one_or_none()
        
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        # Delete messages first (cascade should handle this, but being explicit)
        await db.execute(
            delete(Message).where(Message.conversation_id == conversation_id)
        )
        
        # Delete conversation
        await db.execute(
            delete(Conversation).where(Conversation.id == conversation_id)
        )
        
        await db.commit()
        
        return {"message": "Conversation deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/conversations/{conversation_id}/messages", response_model=List[MessageResponse])
async def get_conversation_messages(
    conversation_id: int,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """Get messages for a conversation"""
    try:
        # Check if conversation exists
        result = await db.execute(
            select(Conversation).where(Conversation.id == conversation_id)
        )
        conversation = result.scalar_one_or_none()
        
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        # Get messages
        result = await db.execute(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.timestamp.asc())
            .offset(skip)
            .limit(limit)
        )
        messages = result.scalars().all()
        
        return [
            MessageResponse(
                id=msg.id,
                content=msg.content,
                role=msg.role,
                agent_id=msg.agent_id,
                agent_name=msg.agent_name,
                metadata=msg.message_metadata,
                timestamp=msg.timestamp
            )
            for msg in messages
        ]
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/conversations/{conversation_id}/messages", response_model=MessageResponse)
async def add_message_to_conversation(
    conversation_id: int,
    message: MessageCreate,
    db: AsyncSession = Depends(get_db)
):
    """Add a message to a conversation"""
    try:
        # Check if conversation exists
        result = await db.execute(
            select(Conversation).where(Conversation.id == conversation_id)
        )
        conversation = result.scalar_one_or_none()
        
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        # Create message
        db_message = Message(
            conversation_id=conversation_id,
            role=message.role,
            content=message.content,
            agent_id=message.agent_id,
            message_metadata=message.metadata
        )
        
        db.add(db_message)
        
        # Update conversation timestamp
        conversation.updated_at = datetime.utcnow()
        
        await db.commit()
        await db.refresh(db_message)
        
        return MessageResponse(
            id=db_message.id,
            content=db_message.content,
            role=db_message.role,
            agent_id=db_message.agent_id,
            agent_name=message.agent_name,
            metadata=db_message.message_metadata,
            timestamp=db_message.timestamp
        )
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


