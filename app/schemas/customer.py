from pydantic import BaseModel, EmailStr, Field, validator
from datetime import datetime
from typing import Optional

class CustomerCreate(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=100)
    phone: str = Field(..., pattern=r'^\+?[1-9]\d{1,14}$')
    email: Optional[str] = None
    address: Optional[str] = None
    pin: str = Field(..., min_length=5, max_length=5)
    
    @validator('pin')
    def validate_pin(cls, v):
        if not v.isdigit():
            raise ValueError('PIN must contain only digits')
        return v

class CustomerLogin(BaseModel):
    phone: str
    pin: str = Field(..., min_length=5, max_length=5)
    
    @validator('pin')
    def validate_pin(cls, v):
        if not v.isdigit():
            raise ValueError('PIN must contain only digits')
        return v

class OTPRequest(BaseModel):
    phone: str

class OTPVerify(BaseModel):
    phone: str
    otp: str = Field(..., min_length=6, max_length=6)
    
    @validator('otp')
    def validate_otp(cls, v):
        if not v.isdigit():
            raise ValueError('OTP must contain only digits')
        return v

class CustomerResponse(BaseModel):
    id: int
    full_name: str
    phone: str
    email: Optional[str]
    address: Optional[str]
    is_active: bool
    is_admin: bool
    pin_enabled: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    customer: CustomerResponse
    login_method: str = "pin"  # "pin" or "otp"