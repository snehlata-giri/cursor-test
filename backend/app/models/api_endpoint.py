"""
API endpoint model for external API integrations
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class APIEndpoint(Base):
    """API endpoint model"""
    __tablename__ = "api_endpoints"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    url = Column(String(500), nullable=False)
    method = Column(String(10), nullable=False, default="GET")  # GET, POST, PUT, DELETE
    headers = Column(JSON, nullable=True)  # Default headers
    auth_type = Column(String(50), nullable=True)  # 'bearer', 'api_key', 'basic', 'none'
    api_auth_config = Column(JSON, nullable=True)  # Authentication configuration
    is_active = Column(Boolean, default=True)
    rate_limit = Column(Integer, nullable=True)  # Requests per minute
    timeout = Column(Integer, default=30)  # Timeout in seconds
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    agents = relationship("AgentAPIEndpoint", back_populates="api_endpoint")
