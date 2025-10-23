"""
WebSocket connection manager for real-time chat - Simplified version
"""

from fastapi import WebSocket
from typing import Dict, List, Any
import json
import logging
from agents.agent_orchestrator import AgentOrchestrator
from app.core.database import AsyncSessionLocal
from app.models.conversation import Conversation
from app.models.message import Message
from sqlalchemy.future import select
from sqlalchemy import desc

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manages WebSocket connections and message routing"""
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.agent_orchestrator = AgentOrchestrator()
    
    async def connect(self, websocket: WebSocket, client_id: str):
        """Accept a new WebSocket connection"""
        await websocket.accept()
        self.active_connections[client_id] = websocket
        logger.info(f"Client {client_id} connected. Total connections: {len(self.active_connections)}")
        
        # Send welcome message
        await self.send_personal_message({
            "type": "system",
            "content": "Connected to Vendor Management System. Ask me about vendors, their locations, services, and pricing!",
            "timestamp": self._get_timestamp()
        }, client_id)
        
        # Send available agents info
        await self.get_available_agents(client_id)

        # Load and send past conversations
        await self.load_and_send_conversations(client_id)
    
    def disconnect(self, client_id: str):
        """Remove a WebSocket connection"""
        if client_id in self.active_connections:
            del self.active_connections[client_id]
            logger.info(f"Client {client_id} disconnected. Total connections: {len(self.active_connections)}")
    
    async def send_personal_message(self, message: Dict[str, Any], client_id: str):
        """Send a message to a specific client"""
        if client_id in self.active_connections:
            try:
                await self.active_connections[client_id].send_text(json.dumps(message))
            except Exception as e:
                logger.error(f"Error sending message to {client_id}: {e}")
                self.disconnect(client_id)
    
    async def broadcast(self, message: Dict[str, Any]):
        """Broadcast a message to all connected clients"""
        for client_id in list(self.active_connections.keys()):
            await self.send_personal_message(message, client_id)
    
    async def process_message(self, client_id: str, message_text: str):
        """Process an incoming message and route to appropriate agent"""
        try:
            # Parse the message
            try:
                message_data = json.loads(message_text)
                user_message = message_data.get("content", "")
                context = message_data.get("context", {})
            except json.JSONDecodeError:
                # If not JSON, treat as plain text
                user_message = message_text
                context = {}
            
            if not user_message.strip():
                await self.send_personal_message({
                    "type": "error",
                    "content": "Please provide a message.",
                    "timestamp": self._get_timestamp()
                }, client_id)
                return
            
            # Save user message to DB and get conversation ID
            db_conversation_id = await self._save_message_to_db(
                conversation_id=message_data.get("conversation_id"),
                user_id=1, # TODO: Replace with actual user ID from authentication
                role="user",
                content=user_message,
                client_id=client_id
            )
            
            # Send user message back to client
            await self.send_personal_message({
                "type": "user",
                "content": user_message,
                "conversation_id": str(db_conversation_id),
                "timestamp": self._get_timestamp()
            }, client_id)
            
            # Send typing indicator
            await self.send_personal_message({
                "type": "typing",
                "content": "Agent is thinking...",
                "conversation_id": str(db_conversation_id),
                "timestamp": self._get_timestamp()
            }, client_id)
            
            # Use agent orchestrator to process the message
            try:
                response = await self.agent_orchestrator.process_query(user_message, context)
                
                # Save agent response to DB
                await self._save_message_to_db(
                    conversation_id=db_conversation_id,
                    user_id=1, # TODO: Replace with actual user ID
                    role="assistant",
                    content=response.content,
                    agent_id=response.agent_id,
                    message_metadata=response.metadata,
                    client_id=client_id,
                    table_data=response.table_data
                )
                
                # Send agent response
                await self.send_personal_message({
                    "type": "assistant",
                    "content": response.content,
                    "agent_id": response.agent_id,
                    "agent_name": response.agent_name,
                    "metadata": response.metadata,
                    "api_calls": response.api_calls,
                    "table_data": response.table_data,
                    "conversation_id": str(db_conversation_id),
                    "timestamp": self._get_timestamp()
                }, client_id)
            except Exception as e:
                logger.error(f"Error in agent orchestrator: {e}")
                await self.send_personal_message({
                    "type": "error",
                    "content": f"I'm sorry, I encountered an error processing your request: {str(e)}",
                    "conversation_id": str(db_conversation_id),
                    "timestamp": self._get_timestamp()
                }, client_id)
            
            logger.info(f"Processed message for {client_id}")
            
        except Exception as e:
            logger.error(f"Error processing message from {client_id}: {e}")
            await self.send_personal_message({
                "type": "error",
                "content": "I'm sorry, I encountered an error processing your message. Please try again.",
                "conversation_id": message_data.get("conversation_id") if 'message_data' in locals() else None,
                "timestamp": self._get_timestamp()
            }, client_id)
    
    def _get_timestamp(self) -> str:
        """Get current timestamp as ISO string"""
        from datetime import datetime
        return datetime.utcnow().isoformat()
    
    async def get_available_agents(self, client_id: str):
        """Send available agents information to client"""
        agents = self.agent_orchestrator.get_available_agents()
        await self.send_personal_message({
            "type": "agents_info",
            "content": "Available agents",
            "agents": agents,
            "timestamp": self._get_timestamp()
        }, client_id)

    async def load_and_send_conversations(self, client_id: str):
        """Load and send past conversations to client"""
        try:
            async with AsyncSessionLocal() as session:
                # For now, assume user_id 1. In a real app, this would come from auth.
                result = await session.execute(
                    select(Conversation)
                    .filter_by(user_id=1)
                    .order_by(desc(Conversation.updated_at))
                )
                conversations = result.scalars().all()
                
                conv_list = []
                for conv in conversations:
                    messages_result = await session.execute(
                        select(Message)
                        .filter_by(conversation_id=conv.id)
                        .order_by(Message.timestamp)
                    )
                    messages = messages_result.scalars().all()
                    
                    conv_list.append({
                        "id": str(conv.id),
                        "title": conv.title,
                        "messages": [{
                            "type": msg.role,
                            "content": msg.content,
                            "agent_id": msg.agent_id,
                            "metadata": msg.message_metadata,
                            "timestamp": msg.timestamp.isoformat() if msg.timestamp else None
                        } for msg in messages]
                    })
                
                await self.send_personal_message({
                    "type": "all_conversations",
                    "content": "Loaded past conversations",
                    "conversations": conv_list,
                    "timestamp": self._get_timestamp()
                }, client_id)
        except Exception as e:
            logger.error(f"Error loading conversations: {e}")
            await self.send_personal_message({
                "type": "error",
                "content": "Failed to load conversations",
                "timestamp": self._get_timestamp()
            }, client_id)

    async def _save_message_to_db(self, conversation_id: int, user_id: int, role: str, content: str, client_id: str, agent_id: str = None, message_metadata: dict = None, table_data: dict = None) -> int:
        """Saves a message to the database and ensures conversation exists."""
        async with AsyncSessionLocal() as session:
            db_conversation = None
            if conversation_id:
                result = await session.execute(select(Conversation).filter_by(id=conversation_id, user_id=user_id))
                db_conversation = result.scalar_one_or_none()

            if not db_conversation:
                # Create a new conversation if none exists or provided ID is invalid
                db_conversation = Conversation(user_id=user_id, title=content[:100]) # Use first 100 chars of user message as title
                session.add(db_conversation)
                await session.commit()
                await session.refresh(db_conversation)
                logger.info(f"Created new conversation with ID: {db_conversation.id}")
                # Notify client about new conversation
                await self.send_personal_message({
                    "type": "new_conversation",
                    "id": str(db_conversation.id),
                    "title": db_conversation.title,
                    "timestamp": self._get_timestamp()
                }, client_id)

            db_message = Message(
                conversation_id=db_conversation.id,
                role=role,
                content=content,
                agent_id=agent_id,
                message_metadata={"api_calls": message_metadata.get("api_calls") if message_metadata else None, "table_data": table_data} if message_metadata or table_data else None
            )
            session.add(db_message)
            await session.commit()
            await session.refresh(db_message)
            logger.info(f"Saved {role} message to conversation {db_conversation.id}")
            return db_conversation.id