from sqlalchemy import Column, Integer, String, Boolean, DateTime, func, ForeignKey, DECIMAL, Text
from sqlalchemy.orm import relationship
from app.db.base import Base

class TransporterProfile(Base):
    __tablename__ = "transporter_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    company_name = Column(String(255))
    contact_person = Column(String(255))
    address = Column(Text)
    city = Column(String(100))
    district = Column(String(100))
    state = Column(String(100))
    pincode = Column(String(20))
    
    verification_status = Column(String(50), default="PENDING")
    
    is_online = Column(Boolean, default=False)
    is_available = Column(Boolean, default=False)
    
    rating = Column(DECIMAL(3, 2), default=5.00)
    total_trips = Column(Integer, default=0)
    completed_trips = Column(Integer, default=0)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())
