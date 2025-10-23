from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base

class VendorService(Base):
    __tablename__ = "vendor_services"

    id = Column(Integer, primary_key=True, index=True)
    dgraph_id = Column(String(50), unique=True, nullable=False) # Reference to Dgraph service node
    vendor_id = Column(Integer, ForeignKey("vendors.id"), nullable=False)
    service_name = Column(String(200), nullable=False)
    category = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    vendor = relationship("Vendor", back_populates="services")
    pricing = relationship("ServicePricing", back_populates="service", cascade="all, delete-orphan")
    reviews = relationship("ServiceReview", back_populates="service", cascade="all, delete-orphan")


