from sqlalchemy import Column, Integer, String, DateTime, func, ForeignKey, DECIMAL, Text
from app.db.base import Base

class WalletTransaction(Base):
    __tablename__ = "wallet_transactions"

    id = Column(Integer, primary_key=True, index=True)
    transporter_id = Column(Integer, ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    trip_id = Column(Integer, ForeignKey("trips.id", ondelete="SET NULL"))
    transaction_type = Column(String(50), nullable=False)
    amount = Column(DECIMAL(15, 2), nullable=False)
    reference_number = Column(String(100))
    status = Column(String(50), default="COMPLETED")
    description = Column(Text)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
