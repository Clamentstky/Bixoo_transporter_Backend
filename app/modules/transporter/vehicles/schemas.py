from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime
from decimal import Decimal

class VehicleCreate(BaseModel):
    vehicle_number: str
    vehicle_type: str
    vehicle_name: Optional[str] = None
    capacity: Decimal
    capacity_unit: str
    driver_name: Optional[str] = None
    driver_mobile: Optional[str] = None
    insurance_number: Optional[str] = None
    insurance_expiry: Optional[date] = None
    rc_number: Optional[str] = None

class VehicleUpdate(BaseModel):
    vehicle_type: Optional[str] = None
    vehicle_name: Optional[str] = None
    capacity: Optional[Decimal] = None
    capacity_unit: Optional[str] = None
    driver_name: Optional[str] = None
    driver_mobile: Optional[str] = None
    insurance_number: Optional[str] = None
    insurance_expiry: Optional[date] = None
    rc_number: Optional[str] = None
    status: Optional[str] = None

class VehicleResponse(BaseModel):
    id: int
    transporter_id: int
    vehicle_number: str
    vehicle_type: str
    vehicle_name: Optional[str] = None
    capacity: Decimal
    capacity_unit: str
    driver_name: Optional[str] = None
    driver_mobile: Optional[str] = None
    insurance_number: Optional[str] = None
    insurance_expiry: Optional[date] = None
    rc_number: Optional[str] = None
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
