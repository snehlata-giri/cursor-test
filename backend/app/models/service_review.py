from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base

class ServiceReview(Base):
    __tablename__ = "service_reviews"

    id = Column(Integer, primary_key=True, index=True)
    vendor_service_id = Column(Integer, ForeignKey("vendor_services.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True) # Can be null if anonymous
    rating = Column(Integer, nullable=False) # 1-5
    review_text = Column(Text, nullable=True)
    cost_rating = Column(Integer, nullable=True) # 1-5
    quality_rating = Column(Integer, nullable=True) # 1-5
    timeliness_rating = Column(Integer, nullable=True) # 1-5
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    service = relationship("VendorService", back_populates="reviews")
    user = relationship("User")


