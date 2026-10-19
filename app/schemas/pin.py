from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime

class PinSetRequest(BaseModel):
    """Request to set up PIN"""
    current_password: str
    pin: str = Field(..., min_length=5, max_length=5)
    confirm_pin: str = Field(..., min_length=5, max_length=5)
    
    @validator('pin')
    def validate_pin(cls, v):
        if not v.isdigit():
            raise ValueError('PIN must contain only digits')
        return v
    
    @validator('confirm_pin')
    def validate_confirm_pin(cls, v):
        if not v.isdigit():
            raise ValueError('PIN must contain only digits')
        return v

class PinVerifyRequest(BaseModel):
    """Request to verify PIN"""
    pin: str = Field(..., min_length=5, max_length=5)
    
    @validator('pin')
    def validate_pin(cls, v):
        if not v.isdigit():
            raise ValueError('PIN must contain only digits')
        return v

class PinChangeRequest(BaseModel):
    """Request to change PIN"""
    current_pin: str = Field(..., min_length=5, max_length=5)
    new_pin: str = Field(..., min_length=5, max_length=5)
    confirm_pin: str = Field(..., min_length=5, max_length=5)
    
    @validator('current_pin', 'new_pin', 'confirm_pin')
    def validate_pin(cls, v):
        if not v.isdigit():
            raise ValueError('PIN must contain only digits')
        return v

class PinDisableRequest(BaseModel):
    """Request to disable PIN"""
    pin: str = Field(..., min_length=5, max_length=5)
    
    @validator('pin')
    def validate_pin(cls, v):
        if not v.isdigit():
            raise ValueError('PIN must contain only digits')
        return v

class PinStatusResponse(BaseModel):
    """PIN status response"""
    enabled: bool
    attempts_remaining: Optional[int] = None
    locked_until: Optional[datetime] = None

class PinRequiredResponse(BaseModel):
    """Response when PIN is required"""
    requires_pin: bool = True
    message: str = "PIN required for this action"