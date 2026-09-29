from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ChatMessageCreate(BaseModel):
    message: str

class ChatMessageResponse(BaseModel):
    id: int
    trip_id: int
    sender_id: int
    sender_type: str
    message: str
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True
