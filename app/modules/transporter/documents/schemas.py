from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import date, datetime
from .models import DocumentType, DocumentStatus

class DocumentBase(BaseModel):
    document_type: DocumentType
    document_number_masked: Optional[str] = None
    file_url: Optional[str] = None
    back_file_url: Optional[str] = None
    issue_date: Optional[date] = None
    expiry_date: Optional[date] = None
    status: DocumentStatus
    rejection_reason: Optional[str] = None

class DocumentResponse(DocumentBase):
    id: int
    transporter_id: int
    uploaded_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class DocumentStatusResponse(BaseModel):
    document_type: DocumentType
    status: DocumentStatus
    message: Optional[str] = None
    uploaded_at: Optional[datetime] = None
    expiry_date: Optional[date] = None

    model_config = ConfigDict(from_attributes=True)
