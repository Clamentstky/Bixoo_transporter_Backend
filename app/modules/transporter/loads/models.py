from sqlalchemy import Column, Integer, String, DateTime, func, ForeignKey, DECIMAL, Text
from sqlalchemy.orm import relationship
from app.db.base import Base

class TransportRequest(Base):
    __tablename__ = "transport_requests"

    id = Column(Integer, primary_key=True, index=True)
    request_code = Column(String(100), unique=True, nullable=False)
    source_type = Column(String(50), nullable=False)
    source_reference_id = Column(String(100))
    pickup_address = Column(Text, nullable=False)
    pickup_city = Column(String(100), nullable=False)
    pickup_state = Column(String(100), nullable=False)
    pickup_latitude = Column(DECIMAL(10, 8))
    pickup_longitude = Column(DECIMAL(11, 8))
    delivery_address = Column(Text, nullable=False)
    delivery_city = Column(String(100), nullable=False)
    delivery_state = Column(String(100), nullable=False)
    delivery_latitude = Column(DECIMAL(10, 8))
    delivery_longitude = Column(DECIMAL(11, 8))
    goods_name = Column(String(255), nullable=False)
    quantity = Column(DECIMAL(10, 2), nullable=False)
    quantity_unit = Column(String(20), nullable=False)
    weight = Column(DECIMAL(10, 2), nullable=False)
    weight_unit = Column(String(20), nullable=False)
    required_vehicle_type = Column(String(100), nullable=False)
    pickup_date = Column(DateTime, nullable=False)
    required_delivery_date = Column(DateTime, nullable=False)
    estimated_distance = Column(DECIMAL(10, 2))
    offered_amount = Column(DECIMAL(15, 2), nullable=False)
    status = Column(String(50), default="PENDING")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

class TransportMatch(Base):
    __tablename__ = "transport_matches"

    id = Column(Integer, primary_key=True, index=True)
    transport_request_id = Column(Integer, ForeignKey("transport_requests.id", ondelete="CASCADE"), nullable=False)
    transporter_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    match_score = Column(DECIMAL(5, 2))
    distance_from_pickup = Column(DECIMAL(10, 2))
    status = Column(String(50), default="PENDING")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    responded_at = Column(DateTime(timezone=True))

    request = relationship("TransportRequest", backref="matches")
