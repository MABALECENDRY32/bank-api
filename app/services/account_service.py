from sqlalchemy.orm import Session
from app.repositories.account_repo import AccountRepository
from app.repositories.customer_repo import CustomerRepository
from app.repositories.transaction_repo import TransactionRepository
from app.models.account import Account
from app.schemas.account import AccountCreate, AccountResponse
from app.schemas.transaction import TransactionRequest
from app.models.transaction import TransactionType
from app.services.pin_service import PinService
from app.services.email_service import EmailService
from fastapi import HTTPException, status
from typing import List
from datetime import date, datetime
import logging

logger = logging.getLogger(__name__)

class AccountService:
    def __init__(self, db: Session):
        self.db = db
        self.account_repo = AccountRepository(db)
        self.customer_repo = CustomerRepository(db)
        self.transaction_repo = TransactionRepository(db)
        self.email_service = EmailService()
    
    def create_account(self, customer_id: int, account_data: AccountCreate) -> AccountResponse:
        # Check if customer exists
        customer = self.customer_repo.get_by_id(customer_id)
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Customer not found"
            )
        
        # Generate unique account number
        account_number = Account.generate_account_number()
        while self.account_repo.exists_by_account_number(account_number):
            account_number = Account.generate_account_number()
        
        # Create account
        account_dict = {
            "account_number": account_number,
            "account_type": account_data.account_type,
            "balance": 0.0,
            "customer_id": customer_id
        }
        
        account = self.account_repo.create(account_dict)
        
        # Send account creation notification
        self.email_service.send_email(
            to_email=customer.email,
            subject=f"New Account Created - {account.account_number}",
            body=f"""
Dear {customer.full_name},

A new {account.account_type.value} account has been created for you.

Account Number: {account.account_number}
Account Type: {account.account_type.value}
Current Balance: ${account.balance:.2f}

You can now start using your account to deposit, withdraw, and transfer money.

Best regards,
The Medium Bank Team
"""
        )
        
        return AccountResponse.model_validate(account)
    
    def get_customer_accounts(self, customer_id: int) -> List[AccountResponse]:
        accounts = self.account_repo.get_by_customer_id(customer_id)
        return [AccountResponse.model_validate(acc) for acc in accounts]
    
    def deposit(self, account_number: str, transaction_data: TransactionRequest, pin: str = None) -> dict:
    # Get account
        account = self.account_repo.get_by_account_number(account_number)
        if not account:
            raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found"
        )
    
    # Check if customer account is frozen
        customer = self.customer_repo.get_by_id(account.customer_id)
        if customer and customer.is_frozen:
            raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Account is frozen. Reason: {customer.freeze_reason or 'No reason provided'}"
        )
    
        # Create transaction record
        transaction_dict = {
            "amount": transaction_data.amount,
            "transaction_type": TransactionType.DEPOSIT,
            "description": transaction_data.description or "Deposit",
            "account_id": account.id
        }
        self.transaction_repo.create(transaction_dict)
        
        # Get customer for email
        customer = self.customer_repo.get_by_id(account.customer_id)
        
        # Send deposit confirmation email
        if customer:
            self.email_service.send_deposit_email(
                customer.email,
                customer.full_name,
                transaction_data.amount,
                account.balance,
                account.account_number
            )
        
        return {
            "message": f"Successfully deposited ${transaction_data.amount:.2f}",
            "new_balance": account.balance
        }
    
    def withdraw(self, account_number: str, transaction_data: TransactionRequest) -> dict:
        # Get account
        account = self.account_repo.get_by_account_number(account_number)
        if not account:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Account not found"
            )

        customer = self.customer_repo.get_by_id(account.customer_id)
        if customer and customer.is_frozen:
            raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Account is frozen. Reason: {customer.freeze_reason or 'No reason provided'}"
        )

        
        # Get customer
        customer = self.customer_repo.get_by_id(account.customer_id)
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Customer not found"
            )
        
        # Reset daily limits if new day
        self.customer_repo.reset_daily_limits(customer)
        
        # Check if customer has enough daily withdrawal limit
        remaining_limit = customer.daily_withdrawal_limit - customer.daily_withdrawal_used
        if transaction_data.amount > remaining_limit:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Daily withdrawal limit exceeded. Remaining limit: ${remaining_limit:.2f}"
            )
        
        # Check sufficient funds
        if account.balance < transaction_data.amount:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Insufficient funds"
            )
        
        # Update balance
        account.balance -= transaction_data.amount
        self.account_repo.update(account)
        
        # Update daily withdrawal usage
        customer.daily_withdrawal_used += transaction_data.amount
        self.customer_repo.update(customer)
        
        # Create transaction record
        transaction_dict = {
            "amount": transaction_data.amount,
            "transaction_type": TransactionType.WITHDRAWAL,
            "description": transaction_data.description or "Withdrawal",
            "account_id": account.id
        }
        self.transaction_repo.create(transaction_dict)
        
        # Send withdrawal confirmation email
        if customer:
            self.email_service.send_withdrawal_email(
                customer.email,
                customer.full_name,
                transaction_data.amount,
                account.balance,
                account.account_number
            )
        
        return {
            "message": f"Successfully withdrew ${transaction_data.amount:.2f}",
            "new_balance": account.balance,
            "daily_limit_used": customer.daily_withdrawal_used,
            "daily_limit_remaining": customer.daily_withdrawal_limit - customer.daily_withdrawal_used
        }
    
    def get_balance(self, account_number: str) -> dict:
        account = self.account_repo.get_by_account_number(account_number)
        if not account:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Account not found"
            )
        
        return {
            "account_number": account.account_number,
            "balance": account.balance,
            "account_type": account.account_type,
            "customer_id": account.customer_id
        }
    
    def get_account_by_number(self, account_number: str) -> Account:
        account = self.account_repo.get_by_account_number(account_number)
        if not account:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Account not found"
            )
        return account