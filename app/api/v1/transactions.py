from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.customer import Customer
from app.schemas.transaction import TransferRequest, TransactionResponse
from app.services.transaction_service import TransactionService
from typing import List

router = APIRouter(prefix="/transactions", tags=["Transactions"])

def get_transaction_service(db: Session = Depends(get_db)) -> TransactionService:
    return TransactionService(db)

@router.post("/transfer")
def transfer(
    transfer_data: TransferRequest,
    current_user: Customer = Depends(get_current_user),
    transaction_service: TransactionService = Depends(get_transaction_service)
):
    """Transfer money between accounts"""
    return transaction_service.transfer(transfer_data)

@router.get("/history/{account_number}", response_model=List[TransactionResponse])
def get_transaction_history(
    account_number: str,
    limit: int = 100,
    current_user: Customer = Depends(get_current_user),
    transaction_service: TransactionService = Depends(get_transaction_service)
):
    """Get transaction history for a specific account"""
    return transaction_service.get_transaction_history(account_number, limit)