from sqlalchemy.orm import Session
from app.repositories.customer_repo import CustomerRepository
from app.core.security import get_password_hash, verify_password, create_access_token
from app.schemas.customer import CustomerCreate, CustomerLogin, CustomerResponse
from app.services.pin_service import PinService
from app.services.sms_service import SMSService
from app.services.otp_service import OTPService
from fastapi import HTTPException, status
import logging

logger = logging.getLogger(__name__)

class AuthService:
    def __init__(self, db: Session):
        self.db = db
        self.customer_repo = CustomerRepository(db)
        self.pin_service = PinService(db)
        self.sms_service = SMSService()
        self.otp_service = OTPService()
    
    def register(self, customer_data: CustomerCreate) -> CustomerResponse:
        """Register a new customer with phone number and PIN"""
        # Check if phone exists
        if self.customer_repo.exists_by_phone(customer_data.phone):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Phone number already registered"
            )
        
        # Hash PIN
        hashed_pin = get_password_hash(customer_data.pin)
        
        # Create customer
        customer_dict = {
            "full_name": customer_data.full_name,
            "phone": customer_data.phone,
            "email": customer_data.email,
            "address": customer_data.address,
            "hashed_pin": hashed_pin,
            "pin_enabled": True,
            "is_active": True
        }
        
        customer = self.customer_repo.create(customer_dict)
        
        # Send welcome SMS
        self.sms_service.send_sms(
            customer.phone,
            f"🏦 Welcome to BLUE Bank, {customer.full_name}! Your account has been created successfully."
        )
        
        return CustomerResponse.model_validate(customer)
    
    def login(self, login_data: CustomerLogin) -> dict:
        """Login with phone number and PIN"""
        # Find customer by phone
        customer = self.customer_repo.get_by_phone(login_data.phone)
        
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
        
        # Check if user is active
        if not customer.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is deactivated"
            )
        
        # Check if user is frozen
        if customer.is_frozen:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Account is frozen. Reason: {customer.freeze_reason or 'No reason provided'}"
            )
        
        # Verify PIN
        try:
            self.pin_service.verify_pin(customer.id, login_data.pin)
        except HTTPException as e:
            raise e
        
        # Create JWT token
        token_data = {"sub": customer.phone}
        access_token = create_access_token(token_data)
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "customer": CustomerResponse.model_validate(customer),
            "login_method": "pin"
        }
    
    def request_otp(self, phone: str) -> dict:
        """Request OTP for login"""
        # Check if phone exists
        customer = self.customer_repo.get_by_phone(phone)
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Phone number not found"
            )
        
        # Generate OTP
        otp = self.otp_service.generate_otp(phone)
        
        # Send SMS
        self.sms_service.send_login_otp(phone, otp)
        
        return {
            "message": "OTP sent successfully",
            "expires_in": 600  # 10 minutes
        }
    
    def verify_otp_and_login(self, phone: str, otp: str) -> dict:
        """Verify OTP and login"""
        # Verify OTP
        if not self.otp_service.verify_otp(phone, otp):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired OTP"
            )
        
        # Get customer
        customer = self.customer_repo.get_by_phone(phone)
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Create JWT token
        token_data = {"sub": customer.phone}
        access_token = create_access_token(token_data)
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "customer": CustomerResponse.model_validate(customer),
            "login_method": "otp"
        }