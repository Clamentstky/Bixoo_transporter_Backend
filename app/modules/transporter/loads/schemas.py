from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from decimal import Decimal

class LoadRejectRequest(BaseModel):
    reason: Optional[str] = None

class TransportRequestResponse(BaseModel):
    id: int
    request_code: str
    pickup_address: str
    pickup_city: str
    pickup_state: str
    delivery_address: str
    delivery_city: str
    delivery_state: str
    goods_name: str
    quantity: Decimal
    quantity_unit: str
    weight: Decimal
    weight_unit: str
    required_vehicle_type: str
    pickup_date: datetime
    required_delivery_date: datetime
    estimated_distance: Optional[Decimal] = None
    offered_amount: Decimal
    status: str

    class Config:
        from_attributes = True

class AvailableLoadResponse(BaseModel):
    match_id: int
    distance_from_pickup: Optional[Decimal] = None
    match_score: Optional[Decimal] = None
    match_status: str
    request: TransportRequestResponse

    class Config:
        from_attributes = True

class TripCreatedResponse(BaseModel):
    trip_id: int
    trip_code: str
    status: str

    class Config:
        from_attributes = True
