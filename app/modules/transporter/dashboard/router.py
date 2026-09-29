from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.db.session import get_db
from app.common.responses import StandardResponse, success_response
from app.core.dependencies import get_current_transporter
from app.modules.auth.models import User
from app.modules.transporter.trips.models import Trip
from app.modules.transporter.loads.models import TransportMatch
from app.modules.transporter.settlements.models import Settlement
from app.modules.notifications.models import Notification
from app.modules.transporter.wallet.models import WalletTransaction
from datetime import datetime, date
from decimal import Decimal

router = APIRouter(prefix="/api/v1/transporter/dashboard", tags=["dashboard"])

@router.get("", response_model=StandardResponse)
def get_dashboard(current_user: User = Depends(get_current_transporter), db: Session = Depends(get_db)):
    # Active Trip
    active_trip = db.query(Trip).filter(
        Trip.transporter_id == current_user.id,
        Trip.status.notin_(["COMPLETED", "CANCELLED"])
    ).order_by(Trip.created_at.desc()).first()
    
    # Available Loads (PENDING/VIEWED matches)
    available_loads_count = db.query(TransportMatch).filter(
        TransportMatch.transporter_id == current_user.id,
        TransportMatch.status.in_(["PENDING", "VIEWED"])
    ).count()
    
    today = date.today()
    # Today's loads
    today_loads_count = db.query(TransportMatch).filter(
        TransportMatch.transporter_id == current_user.id,
        TransportMatch.status.in_(["PENDING", "VIEWED"]),
        func.date(TransportMatch.created_at) == today
    ).count()
    
    # Today's completed trips
    today_completed_count = db.query(Trip).filter(
        Trip.transporter_id == current_user.id,
        Trip.status == "COMPLETED",
        func.date(Trip.completed_at) == today
    ).count()
    
    # Total completed trips
    total_completed_count = db.query(Trip).filter(
        Trip.transporter_id == current_user.id,
        Trip.status == "COMPLETED"
    ).count()
    
    # Pending Settlement Amount
    pending_settlement = db.query(func.sum(Settlement.net_amount)).filter(
        Settlement.transporter_id == current_user.id,
        Settlement.status.in_(["PENDING", "PROCESSING"])
    ).scalar() or Decimal('0.00')
    
    # Total Earnings (Credits)
    total_earnings = db.query(func.sum(WalletTransaction.amount)).filter(
        WalletTransaction.transporter_id == current_user.id,
        WalletTransaction.transaction_type == "CREDIT",
        WalletTransaction.status == "COMPLETED"
    ).scalar() or Decimal('0.00')
    
    # Recent Notifications
    recent_notifications = db.query(Notification).filter(
        Notification.user_id == current_user.id
    ).order_by(Notification.created_at.desc()).limit(5).all()
    
    return success_response(data={
        "stats": {
            "available_loads": available_loads_count,
            "today_available": today_loads_count,
            "today_completed": today_completed_count,
            "total_completed": total_completed_count,
            "pending_settlement": float(pending_settlement),
            "total_earnings": float(total_earnings)
        },
        "active_trip": {
            "trip_id": active_trip.trip_code if active_trip else None,
            "internal_id": active_trip.id if active_trip else None,
            "status": active_trip.status if active_trip else None,
            "pickup": active_trip.request.pickup_city if active_trip and active_trip.request else None,
            "delivery": active_trip.request.delivery_city if active_trip and active_trip.request else None,
            "load": f"{active_trip.request.weight} {active_trip.request.weight_unit} {active_trip.request.goods_name}" if active_trip and active_trip.request else None,
            "distance": f"{active_trip.request.estimated_distance} KM" if active_trip and active_trip.request else None
        } if active_trip else None,
        "recent_notifications": [
            {
                "id": n.id,
                "title": n.title,
                "message": n.message,
                "type": n.type,
                "is_read": n.is_read,
                "created_at": n.created_at
            } for n in recent_notifications
        ]
    })
