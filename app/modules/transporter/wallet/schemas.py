from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from decimal import Decimal

class SettlementResponse(BaseModel):
    id: int
    trip_id: int
    trip_amount: Decimal
    platform_fee: Decimal
    tax_amount: Decimal
    deduction_amount: Decimal
    net_amount: Decimal
    status: str
    created_at: datetime
    processed_at: Optional[datetime]
    settled_at: Optional[datetime]

    class Config:
        from_attributes = True

class WalletTransactionResponse(BaseModel):
    id: int
    trip_id: Optional[int]
    transaction_type: str
    amount: Decimal
    reference_number: Optional[str]
    status: str
    description: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True

class WalletSummaryResponse(BaseModel):
    available_balance: Decimal
    pending_amount: Decimal
    total_earnings: Decimal
    transactions: List[WalletTransactionResponse] = []
