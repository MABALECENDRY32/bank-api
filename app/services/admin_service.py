from sqlalchemy.orm import Session
from sqlalchemy import func
from app.repositories.customer_repo import CustomerRepository
from app.repositories.account_repo import AccountRepository
from app.repositories.transaction_repo import TransactionRepository
from app.models.customer import Customer
from app.models.account import Account
from app.models.transaction import Transaction
from app.schemas.admin import (
    AdminDashboardStats, AdminUserResponse, AdminUserUpdate,
    FreezeAccountRequest, UnfreezeAccountRequest
)
from app.schemas.customer import CustomerResponse
from app.schemas.account import AccountResponse
from app.schemas.transaction import TransactionResponse
from app.core.security import get_password_hash
from fastapi import HTTPException, status
from datetime import datetime
from typing import List, Optional


class AdminService:
    def __init__(self, db: Session):
        self.db = db
        self.customer_repo = CustomerRepository(db)
        self.account_repo = AccountRepository(db)
        self.transaction_repo = TransactionRepository(db)
    
    def check_admin(self, customer_id: int):
        """Check if user is admin"""
        customer = self.customer_repo.get_by_id(customer_id)
        if not customer or not customer.is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin access required"
            )
        return customer
    
    def get_dashboard_stats(self) -> AdminDashboardStats:
        """Get dashboard statistics"""
        total_users = self.db.query(Customer).count()
        active_users = self.db.query(Customer).filter(Customer.is_active == True).count()
        total_accounts = self.db.query(Account).count()
        total_transactions = self.db.query(Transaction).count()
        frozen_accounts = self.db.query(Customer).filter(Customer.is_frozen == True).count()
        
        # Total balance across all accounts
        total_balance = self.db.query(func.sum(Account.balance)).scalar() or 0.0
        
        return AdminDashboardStats(
            total_users=total_users,
            active_users=active_users,
            total_accounts=total_accounts,
            total_transactions=total_transactions,
            total_balance=float(total_balance),
            frozen_accounts=frozen_accounts,
            pending_transactions=0
        )
    
    def get_all_users(self, skip: int = 0, limit: int = 100) -> List[CustomerResponse]:
        """Get all users with pagination"""
        users = self.db.query(Customer).offset(skip).limit(limit).all()
        return [CustomerResponse.model_validate(user) for user in users]
    
    def get_user_details(self, user_id: int) -> AdminUserResponse:
        """Get detailed user information"""
        customer = self.customer_repo.get_by_id(user_id)
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        accounts = self.account_repo.get_by_customer_id(user_id)
        recent_transactions = self.db.query(Transaction)\
            .join(Account)\
            .filter(Account.customer_id == user_id)\
            .order_by(Transaction.created_at.desc())\
            .limit(10)\
            .all()
        
        return AdminUserResponse(
            customer=CustomerResponse.model_validate(customer),
            accounts=[AccountResponse.model_validate(acc) for acc in accounts],
            recent_transactions=[TransactionResponse.model_validate(t) for t in recent_transactions],
            is_frozen=customer.is_frozen,
            freeze_reason=customer.freeze_reason
        )
    
    def update_user(self, user_id: int, user_data: AdminUserUpdate) -> CustomerResponse:
        """Update user information"""
        customer = self.customer_repo.get_by_id(user_id)
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        update_data = user_data.model_dump(exclude_unset=True)
        
        # Hash password if provided
        if 'password' in update_data:
            update_data['hashed_password'] = get_password_hash(update_data.pop('password'))
        
        for key, value in update_data.items():
            setattr(customer, key, value)
        
        self.customer_repo.update(customer)
        return CustomerResponse.model_validate(customer)
    
    def freeze_account(self, user_id: int, reason: FreezeAccountRequest) -> dict:
        """Freeze a user account"""
        customer = self.customer_repo.get_by_id(user_id)
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        if customer.is_frozen:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Account is already frozen"
            )
        
        customer.is_frozen = True
        customer.freeze_reason = reason.freeze_reason
        customer.frozen_at = datetime.utcnow()
        self.customer_repo.update(customer)
        
        return {
            "message": "Account frozen successfully",
            "user_id": user_id,
            "reason": reason.freeze_reason
        }
    
    def unfreeze_account(self, user_id: int, reason: UnfreezeAccountRequest) -> dict:
        """Unfreeze a user account"""
        customer = self.customer_repo.get_by_id(user_id)
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        if not customer.is_frozen:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Account is not frozen"
            )
        
        customer.is_frozen = False
        customer.freeze_reason = None
        customer.frozen_at = None
        self.customer_repo.update(customer)
        
        return {
            "message": "Account unfrozen successfully",
            "user_id": user_id,
            "reason": reason.unfreeze_reason
        }
    
    def create_admin_user(self, full_name: str, email: str, phone: str, password: str) -> CustomerResponse:
        """Create a new admin user"""
        # Check if email exists
        if self.customer_repo.exists_by_email(email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Check if phone exists
        if self.customer_repo.exists_by_phone(phone):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Phone number already registered"
            )
        
        # Hash password
        hashed_password = get_password_hash(password)
        
        # Create admin
        customer_dict = {
            "full_name": full_name,
            "email": email,
            "phone": phone,
            "hashed_password": hashed_password,
            "is_admin": True,
            "is_active": True
        }
        
        customer = self.customer_repo.create(customer_dict)
        return CustomerResponse.model_validate(customer)