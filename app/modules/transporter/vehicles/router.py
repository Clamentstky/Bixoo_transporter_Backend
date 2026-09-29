from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.common.responses import StandardResponse, success_response
from app.core.dependencies import get_current_transporter
from app.modules.auth.models import User
from app.modules.transporter.vehicles import schemas, models
from typing import List

router = APIRouter(prefix="/api/v1/transporter/vehicles", tags=["vehicles"])

@router.get("", response_model=StandardResponse[List[schemas.VehicleResponse]])
def list_vehicles(current_user: User = Depends(get_current_transporter), db: Session = Depends(get_db)):
    vehicles = db.query(models.Vehicle).filter(models.Vehicle.transporter_id == current_user.id).all()
    return success_response(data=vehicles)

@router.post("", response_model=StandardResponse[schemas.VehicleResponse], status_code=status.HTTP_201_CREATED)
def create_vehicle(request: schemas.VehicleCreate, current_user: User = Depends(get_current_transporter), db: Session = Depends(get_db)):
    existing_vehicle = db.query(models.Vehicle).filter(models.Vehicle.vehicle_number == request.vehicle_number).first()
    if existing_vehicle:
        raise HTTPException(status_code=409, detail="Vehicle with this number already exists")
    
    vehicle = models.Vehicle(**request.model_dump(), transporter_id=current_user.id)
    db.add(vehicle)
    db.commit()
    db.refresh(vehicle)
    return success_response(data=vehicle, message="Vehicle created successfully")

@router.get("/{id}", response_model=StandardResponse[schemas.VehicleResponse])
def get_vehicle(id: int, current_user: User = Depends(get_current_transporter), db: Session = Depends(get_db)):
    vehicle = db.query(models.Vehicle).filter(
        models.Vehicle.id == id,
        models.Vehicle.transporter_id == current_user.id
    ).first()
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    return success_response(data=vehicle)

@router.patch("/{id}", response_model=StandardResponse[schemas.VehicleResponse])
def update_vehicle(id: int, request: schemas.VehicleUpdate, current_user: User = Depends(get_current_transporter), db: Session = Depends(get_db)):
    vehicle = db.query(models.Vehicle).filter(
        models.Vehicle.id == id,
        models.Vehicle.transporter_id == current_user.id
    ).first()
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    
    update_data = request.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(vehicle, key, value)
    
    db.commit()
    db.refresh(vehicle)
    return success_response(data=vehicle, message="Vehicle updated successfully")

@router.delete("/{id}", response_model=StandardResponse)
def delete_vehicle(id: int, current_user: User = Depends(get_current_transporter), db: Session = Depends(get_db)):
    vehicle = db.query(models.Vehicle).filter(
        models.Vehicle.id == id,
        models.Vehicle.transporter_id == current_user.id
    ).first()
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    
    db.delete(vehicle)
    db.commit()
    return success_response(message="Vehicle deleted successfully")
