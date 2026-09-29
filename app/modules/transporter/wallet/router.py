from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.db.session import get_db
from app.common.responses import StandardResponse, success_response, Pagination
from app.core.dependencies import get_current_transporter
from app.modules.auth.models import User
from app.modules.transporter.wallet import models as wallet_models, schemas
from app.modules.transporter.settlements.models import Settlement
from decimal import Decimal

router = APIRouter(prefix="/api/v1/transporter/wallet", tags=["wallet"])

from sqlalchemy import or_, asc, desc

@router.get("", response_model=StandardResponse[schemas.WalletSummaryResponse])
def get_wallet(
    page: int = 1, limit: int = 20, 
    type: str = None, search: str = None,
    sort_order: str = "desc",
    current_user: User = Depends(get_current_transporter), db: Session = Depends(get_db)
):
    # Calculate balances
    credit_sum = db.query(func.sum(wallet_models.WalletTransaction.amount)).filter(
        wallet_models.WalletTransaction.transporter_id == current_user.id,
        wallet_models.WalletTransaction.transaction_type == "CREDIT",
        wallet_models.WalletTransaction.status == "COMPLETED"
    ).scalar() or Decimal('0.00')
    
    debit_sum = db.query(func.sum(wallet_models.WalletTransaction.amount)).filter(
        wallet_models.WalletTransaction.transporter_id == current_user.id,
        wallet_models.WalletTransaction.transaction_type == "DEBIT",
        wallet_models.WalletTransaction.status == "COMPLETED"
    ).scalar() or Decimal('0.00')
    
    available_balance = credit_sum - debit_sum
    
    pending_amount = db.query(func.sum(Settlement.net_amount)).filter(
        Settlement.transporter_id == current_user.id,
        Settlement.status.in_(["PENDING", "PROCESSING"])
    ).scalar() or Decimal('0.00')
    
    total_earnings = credit_sum  
    
    # Get recent transactions with filter
    tx_query = db.query(wallet_models.WalletTransaction).filter(
        wallet_models.WalletTransaction.transporter_id == current_user.id
    )
    
    if type and type.upper() != "ALL":
        tx_query = tx_query.filter(wallet_models.WalletTransaction.transaction_type == type.upper())
        
    if search:
        search_term = f"%{search.strip()}%"
        tx_query = tx_query.filter(
            or_(
                wallet_models.WalletTransaction.reference_id.ilike(search_term),
                wallet_models.WalletTransaction.description.ilike(search_term)
            )
        )
        
    if sort_order.lower() == "asc":
        tx_query = tx_query.order_by(wallet_models.WalletTransaction.created_at.asc())
    else:
        tx_query = tx_query.order_by(wallet_models.WalletTransaction.created_at.desc())
        
    total_tx = tx_query.count()
    transactions = tx_query.offset((page - 1) * limit).limit(limit).all()
    
    # We can pack total_tx into the response
    return success_response(
        data={
            "available_balance": available_balance,
            "pending_amount": pending_amount,
            "total_earnings": total_earnings,
            "transactions": transactions,
        },
        pagination=Pagination(
            page=page,
            limit=limit,
            total=total_tx,
            total_pages=(total_tx + limit - 1) // limit
        )
    )
