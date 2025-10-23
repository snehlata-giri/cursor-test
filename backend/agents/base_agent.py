"""
Base agent class for all AI agents
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)


class AgentResponse(BaseModel):
    """Standard response format for agents"""
    content: str
    agent_id: str
    agent_name: str
    metadata: Optional[Dict[str, Any]] = None
    api_calls: Optional[List[Dict[str, Any]]] = None
    table_data: Optional[Dict[str, Any]] = None


class BaseAgent(ABC):
    """Base class for all AI agents"""
    
    def __init__(self, agent_id: str, name: str, description: str, capabilities: List[str]):
        self.agent_id = agent_id
        self.name = name
        self.description = description
        self.capabilities = capabilities
        self.logger = logging.getLogger(f"agent.{name}")
    
    @abstractmethod
    async def process_query(self, query: str, context: Optional[Dict[str, Any]] = None) -> AgentResponse:
        """Process a user query and return a response"""
        pass
    
    def get_capabilities(self) -> List[str]:
        """Get list of agent capabilities"""
        return self.capabilities
    
    def can_handle(self, query: str, context: Optional[Dict[str, Any]] = None) -> float:
        """
        Determine if this agent can handle the query
        Returns a confidence score between 0 and 1
        """
        # Basic keyword matching - can be enhanced with ML models
        query_lower = query.lower()
        score = 0.0
        
        for capability in self.capabilities:
            if capability.lower() in query_lower:
                score += 0.3
        
        # Normalize score to 0-1 range
        return min(score, 1.0)
    
    def get_description(self) -> str:
        """Get agent description"""
        return self.description
    
    def get_metadata(self) -> Dict[str, Any]:
        """Get agent metadata"""
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "description": self.description,
            "capabilities": self.capabilities
        }
