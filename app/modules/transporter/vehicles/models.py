from sqlalchemy import Column, Integer, String, DateTime, func, ForeignKey, DECIMAL, Date
from sqlalchemy.orm import relationship
from app.db.base import Base

class Vehicle(Base):
    __tablename__ = "vehicles"

    id = Column(Integer, primary_key=True, index=True)
    transporter_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    vehicle_number = Column(String(50), unique=True, nullable=False)
    vehicle_type = Column(String(100), nullable=False)
    vehicle_name = Column(String(100))
    capacity = Column(DECIMAL(10, 2), nullable=False)
    capacity_unit = Column(String(20), nullable=False)
    driver_name = Column(String(255))
    driver_mobile = Column(String(20))
    insurance_number = Column(String(100))
    insurance_expiry = Column(Date)
    rc_number = Column(String(100))
    status = Column(String(50), default="ACTIVE")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())
