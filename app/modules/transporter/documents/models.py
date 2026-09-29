from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.db.base import Base

class DocumentStatus(str, enum.Enum):
    NOT_SUBMITTED = "NOT_SUBMITTED"
    PENDING = "PENDING"
    VERIFIED = "VERIFIED"
    REJECTED = "REJECTED"
    EXPIRED = "EXPIRED"

class DocumentType(str, enum.Enum):
    DRIVING_LICENSE = "DRIVING_LICENSE"
    AADHAAR_CARD = "AADHAAR_CARD"
    PAN_CARD = "PAN_CARD"
    RC_BOOK = "RC_BOOK"
    INSURANCE = "INSURANCE"
    FITNESS_CERTIFICATE = "FITNESS_CERTIFICATE"
    PERMIT = "PERMIT"
    PROFILE_ID_PROOF = "PROFILE_ID_PROOF"
    OTHER = "OTHER"

class TransporterDocument(Base):
    __tablename__ = "transporter_documents"

    id = Column(Integer, primary_key=True, index=True)
    transporter_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    document_type = Column(Enum(DocumentType), nullable=False)
    document_number = Column(String(255), nullable=True)
    document_number_masked = Column(String(255), nullable=True)
    
    file_path = Column(String(1024), nullable=True)
    file_url = Column(String(1024), nullable=True)
    back_file_path = Column(String(1024), nullable=True)
    back_file_url = Column(String(1024), nullable=True)
    
    issue_date = Column(Date, nullable=True)
    expiry_date = Column(Date, nullable=True)
    
    status = Column(Enum(DocumentStatus), default=DocumentStatus.PENDING, nullable=False)
    rejection_reason = Column(String(1024), nullable=True)
    
    verified_by = Column(Integer, nullable=True)  # Admin ID
    verified_at = Column(DateTime, nullable=True)
    
    uploaded_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    created_at = Column(DateTime, default=func.now())

    transporter = relationship("User", foreign_keys=[transporter_id])
