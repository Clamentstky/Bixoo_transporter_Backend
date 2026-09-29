from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.common.responses import StandardResponse, success_response, Pagination
from app.core.dependencies import get_current_transporter
from app.modules.auth.models import User
from app.modules.transporter.settlements import models as settlement_models
from app.modules.transporter.wallet.schemas import SettlementResponse
from typing import List

router = APIRouter(prefix="/api/v1/transporter/settlements", tags=["settlements"])

@router.get("", response_model=StandardResponse[List[SettlementResponse]])
def get_settlements(
    page: int = 1, limit: int = 10, status: str = None, 
    current_user: User = Depends(get_current_transporter), db: Session = Depends(get_db)
):
    query = db.query(settlement_models.Settlement).filter(settlement_models.Settlement.transporter_id == current_user.id)
    
    if status:
        query = query.filter(settlement_models.Settlement.status == status)
        
    total = query.count()
    settlements = query.order_by(settlement_models.Settlement.created_at.desc()).offset((page - 1) * limit).limit(limit).all()
    
    return success_response(
        data=settlements,
        pagination=Pagination(page=page, limit=limit, total=total, total_pages=(total + limit - 1) // limit)
    )

@router.get("/{id}", response_model=StandardResponse[SettlementResponse])
def get_settlement(id: int, current_user: User = Depends(get_current_transporter), db: Session = Depends(get_db)):
    settlement = db.query(settlement_models.Settlement).filter(
        settlement_models.Settlement.id == id,
        settlement_models.Settlement.transporter_id == current_user.id
    ).first()
    if not settlement:
        raise HTTPException(status_code=404, detail="Settlement not found")
    
    return success_response(data=settlement)
