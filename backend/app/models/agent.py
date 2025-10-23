"""
Agent model for AI agents and their capabilities
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, JSON, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class Agent(Base):
    """Agent model"""
    __tablename__ = "agents"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    capabilities = Column(JSON, nullable=True)  # List of capabilities
    is_active = Column(Boolean, default=True)
    agent_config = Column(JSON, nullable=True)  # Agent-specific configuration
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    messages = relationship("Message", back_populates="agent")
    api_endpoints = relationship("AgentAPIEndpoint", back_populates="agent")


class AgentCapability(Base):
    """Agent capability model"""
    __tablename__ = "agent_capabilities"
    
    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(Integer, ForeignKey("agents.id"), nullable=False)
    capability_name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    keywords = Column(JSON, nullable=True)  # Keywords for matching
    
    # Relationships
    agent = relationship("Agent")


class AgentAPIEndpoint(Base):
    """Agent-API endpoint mapping"""
    __tablename__ = "agent_api_endpoints"
    
    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(Integer, ForeignKey("agents.id"), nullable=False)
    api_endpoint_id = Column(Integer, ForeignKey("api_endpoints.id"), nullable=False)
    
    # Relationships
    agent = relationship("Agent", back_populates="api_endpoints")
    api_endpoint = relationship("APIEndpoint", back_populates="agents")
