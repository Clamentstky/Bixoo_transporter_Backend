from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from decimal import Decimal
from app.modules.transporter.loads.schemas import TransportRequestResponse

class TripLocationCreate(BaseModel):
    latitude: float
    longitude: float
    speed: Optional[float] = None
    heading: Optional[float] = None

class TripStatusUpdate(BaseModel):
    status: str
    remarks: Optional[str] = None

class TripDocumentResponse(BaseModel):
    id: int
    document_type: str
    file_name: str
    file_url: str
    created_at: datetime

    class Config:
        from_attributes = True

class TripResponse(BaseModel):
    id: int
    trip_code: str
    transport_request_id: int
    vehicle_id: Optional[int]
    status: str
    accepted_at: Optional[datetime]
    going_to_pickup_at: Optional[datetime]
    picked_up_at: Optional[datetime]
    started_at: Optional[datetime]
    reached_delivery_at: Optional[datetime]
    delivered_at: Optional[datetime]
    completed_at: Optional[datetime]
    distance_travelled: Decimal
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class TripDetailResponse(TripResponse):
    request: TransportRequestResponse
    documents: List[TripDocumentResponse] = []
