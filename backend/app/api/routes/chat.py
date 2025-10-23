"""
Chat API routes - Simplified version
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from pydantic import BaseModel
from app.core.database import get_db
from agents.agent_orchestrator import AgentOrchestrator

router = APIRouter()

# Initialize agent orchestrator
agent_orchestrator = AgentOrchestrator()


class ChatMessage(BaseModel):
    """Chat message model"""
    content: str
    conversation_id: Optional[int] = None
    context: Optional[dict] = None


class ChatResponse(BaseModel):
    """Chat response model"""
    content: str
    agent_id: str
    agent_name: str
    metadata: Optional[dict] = None
    api_calls: Optional[List[dict]] = None


@router.post("/chat", response_model=ChatResponse)
async def send_message(
    message: ChatMessage,
    db: AsyncSession = Depends(get_db)
):
    """Send a message and get agent response"""
    try:
        # Use the agent orchestrator to process the message
        response = await agent_orchestrator.process_query(message.content, message.context or {})
        
        return ChatResponse(
            content=response.content,
            agent_id=response.agent_id,
            agent_name=response.agent_name,
            metadata=response.metadata,
            api_calls=response.api_calls
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/agents")
async def get_available_agents():
    """Get list of available agents and their capabilities"""
    try:
        agents = agent_orchestrator.get_available_agents()
        return {"agents": agents}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/chat/{agent_id}", response_model=ChatResponse)
async def send_message_to_agent(
    agent_id: str,
    message: ChatMessage,
    db: AsyncSession = Depends(get_db)
):
    """Send a message to a specific agent"""
    try:
        response_content = f"Agent '{agent_id}' received: '{message.content}'. This is a placeholder response."
        
        return ChatResponse(
            content=response_content,
            agent_id=agent_id,
            agent_name=f"Agent {agent_id}",
            metadata={"status": "placeholder"}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))