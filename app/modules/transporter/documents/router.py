import os
import uuid
from typing import List, Optional
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.dependencies import get_current_user
from app.modules.auth.models import User
from .models import TransporterDocument, DocumentType, DocumentStatus
from .schemas import DocumentResponse, DocumentStatusResponse

router = APIRouter(
    prefix="/api/v1/transporter/documents",
    tags=["Transporter Documents"],
)

UPLOAD_DIR = "uploads/transporter_documents"

def get_file_extension(filename: str) -> str:
    if not filename:
        return ""
    return os.path.splitext(filename)[1].lower()

def safe_filename(transporter_id: int, doc_type: str, ext: str) -> str:
    unique_id = uuid.uuid4().hex[:8]
    return f"{doc_type.lower()}_{transporter_id}_{unique_id}{ext}"

@router.get("", response_model=List[DocumentResponse])
def get_documents(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    docs = db.query(TransporterDocument).filter(TransporterDocument.transporter_id == current_user.id).all()
    return docs

@router.get("/status", response_model=List[DocumentStatusResponse])
def get_document_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    docs = db.query(TransporterDocument).filter(TransporterDocument.transporter_id == current_user.id).all()
    
    # Pre-fill expected documents
    expected_types = [DocumentType.DRIVING_LICENSE, DocumentType.AADHAAR_CARD]
    existing_map = {doc.document_type: doc for doc in docs}
    
    result = []
    for t in expected_types:
        if t in existing_map:
            doc = existing_map[t]
            msg = doc.rejection_reason if doc.status == DocumentStatus.REJECTED else None
            if doc.status == DocumentStatus.VERIFIED and doc.expiry_date and doc.expiry_date < date.today():
                doc.status = DocumentStatus.EXPIRED
                msg = "Document has expired"
                
            result.append(DocumentStatusResponse(
                document_type=t,
                status=doc.status,
                message=msg,
                uploaded_at=doc.uploaded_at,
                expiry_date=doc.expiry_date
            ))
        else:
            result.append(DocumentStatusResponse(
                document_type=t,
                status=DocumentStatus.NOT_SUBMITTED,
                message="Not submitted",
                uploaded_at=None,
                expiry_date=None
            ))
            
    return result

@router.get("/{document_type}", response_model=DocumentResponse)
def get_document(
    document_type: DocumentType,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    doc = db.query(TransporterDocument).filter(
        TransporterDocument.transporter_id == current_user.id,
        TransporterDocument.document_type == document_type
    ).first()
    
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
        
    return doc

@router.post("", response_model=DocumentResponse)
async def upload_document(
    document_type: DocumentType = Form(...),
    document_number: str = Form(...),
    issue_date: Optional[date] = Form(None),
    expiry_date: Optional[date] = Form(None),
    front_file: UploadFile = File(...),
    back_file: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    allowed_exts = [".jpg", ".jpeg", ".png", ".pdf"]
    front_ext = get_file_extension(front_file.filename)
    
    if front_ext not in allowed_exts:
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {front_ext}")
        
    # Create upload dir
    user_upload_dir = os.path.join(UPLOAD_DIR, str(current_user.id))
    os.makedirs(user_upload_dir, exist_ok=True)
    
    front_filename = safe_filename(current_user.id, document_type.value, front_ext)
    front_path = os.path.join(user_upload_dir, front_filename)
    
    with open(front_path, "wb") as f:
        content = await front_file.read()
        f.write(content)
        
    back_path = None
    if back_file:
        back_ext = get_file_extension(back_file.filename)
        if back_ext not in allowed_exts:
             raise HTTPException(status_code=400, detail=f"Unsupported file type: {back_ext}")
             
        back_filename = safe_filename(current_user.id, document_type.value + "_back", back_ext)
        back_path = os.path.join(user_upload_dir, back_filename)
        with open(back_path, "wb") as f:
            content = await back_file.read()
            f.write(content)

    # Masking logic
    masked_number = ""
    if document_number:
        if document_type == DocumentType.AADHAAR_CARD and len(document_number) == 12:
            masked_number = f"XXXX XXXX {document_number[-4:]}"
        elif len(document_number) > 4:
            masked_number = f"{'X' * (len(document_number)-4)}{document_number[-4:]}"
        else:
            masked_number = document_number

    # Check if exists
    doc = db.query(TransporterDocument).filter(
        TransporterDocument.transporter_id == current_user.id,
        TransporterDocument.document_type == document_type
    ).first()
    
    if doc:
        doc.document_number = document_number
        doc.document_number_masked = masked_number
        doc.file_path = front_path
        doc.file_url = f"/static/{front_path}"
        if back_path:
            doc.back_file_path = back_path
            doc.back_file_url = f"/static/{back_path}"
        doc.issue_date = issue_date
        doc.expiry_date = expiry_date
        doc.status = DocumentStatus.PENDING
        doc.rejection_reason = None
    else:
        doc = TransporterDocument(
            transporter_id=current_user.id,
            document_type=document_type,
            document_number=document_number,
            document_number_masked=masked_number,
            file_path=front_path,
            file_url=f"/static/{front_path}",
            back_file_path=back_path,
            back_file_url=f"/static/{back_path}" if back_path else None,
            issue_date=issue_date,
            expiry_date=expiry_date,
            status=DocumentStatus.PENDING
        )
        db.add(doc)
        
    db.commit()
    db.refresh(doc)
    
    return doc
