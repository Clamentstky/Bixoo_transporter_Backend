from sqlalchemy import Column, Integer, String, DateTime, func, ForeignKey, DECIMAL, Text
from app.db.base import Base

class Settlement(Base):
    __tablename__ = "settlements"

    id = Column(Integer, primary_key=True, index=True)
    trip_id = Column(Integer, ForeignKey("trips.id", ondelete="RESTRICT"), unique=True, nullable=False)
    transporter_id = Column(Integer, ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    trip_amount = Column(DECIMAL(15, 2), nullable=False)
    platform_fee = Column(DECIMAL(15, 2), default=0.00, nullable=False)
    tax_amount = Column(DECIMAL(15, 2), default=0.00, nullable=False)
    deduction_amount = Column(DECIMAL(15, 2), default=0.00, nullable=False)
    net_amount = Column(DECIMAL(15, 2), nullable=False)
    status = Column(String(50), default="PENDING")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    processed_at = Column(DateTime(timezone=True))
    settled_at = Column(DateTime(timezone=True))
