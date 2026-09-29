from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from decimal import Decimal

class AvailabilityUpdate(BaseModel):
    is_online: bool
    is_available: bool

class ProfileUpdate(BaseModel):
    company_name: Optional[str] = None
    contact_person: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    district: Optional[str] = None
    state: Optional[str] = None
    pincode: Optional[str] = None

class TransporterProfileResponse(BaseModel):
    id: int
    user_id: int
    company_name: Optional[str] = None
    contact_person: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    district: Optional[str] = None
    state: Optional[str] = None
    pincode: Optional[str] = None
    verification_status: str
    is_online: bool
    is_available: bool
    rating: Decimal
    total_trips: int
    completed_trips: int

    class Config:
        from_attributes = True
