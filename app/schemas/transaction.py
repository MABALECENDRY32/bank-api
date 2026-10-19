from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from app.models.transaction import TransactionType

class TransactionRequest(BaseModel):
    amount: float = Field(..., gt=0.01)
    description: Optional[str] = None

class TransferRequest(BaseModel):
    from_account_number: str = Field(..., min_length=10, max_length=10)
    to_account_number: str = Field(..., min_length=10, max_length=10)
    amount: float = Field(..., gt=0.01)
    description: Optional[str] = None

class TransactionResponse(BaseModel):
    id: int
    amount: float
    transaction_type: TransactionType
    description: Optional[str]
    account_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True