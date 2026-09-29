import app.modules.transporter.loads.models
import app.modules.auth.models
import app.modules.transporter.trips.models
from sqlalchemy import Column, Integer, String, DateTime, func, ForeignKey, Text, Boolean
from app.db.base import Base

class ChatMessage(Base):
    __tablename__ = "trip_chats"

    id = Column(Integer, primary_key=True, index=True)
    trip_id = Column(Integer, ForeignKey("trips.id", ondelete="CASCADE"), nullable=False)
    sender_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    sender_type = Column(String(50), nullable=False) # 'TRANSPORTER', 'CUSTOMER', 'SUPPORT'
    message = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


