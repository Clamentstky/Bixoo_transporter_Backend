import os
import uuid
import shutil
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.common.responses import StandardResponse, success_response, Pagination
from app.core.dependencies import get_current_transporter
from app.modules.auth.models import User
from app.modules.transporter.trips import schemas, models as trip_models
from datetime import datetime, timezone
from typing import List
from app.core.config import settings

router = APIRouter(prefix="/api/v1/transporter/trips", tags=["trips"])

TRIP_FLOW = {
    "ACCEPTED": ["GOING_TO_PICKUP"],
    "GOING_TO_PICKUP": ["PICKED_UP"],
    "PICKED_UP": ["IN_TRANSIT"],
    "IN_TRANSIT": ["AT_DELIVERY"],
    "AT_DELIVERY": ["DELIVERED"],
    "DELIVERED": ["COMPLETED"],
    "COMPLETED": []
}

from sqlalchemy import or_, desc, asc
from app.modules.transporter.loads import models as load_models

@router.get("", response_model=StandardResponse[List[schemas.TripDetailResponse]])
def get_trips(
    page: int = 1, limit: int = 10, trip_status: str = None, 
    statuses: str = None, search: str = None,
    sort_by: str = None, sort_order: str = "desc",
    current_user: User = Depends(get_current_transporter), db: Session = Depends(get_db)
):
    query = db.query(trip_models.Trip).join(load_models.TransportRequest).filter(
        trip_models.Trip.transporter_id == current_user.id
    )
    
    if trip_status and trip_status.upper() != "ALL":
        query = query.filter(trip_models.Trip.status == trip_status.upper())
    
    if statuses:
        status_list = [s.strip().upper() for s in statuses.split(",")]
        query = query.filter(trip_models.Trip.status.in_(status_list))
        
    if search:
        search_term = f"%{search.strip()}%"
        query = query.filter(
            or_(
                trip_models.Trip.trip_code.ilike(search_term),
                load_models.TransportRequest.request_code.ilike(search_term),
                load_models.TransportRequest.pickup_city.ilike(search_term),
                load_models.TransportRequest.delivery_city.ilike(search_term),
                load_models.TransportRequest.goods_name.ilike(search_term)
            )
        )
        
    sort_column = trip_models.Trip.created_at
    if sort_by == "pickup_date":
        sort_column = load_models.TransportRequest.pickup_date
    elif sort_by == "payout":
        sort_column = load_models.TransportRequest.offered_amount
        
    if sort_order.lower() == "asc":
        query = query.order_by(asc(sort_column))
    else:
        query = query.order_by(desc(sort_column))
    
    total = query.count()
    trips = query.offset((page - 1) * limit).limit(limit).all()
    
    return success_response(
        data=trips,
        pagination=Pagination(page=page, limit=limit, total=total, total_pages=(total + limit - 1) // limit)
    )

@router.get("/{trip_id}", response_model=StandardResponse[schemas.TripDetailResponse])
def get_trip_details(trip_id: int, current_user: User = Depends(get_current_transporter), db: Session = Depends(get_db)):
    trip = db.query(trip_models.Trip).filter(
        trip_models.Trip.id == trip_id,
        trip_models.Trip.transporter_id == current_user.id
    ).first()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    return success_response(data=trip)

@router.patch("/{trip_id}/status", response_model=StandardResponse[schemas.TripResponse])
def update_trip_status(
    trip_id: int, request: schemas.TripStatusUpdate, 
    current_user: User = Depends(get_current_transporter), db: Session = Depends(get_db)
):
    trip = db.query(trip_models.Trip).filter(
        trip_models.Trip.id == trip_id,
        trip_models.Trip.transporter_id == current_user.id
    ).first()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    
    valid_next = TRIP_FLOW.get(trip.status, [])
    if request.status not in valid_next:
        raise HTTPException(status_code=400, detail=f"Invalid transition from {trip.status} to {request.status}")
    
    # Record history
    history = trip_models.TripStatusHistory(
        trip_id=trip.id,
        old_status=trip.status,
        new_status=request.status,
        changed_by=current_user.id,
        remarks=request.remarks
    )
    db.add(history)
    
    # Update state and timestamps
    trip.status = request.status
    now = datetime.now(timezone.utc)
    if request.status == "GOING_TO_PICKUP": trip.going_to_pickup_at = now
    elif request.status == "PICKED_UP": trip.picked_up_at = now
    elif request.status == "IN_TRANSIT": trip.started_at = now
    elif request.status == "AT_DELIVERY": trip.reached_delivery_at = now
    elif request.status == "DELIVERED": trip.delivered_at = now
    elif request.status == "COMPLETED": 
        trip.completed_at = now
        
        # Add earnings to Wallet
        from app.modules.transporter.wallet.models import WalletTransaction
        import uuid
        
        # Load the transport request to get the estimated price
        if trip.request and trip.request.offered_amount:
            tx = WalletTransaction(
                transporter_id=trip.transporter_id,
                trip_id=trip.id,
                transaction_type="CREDIT",
                amount=trip.request.offered_amount,
                reference_number=f"TRIP-PAY-{str(uuid.uuid4())[:8].upper()}",
                status="COMPLETED",
                description=f"Trip payout for {trip.trip_code or 'TRIP-' + str(trip.id)}"
            )
            db.add(tx)
            
        # Update TransporterProfile stats
        from app.modules.transporter.profile.models import TransporterProfile
        profile = db.query(TransporterProfile).filter(TransporterProfile.user_id == current_user.id).first()
        if profile:
            profile.completed_trips += 1
    
    db.commit()
    db.refresh(trip)
    return success_response(data=trip, message="Trip status updated")

@router.post("/{trip_id}/location", response_model=StandardResponse)
def update_trip_location(
    trip_id: int, request: schemas.TripLocationCreate, 
    current_user: User = Depends(get_current_transporter), db: Session = Depends(get_db)
):
    trip = db.query(trip_models.Trip).filter(
        trip_models.Trip.id == trip_id,
        trip_models.Trip.transporter_id == current_user.id
    ).first()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    
    loc = trip_models.TripLocation(
        trip_id=trip.id,
        transporter_id=current_user.id,
        latitude=request.latitude,
        longitude=request.longitude,
        speed=request.speed,
        heading=request.heading
    )
    db.add(loc)
    db.commit()
    return success_response(message="Location updated")

@router.post("/{trip_id}/documents", response_model=StandardResponse[schemas.TripDocumentResponse])
def upload_trip_document(
    trip_id: int, 
    document_type: str = Form(...),
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_transporter), 
    db: Session = Depends(get_db)
):
    trip = db.query(trip_models.Trip).filter(
        trip_models.Trip.id == trip_id,
        trip_models.Trip.transporter_id == current_user.id
    ).first()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    
    ext = os.path.splitext(file.filename)[1]
    filename = f"{trip.trip_code}_{document_type}_{uuid.uuid4().hex[:8]}{ext}"
    file_path = os.path.join(settings.UPLOAD_DIR, "trips", filename)
    
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    doc = trip_models.TripDocument(
        trip_id=trip.id,
        document_type=document_type,
        file_name=file.filename,
        file_path=file_path,
        file_url=f"/{file_path}",
        uploaded_by=current_user.id
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return success_response(data=doc, message="Document uploaded successfully")

@router.get("/{trip_id}/documents", response_model=StandardResponse[List[schemas.TripDocumentResponse]])
def get_trip_documents(trip_id: int, current_user: User = Depends(get_current_transporter), db: Session = Depends(get_db)):
    docs = db.query(trip_models.TripDocument).filter(
        trip_models.TripDocument.trip_id == trip_id
    ).join(trip_models.Trip).filter(
        trip_models.Trip.transporter_id == current_user.id
    ).all()
    return success_response(data=docs)

@router.delete("/{trip_id}/documents/{document_id}", response_model=StandardResponse)
def delete_trip_document(trip_id: int, document_id: int, current_user: User = Depends(get_current_transporter), db: Session = Depends(get_db)):
    doc = db.query(trip_models.TripDocument).filter(
        trip_models.TripDocument.id == document_id,
        trip_models.TripDocument.trip_id == trip_id
    ).join(trip_models.Trip).filter(
        trip_models.Trip.transporter_id == current_user.id
    ).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    if os.path.exists(doc.file_path):
        os.remove(doc.file_path)
        
    db.delete(doc)
    db.commit()
    return success_response(message="Document deleted successfully")
