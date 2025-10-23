"""
New Service Pricing model for hybrid Dgraph + PostgreSQL architecture
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, DECIMAL, Index
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class ServicePricingNew(Base):
    """New service pricing model that references vendor and service by name"""
    __tablename__ = "service_pricing_new"

    id = Column(Integer, primary_key=True, index=True)
    vendor_name = Column(String(200), nullable=False, index=True)  # Reference to Dgraph vendor node
    service_name = Column(String(200), nullable=False, index=True)  # Reference to Dgraph service node
    pricing_type = Column(String(50), nullable=False)  # fixed, hourly, monthly, per_unit
    base_price = Column(DECIMAL(10, 2), nullable=False)
    currency = Column(String(3), default="USD")
    unit = Column(String(50), nullable=True)  # project, hour, month, panel, etc.
    discount_percentage = Column(DECIMAL(5, 2), default=0.0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Create composite index for efficient lookups
    __table_args__ = (
        Index('idx_vendor_service', 'vendor_name', 'service_name'),
        Index('idx_pricing_type', 'pricing_type'),
        Index('idx_price_range', 'base_price'),
    )


