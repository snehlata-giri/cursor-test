from sqlalchemy import Column, Integer, String, Text, DateTime, DECIMAL, Boolean, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base

class ServicePricing(Base):
    __tablename__ = "service_pricing"

    id = Column(Integer, primary_key=True, index=True)
    vendor_service_id = Column(Integer, ForeignKey("vendor_services.id"), nullable=False)
    pricing_type = Column(String(50), nullable=False) # 'hourly', 'fixed', 'per_unit', 'monthly'
    base_price = Column(DECIMAL(10, 2), nullable=False)
    currency = Column(String(3), default='USD')
    unit = Column(String(50), nullable=True) # 'hour', 'project', 'item', 'month'
    minimum_quantity = Column(Integer, default=1)
    maximum_quantity = Column(Integer, nullable=True)
    discount_percentage = Column(DECIMAL(5, 2), default=0.0)
    is_active = Column(Boolean, default=True)
    valid_from = Column(DateTime(timezone=True), server_default=func.now())
    valid_until = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    service = relationship("VendorService", back_populates="pricing")


