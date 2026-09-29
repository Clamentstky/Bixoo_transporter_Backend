from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.common.responses import StandardResponse, success_response
from app.core.dependencies import get_current_transporter
from app.modules.auth.models import User
from app.modules.transporter.chats import models as chat_models, schemas

from typing import List

router = APIRouter(prefix="/api/v1/transporter/chats", tags=["chats"])

@router.get("/{trip_id}/messages", response_model=StandardResponse[List[schemas.ChatMessageResponse]])
def get_trip_messages(
    trip_id: int, 
    current_user: User = Depends(get_current_transporter), 
    db: Session = Depends(get_db)
):
    messages = db.query(chat_models.ChatMessage).filter(
        chat_models.ChatMessage.trip_id == trip_id
    ).order_by(chat_models.ChatMessage.created_at.asc()).all()
    
    return success_response(data=messages)

@router.post("/{trip_id}/messages", response_model=StandardResponse[schemas.ChatMessageResponse])
def send_trip_message(
    trip_id: int, 
    request: schemas.ChatMessageCreate,
    current_user: User = Depends(get_current_transporter), 
    db: Session = Depends(get_db)
):
    msg = chat_models.ChatMessage(
        trip_id=trip_id,
        sender_id=current_user.id,
        sender_type="TRANSPORTER",
        message=request.message
    )
    db.add(msg)
    db.commit()
    db.refresh(msg)
    
    return success_response(data=msg, message="Message sent")
