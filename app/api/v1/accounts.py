from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.customer import Customer
from app.schemas.account import AccountCreate, AccountResponse
from app.schemas.transaction import TransactionRequest
from app.services.account_service import AccountService
from typing import List

# Make sure router has a unique prefix
router = APIRouter(prefix="/accounts", tags=["Accounts"])

def get_account_service(db: Session = Depends(get_db)) -> AccountService:
    return AccountService(db)

@router.post("/create", response_model=AccountResponse, status_code=status.HTTP_201_CREATED)
def create_account(
    account_data: AccountCreate,
    current_user: Customer = Depends(get_current_user),
    account_service: AccountService = Depends(get_account_service)
):
    """Create a new bank account (checking or savings)"""
    return account_service.create_account(current_user.id, account_data)

@router.get("/my-accounts", response_model=List[AccountResponse])
def get_my_accounts(
    current_user: Customer = Depends(get_current_user),
    account_service: AccountService = Depends(get_account_service)
):
    """Get all accounts for the logged-in user"""
    return account_service.get_customer_accounts(current_user.id)

@router.post("/{account_number}/deposit")
def deposit(
    account_number: str,
    transaction_data: TransactionRequest,
    account_service: AccountService = Depends(get_account_service)
):
    """Deposit money into an account"""
    return account_service.deposit(account_number, transaction_data)

@router.post("/{account_number}/withdraw")
def withdraw(
    account_number: str,
    transaction_data: TransactionRequest,
    account_service: AccountService = Depends(get_account_service)
):
    """Withdraw money from an account"""
    return account_service.withdraw(account_number, transaction_data)

@router.get("/{account_number}/balance")
def get_balance(
    account_number: str,
    account_service: AccountService = Depends(get_account_service)
):
    """Check account balance"""
    return account_service.get_balance(account_number)