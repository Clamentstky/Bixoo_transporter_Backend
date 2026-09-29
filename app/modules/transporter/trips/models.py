from sqlalchemy import Column, Integer, String, DateTime, func, ForeignKey, DECIMAL, Text
from sqlalchemy.orm import relationship
from app.db.base import Base

class Trip(Base):
    __tablename__ = "trips"

    id = Column(Integer, primary_key=True, index=True)
    trip_code = Column(String(100), unique=True, nullable=False)
    transport_request_id = Column(Integer, ForeignKey("transport_requests.id", ondelete="RESTRICT"), nullable=False)
    transporter_id = Column(Integer, ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    vehicle_id = Column(Integer, ForeignKey("vehicles.id", ondelete="SET NULL"))
    status = Column(String(50), default="ACCEPTED")
    
    accepted_at = Column(DateTime(timezone=True))
    going_to_pickup_at = Column(DateTime(timezone=True))
    picked_up_at = Column(DateTime(timezone=True))
    started_at = Column(DateTime(timezone=True))
    reached_delivery_at = Column(DateTime(timezone=True))
    delivered_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    
    pickup_otp = Column(String(10))
    delivery_otp = Column(String(10))
    distance_travelled = Column(DECIMAL(10, 2), default=0.00)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    request = relationship("TransportRequest")
    locations = relationship("TripLocation", backref="trip", cascade="all, delete-orphan")
    documents = relationship("TripDocument", backref="trip", cascade="all, delete-orphan")
    status_history = relationship("TripStatusHistory", backref="trip", cascade="all, delete-orphan")

class TripStatusHistory(Base):
    __tablename__ = "trip_status_history"

    id = Column(Integer, primary_key=True, index=True)
    trip_id = Column(Integer, ForeignKey("trips.id", ondelete="CASCADE"), nullable=False)
    old_status = Column(String(50))
    new_status = Column(String(50), nullable=False)
    changed_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    remarks = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class TripLocation(Base):
    __tablename__ = "trip_locations"

    id = Column(Integer, primary_key=True, index=True)
    trip_id = Column(Integer, ForeignKey("trips.id", ondelete="CASCADE"), nullable=False)
    transporter_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    latitude = Column(DECIMAL(10, 8), nullable=False)
    longitude = Column(DECIMAL(11, 8), nullable=False)
    speed = Column(DECIMAL(5, 2))
    heading = Column(DECIMAL(5, 2))
    captured_at = Column(DateTime(timezone=True), server_default=func.now())

class TripDocument(Base):
    __tablename__ = "trip_documents"

    id = Column(Integer, primary_key=True, index=True)
    trip_id = Column(Integer, ForeignKey("trips.id", ondelete="CASCADE"), nullable=False)
    document_type = Column(String(50), nullable=False)
    file_name = Column(String(255), nullable=False)
    file_path = Column(Text, nullable=False)
    file_url = Column(Text, nullable=False)
    uploaded_by = Column(Integer, ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
