from sqlalchemy import Column, Integer, String, Text, DateTime, DECIMAL, Boolean, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base

class VendorLocation(Base):
    __tablename__ = "vendor_locations"

    id = Column(Integer, primary_key=True, index=True)
    dgraph_id = Column(String(50), unique=True, nullable=False) # Reference to Dgraph location node
    vendor_id = Column(Integer, ForeignKey("vendors.id"), nullable=False)
    address = Column(Text, nullable=False)
    city = Column(String(100), nullable=False)
    state = Column(String(100), nullable=True)
    country = Column(String(100), nullable=False)
    postal_code = Column(String(20), nullable=True)
    latitude = Column(DECIMAL(10, 8), nullable=True)
    longitude = Column(DECIMAL(11, 8), nullable=True)
    is_primary = Column(Boolean, default=False)
    phone = Column(String(20), nullable=True)
    email = Column(String(100), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    vendor = relationship("Vendor", back_populates="locations")


