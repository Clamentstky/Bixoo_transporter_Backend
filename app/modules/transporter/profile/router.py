from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.common.responses import StandardResponse, success_response
from app.core.dependencies import get_current_transporter
from app.modules.auth.models import User
from app.modules.transporter.profile import schemas, models

router = APIRouter(prefix="/api/v1/transporter", tags=["profile", "availability"])

@router.get("/profile", response_model=StandardResponse[schemas.TransporterProfileResponse])
def get_profile(current_user: User = Depends(get_current_transporter), db: Session = Depends(get_db)):
    profile = db.query(models.TransporterProfile).filter(models.TransporterProfile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
        
    # Dynamically sync trip counts to ensure accuracy
    from app.modules.transporter.trips.models import Trip
    total_count = db.query(Trip).filter(
        Trip.transporter_id == current_user.id
    ).count()
    completed_count = db.query(Trip).filter(
        Trip.transporter_id == current_user.id, 
        Trip.status == "COMPLETED"
    ).count()
    
    if profile.completed_trips != completed_count or profile.total_trips != total_count:
        profile.completed_trips = completed_count
        profile.total_trips = total_count
        db.commit()
        db.refresh(profile)
        
    return success_response(data=profile)

@router.patch("/profile", response_model=StandardResponse[schemas.TransporterProfileResponse])
def update_profile(request: schemas.ProfileUpdate, current_user: User = Depends(get_current_transporter), db: Session = Depends(get_db)):
    profile = db.query(models.TransporterProfile).filter(models.TransporterProfile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    update_data = request.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(profile, key, value)
    
    db.commit()
    db.refresh(profile)
    return success_response(data=profile, message="Profile updated successfully")

@router.get("/availability", response_model=StandardResponse[schemas.AvailabilityUpdate])
def get_availability(current_user: User = Depends(get_current_transporter), db: Session = Depends(get_db)):
    profile = db.query(models.TransporterProfile).filter(models.TransporterProfile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return success_response(data={"is_online": profile.is_online, "is_available": profile.is_available})

@router.patch("/availability", response_model=StandardResponse[schemas.AvailabilityUpdate])
def update_availability(request: schemas.AvailabilityUpdate, current_user: User = Depends(get_current_transporter), db: Session = Depends(get_db)):
    profile = db.query(models.TransporterProfile).filter(models.TransporterProfile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    profile.is_online = request.is_online
    profile.is_available = request.is_available
    db.commit()
    db.refresh(profile)
    
    return success_response(data={"is_online": profile.is_online, "is_available": profile.is_available}, message="Availability updated successfully")
