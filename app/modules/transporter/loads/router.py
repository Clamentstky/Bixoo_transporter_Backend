import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.common.responses import StandardResponse, success_response, Pagination
from app.core.dependencies import get_current_transporter
from app.modules.auth.models import User
from app.modules.transporter.loads import schemas, models as load_models
from app.modules.transporter.trips import models as trip_models
from datetime import datetime, timezone
from typing import List

router = APIRouter(prefix="/api/v1/transporter/loads", tags=["loads"])

from sqlalchemy import or_, desc, asc

@router.get("", response_model=StandardResponse[List[schemas.AvailableLoadResponse]])
def get_available_loads(
    page: int = 1, limit: int = 10, search: str = None, 
    status: str = None, vehicle_type: str = None, 
    pickup_city: str = None, delivery_city: str = None,
    sort_by: str = None, sort_order: str = "desc",
    current_user: User = Depends(get_current_transporter), db: Session = Depends(get_db)
):
    query = db.query(load_models.TransportMatch).join(load_models.TransportRequest).filter(
        load_models.TransportMatch.transporter_id == current_user.id
    )
    
    if status and status.upper() != "ALL":
        query = query.filter(load_models.TransportMatch.status == status.upper())
    else:
        query = query.filter(load_models.TransportMatch.status.in_(["PENDING", "VIEWED"]))
        
    if search:
        search_term = f"%{search.strip()}%"
        query = query.filter(
            or_(
                load_models.TransportRequest.request_code.ilike(search_term),
                load_models.TransportRequest.pickup_city.ilike(search_term),
                load_models.TransportRequest.delivery_city.ilike(search_term),
                load_models.TransportRequest.goods_name.ilike(search_term)
            )
        )
        
    if vehicle_type:
        query = query.filter(load_models.TransportRequest.required_vehicle_type == vehicle_type)
        
    if pickup_city:
        query = query.filter(load_models.TransportRequest.pickup_city == pickup_city)
        
    if delivery_city:
        query = query.filter(load_models.TransportRequest.delivery_city == delivery_city)
        
    # Sorting
    sort_column = load_models.TransportMatch.created_at
    if sort_by == "distance":
        sort_column = load_models.TransportMatch.distance_from_pickup
    elif sort_by == "payout":
        sort_column = load_models.TransportRequest.offered_amount
    elif sort_by == "pickup_date":
        sort_column = load_models.TransportRequest.pickup_date
        
    if sort_order.lower() == "asc":
        query = query.order_by(asc(sort_column))
    else:
        query = query.order_by(desc(sort_column))
    
    total = query.count()
    matches = query.offset((page - 1) * limit).limit(limit).all()
    
    data = []
    for match in matches:
        data.append({
            "match_id": match.id,
            "distance_from_pickup": match.distance_from_pickup,
            "match_score": match.match_score,
            "match_status": match.status,
            "request": match.request
        })
        
    return success_response(
        data=data,
        pagination=Pagination(page=page, limit=limit, total=total, total_pages=(total + limit - 1) // limit)
    )

@router.get("/{match_id}", response_model=StandardResponse[schemas.AvailableLoadResponse])
def get_load_details(match_id: int, current_user: User = Depends(get_current_transporter), db: Session = Depends(get_db)):
    match = db.query(load_models.TransportMatch).filter(
        load_models.TransportMatch.id == match_id,
        load_models.TransportMatch.transporter_id == current_user.id
    ).first()
    if not match:
        raise HTTPException(status_code=404, detail="Load not found")
    
    if match.status == "PENDING":
        match.status = "VIEWED"
        db.commit()
        db.refresh(match)

    return success_response(data={
        "match_id": match.id,
        "distance_from_pickup": match.distance_from_pickup,
        "match_score": match.match_score,
        "match_status": match.status,
        "request": match.request
    })

@router.post("/{match_id}/accept", response_model=StandardResponse[schemas.TripCreatedResponse])
def accept_load(match_id: int, current_user: User = Depends(get_current_transporter), db: Session = Depends(get_db)):
    match = db.query(load_models.TransportMatch).filter(
        load_models.TransportMatch.id == match_id,
        load_models.TransportMatch.transporter_id == current_user.id
    ).first()
    if not match:
        raise HTTPException(status_code=404, detail="Load not found")
    if match.status == "ACCEPTED":
        raise HTTPException(status_code=409, detail="Load already accepted")
    
    # Check if request is still available
    if match.request.status != "PENDING":
        raise HTTPException(status_code=409, detail="This load is no longer available")
    
    # Update match and request status
    match.status = "ACCEPTED"
    match.responded_at = datetime.now(timezone.utc)
    match.request.status = "ASSIGNED"
    
    # Create Trip
    trip_code = f"TRIP-{uuid.uuid4().hex[:8].upper()}"
    new_trip = trip_models.Trip(
        trip_code=trip_code,
        transport_request_id=match.transport_request_id,
        transporter_id=current_user.id,
        status="ACCEPTED",
        accepted_at=datetime.now(timezone.utc)
    )
    db.add(new_trip)
    
    # Update total_trips in profile
    from app.modules.transporter.profile.models import TransporterProfile
    profile = db.query(TransporterProfile).filter(TransporterProfile.user_id == current_user.id).first()
    if profile:
        profile.total_trips += 1
        
    db.commit()
    db.refresh(new_trip)
    
    return success_response(
        data={"trip_id": new_trip.id, "trip_code": new_trip.trip_code, "status": new_trip.status},
        message="Load accepted successfully"
    )

@router.post("/{match_id}/reject", response_model=StandardResponse)
def reject_load(match_id: int, request: schemas.LoadRejectRequest, current_user: User = Depends(get_current_transporter), db: Session = Depends(get_db)):
    match = db.query(load_models.TransportMatch).filter(
        load_models.TransportMatch.id == match_id,
        load_models.TransportMatch.transporter_id == current_user.id
    ).first()
    if not match:
        raise HTTPException(status_code=404, detail="Load not found")
    
    match.status = "REJECTED"
    match.responded_at = datetime.now(timezone.utc)
    db.commit()
    
    return success_response(message="Load rejected successfully")
