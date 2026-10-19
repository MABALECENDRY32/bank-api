from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.customer import Customer
from app.services.pin_service import PinService
from app.schemas.pin import ( # pyright: ignore[reportMissingImports]
    PinSetRequest, PinVerifyRequest, PinChangeRequest,
    PinDisableRequest, PinStatusResponse, PinRequiredResponse
)

router = APIRouter(prefix="/pin", tags=["PIN Security"])

def get_pin_service(db: Session = Depends(get_db)) -> PinService:
    return PinService(db)

@router.post("/set")
def set_pin(
    request: PinSetRequest,
    current_user: Customer = Depends(get_current_user),
    pin_service: PinService = Depends(get_pin_service)
):
    """Set up a new PIN for the current user"""
    if request.pin != request.confirm_pin:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="PINs do not match"
        )
    
    return pin_service.set_pin(
        current_user.id,
        request.current_password,
        request.pin
    )

@router.post("/verify")
def verify_pin(
    request: PinVerifyRequest,
    current_user: Customer = Depends(get_current_user),
    pin_service: PinService = Depends(get_pin_service)
):
    """Verify PIN for sensitive operations"""
    return pin_service.verify_pin(current_user.id, request.pin)

@router.post("/change")
def change_pin(
    request: PinChangeRequest,
    current_user: Customer = Depends(get_current_user),
    pin_service: PinService = Depends(get_pin_service)
):
    """Change the current PIN"""
    if request.new_pin != request.confirm_pin:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="PINs do not match"
        )
    
    return pin_service.change_pin(
        current_user.id,
        request.current_pin,
        request.new_pin
    )

@router.post("/disable")
def disable_pin(
    request: PinDisableRequest,
    current_user: Customer = Depends(get_current_user),
    pin_service: PinService = Depends(get_pin_service)
):
    """Disable PIN for the current user"""
    return pin_service.disable_pin(current_user.id, request.pin)

@router.get("/status", response_model=PinStatusResponse)
def get_pin_status(
    current_user: Customer = Depends(get_current_user),
    pin_service: PinService = Depends(get_pin_service)
):
    """Get the current PIN status"""
    return pin_service.get_pin_status(current_user.id)

@router.get("/required")
def is_pin_required(
    current_user: Customer = Depends(get_current_user),
    pin_service: PinService = Depends(get_pin_service)
):
    """Check if PIN is required for sensitive actions"""
    requires_pin = pin_service.require_pin_for_action(current_user.id)
    return PinRequiredResponse(
        requires_pin=requires_pin,
        message="PIN required for this action" if requires_pin else "No PIN required"
    )