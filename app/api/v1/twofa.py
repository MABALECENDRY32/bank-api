from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.customer import Customer
from app.services.twofa_service import TwoFAService
from app.schemas.twofa import (
    TwoFASetupResponse, TwoFAEnableRequest, 
    TwoFAVerifyRequest, TwoFADisableRequest,
    TwoFAStatusResponse
)

router = APIRouter(prefix="/2fa", tags=["Two-Factor Authentication"])

def get_twofa_service(db: Session = Depends(get_db)) -> TwoFAService:
    return TwoFAService(db)

@router.post("/setup", response_model=TwoFASetupResponse)
def setup_2fa(
    current_user: Customer = Depends(get_current_user),
    twofa_service: TwoFAService = Depends(get_twofa_service)
):
    """Setup 2FA - generates secret and QR code"""
    result = twofa_service.setup_2fa(current_user.id)
    return result

@router.post("/enable")
def enable_2fa(
    request: TwoFAEnableRequest,
    current_user: Customer = Depends(get_current_user),
    twofa_service: TwoFAService = Depends(get_twofa_service)
):
    """Enable 2FA after verification"""
    return twofa_service.enable_2fa(current_user.id, request.secret, request.totp_code)

@router.post("/disable")
def disable_2fa(
    request: TwoFADisableRequest,
    current_user: Customer = Depends(get_current_user),
    twofa_service: TwoFAService = Depends(get_twofa_service)
):
    """Disable 2FA"""
    return twofa_service.disable_2fa(current_user.id, request.totp_code)

@router.get("/status", response_model=TwoFAStatusResponse)
def get_2fa_status(
    current_user: Customer = Depends(get_current_user),
    twofa_service: TwoFAService = Depends(get_twofa_service)
):
    """Get 2FA status for current user"""
    return twofa_service.get_2fa_status(current_user.id)