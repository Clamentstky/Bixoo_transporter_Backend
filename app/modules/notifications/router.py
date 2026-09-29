from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.common.responses import StandardResponse, success_response, Pagination
from app.core.dependencies import get_current_user
from app.modules.auth.models import User
from app.modules.notifications import models, schemas
from datetime import datetime, timezone
from typing import List

router = APIRouter(prefix="/api/v1/notifications", tags=["notifications"])

@router.get("", response_model=StandardResponse[List[schemas.NotificationResponse]])
def get_notifications(
    page: int = 1, limit: int = 20, unread_only: bool = False,
    sort_order: str = "desc",
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    query = db.query(models.Notification).filter(models.Notification.user_id == current_user.id)
    if unread_only:
        query = query.filter(models.Notification.is_read == False)
        
    total = query.count()
    
    if sort_order.lower() == "asc":
        query = query.order_by(models.Notification.created_at.asc())
    else:
        query = query.order_by(models.Notification.created_at.desc())
        
    notifications = query.offset((page - 1) * limit).limit(limit).all()
    
    return success_response(
        data=notifications,
        pagination=Pagination(page=page, limit=limit, total=total, total_pages=(total + limit - 1) // limit)
    )

@router.patch("/{id}/read", response_model=StandardResponse)
def read_notification(id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    notification = db.query(models.Notification).filter(
        models.Notification.id == id,
        models.Notification.user_id == current_user.id
    ).first()
    
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    if not notification.is_read:
        notification.is_read = True
        notification.read_at = datetime.now(timezone.utc)
        db.commit()
        
    return success_response(message="Notification marked as read")

@router.patch("/read-all", response_model=StandardResponse)
def read_all_notifications(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    db.query(models.Notification).filter(
        models.Notification.user_id == current_user.id,
        models.Notification.is_read == False
    ).update({
        models.Notification.is_read: True,
        models.Notification.read_at: datetime.now(timezone.utc)
    }, synchronize_session=False)
    
    db.commit()
    return success_response(message="All notifications marked as read")
