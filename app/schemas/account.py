from pydantic import BaseModel
from datetime import datetime
from app.models.account import AccountType

class AccountCreate(BaseModel):
    account_type: AccountType

class AccountResponse(BaseModel):
    id: int
    account_number: str
    account_type: AccountType
    balance: float
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True