from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.customer import Customer
from app.services.admin_service import AdminService
from app.schemas.admin import (
    AdminDashboardStats, AdminUserResponse, AdminUserUpdate,
    AdminUserCreate, FreezeAccountRequest, UnfreezeAccountRequest,
    AdminTransactionFilter
)
from app.schemas.customer import CustomerResponse

router = APIRouter(prefix="/admin", tags=["Admin"])

def get_admin_service(db: Session = Depends(get_db)) -> AdminService:
    return AdminService(db)

def get_admin_user(current_user: Customer = Depends(get_current_user)):
    """Check if current user is admin"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user

@router.get("/dashboard", response_model=AdminDashboardStats)
def get_dashboard_stats(
    admin: Customer = Depends(get_admin_user),
    admin_service: AdminService = Depends(get_admin_service)
):
    """Get dashboard statistics"""
    return admin_service.get_dashboard_stats()

@router.get("/users", response_model=List[CustomerResponse])
def get_all_users(
    skip: int = 0,
    limit: int = 100,
    admin: Customer = Depends(get_admin_user),
    admin_service: AdminService = Depends(get_admin_service)
):
    """Get all users with pagination"""
    return admin_service.get_all_users(skip, limit)

@router.get("/users/{user_id}", response_model=AdminUserResponse)
def get_user_details(
    user_id: int,
    admin: Customer = Depends(get_admin_user),
    admin_service: AdminService = Depends(get_admin_service)
):
    """Get detailed user information"""
    return admin_service.get_user_details(user_id)

@router.put("/users/{user_id}", response_model=CustomerResponse)
def update_user(
    user_id: int,
    user_data: AdminUserUpdate,
    admin: Customer = Depends(get_admin_user),
    admin_service: AdminService = Depends(get_admin_service)
):
    """Update user information"""
    return admin_service.update_user(user_id, user_data)

@router.post("/users/{user_id}/freeze")
def freeze_account(
    user_id: int,
    reason: FreezeAccountRequest,
    admin: Customer = Depends(get_admin_user),
    admin_service: AdminService = Depends(get_admin_service)
):
    """Freeze a user account"""
    return admin_service.freeze_account(user_id, reason)

@router.post("/users/{user_id}/unfreeze")
def unfreeze_account(
    user_id: int,
    reason: UnfreezeAccountRequest,
    admin: Customer = Depends(get_admin_user),
    admin_service: AdminService = Depends(get_admin_service)
):
    """Unfreeze a user account"""
    return admin_service.unfreeze_account(user_id, reason)

@router.post("/create-admin", response_model=CustomerResponse)
def create_admin_user(
    user_data: AdminUserCreate,
    admin_service: AdminService = Depends(get_admin_service)
):
    """Create a new admin user (First admin only)"""
    return admin_service.create_admin_user(
        user_data.full_name,
        user_data.email,
        user_data.phone,
        user_data.password
    )

@router.get("/users/search")
def search_users(
    query: str,
    admin: Customer = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Search for users by name or email"""
    users = db.query(Customer).filter(
        (Customer.full_name.ilike(f"%{query}%")) |
        (Customer.email.ilike(f"%{query}%"))
    ).limit(10).all()
    
    return [CustomerResponse.model_validate(user) for user in users]