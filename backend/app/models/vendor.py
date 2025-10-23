from sqlalchemy import Column, Integer, String, Text, DateTime, DECIMAL
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base

class Vendor(Base):
    __tablename__ = "vendors"

    id = Column(Integer, primary_key=True, index=True)
    dgraph_id = Column(String(50), unique=True, nullable=False) # Reference to Dgraph vendor node
    name = Column(String(200), nullable=False)
    email = Column(String(100), nullable=True)
    phone = Column(String(20), nullable=True)
    website = Column(String(200), nullable=True)
    rating = Column(DECIMAL(3,2), default=0.0)
    established_year = Column(Integer, nullable=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    locations = relationship("VendorLocation", back_populates="vendor", cascade="all, delete-orphan")
    services = relationship("VendorService", back_populates="vendor", cascade="all, delete-orphan")

