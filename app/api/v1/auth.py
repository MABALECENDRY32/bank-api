from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.schemas.customer import CustomerCreate, CustomerLogin, CustomerResponse, TokenResponse, OTPRequest, OTPVerify
from app.services.auth_service import AuthService
from app.services.pin_service import PinService
from app.services.sms_service import SMSService

router = APIRouter(prefix="/auth", tags=["Authentication"])

def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    return AuthService(db)

@router.post("/register", response_model=CustomerResponse, status_code=status.HTTP_201_CREATED)
def register(
    customer_data: CustomerCreate,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Register a new customer with phone number and PIN"""
    return auth_service.register(customer_data)

@router.post("/login", response_model=TokenResponse)
def login(
    login_data: CustomerLogin,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Login with phone number and PIN"""
    return auth_service.login(login_data)

@router.post("/request-otp")
def request_otp(
    request: OTPRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Request OTP for login"""
    return auth_service.request_otp(request.phone)

@router.post("/verify-otp", response_model=TokenResponse)
def verify_otp(
    request: OTPVerify,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Verify OTP and login"""
    return auth_service.verify_otp_and_login(request.phone, request.otp)

@router.get("/me", response_model=CustomerResponse)
def get_current_user_profile(
    current_user = Depends(get_current_user)
):
    """Get the current authenticated user's profile"""
    return CustomerResponse.model_validate(current_user)