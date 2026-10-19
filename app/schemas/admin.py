from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
from app.schemas.customer import CustomerResponse
from app.schemas.account import AccountResponse
from app.schemas.transaction import TransactionResponse

class AdminUserCreate(BaseModel):
    full_name: str
    email: str
    phone: str
    password: str
    is_admin: bool = True

class AdminUserUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    is_active: Optional[bool] = None
    is_admin: Optional[bool] = None
    daily_withdrawal_limit: Optional[float] = None
    daily_transfer_limit: Optional[float] = None

class FreezeAccountRequest(BaseModel):
    freeze_reason: str

class UnfreezeAccountRequest(BaseModel):
    unfreeze_reason: str

class AdminDashboardStats(BaseModel):
    total_users: int
    active_users: int
    total_accounts: int
    total_transactions: int
    total_balance: float
    frozen_accounts: int
    pending_transactions: int

class AdminUserResponse(BaseModel):
    customer: CustomerResponse
    accounts: List[AccountResponse]
    recent_transactions: List[TransactionResponse]
    is_frozen: bool
    freeze_reason: Optional[str]

class AdminTransactionFilter(BaseModel):
    user_id: Optional[int] = None
    account_id: Optional[int] = None
    transaction_type: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    min_amount: Optional[float] = None
    max_amount: Optional[float] = None