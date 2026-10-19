from sqlalchemy.orm import Session
from app.repositories.customer_repo import CustomerRepository
from app.core.security import get_password_hash, verify_password
from fastapi import HTTPException, status
from datetime import datetime, timedelta
import logging
import random

logger = logging.getLogger(__name__)

class PinService:
    def __init__(self, db: Session):
        self.db = db
        self.customer_repo = CustomerRepository(db)
        self.MAX_PIN_ATTEMPTS = 5
        self.PIN_LOCKOUT_MINUTES = 30
    
    def set_pin(self, customer_id: int, current_password: str, pin: str) -> dict:
        """Set up a new PIN for the user"""
        customer = self.customer_repo.get_by_id(customer_id)
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Verify current password
        if not verify_password(current_password, customer.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid password"
            )
        
        # Check if PIN is already set
        if customer.pin_enabled:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="PIN already set. Use change PIN or disable PIN"
            )
        
        # Hash PIN
        hashed_pin = get_password_hash(pin)
        customer.hashed_pin = hashed_pin
        customer.pin_enabled = True
        customer.pin_attempts = 0
        customer.pin_locked_until = None
        self.customer_repo.update(customer)
        
        logger.info(f"PIN set for user: {customer.email}")
        return {
            "message": "PIN set successfully",
            "enabled": True
        }
    
    def verify_pin(self, customer_id: int, pin: str) -> dict:
        """Verify a user's PIN"""
        customer = self.customer_repo.get_by_id(customer_id)
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Check if PIN is enabled
        if not customer.pin_enabled:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="PIN is not enabled"
            )
        
        # Check if PIN is locked
        if customer.pin_locked_until:
            if datetime.utcnow() < customer.pin_locked_until:
                remaining = (customer.pin_locked_until - datetime.utcnow()).seconds // 60
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"PIN is locked. Try again in {remaining} minutes"
                )
            else:
                # Reset lock
                customer.pin_attempts = 0
                customer.pin_locked_until = None
                self.customer_repo.update(customer)
        
        # Verify PIN
        if verify_password(pin, customer.hashed_pin):
            # Reset attempts on success
            customer.pin_attempts = 0
            self.customer_repo.update(customer)
            logger.info(f"PIN verified for user: {customer.email}")
            return {"verified": True, "message": "PIN verified successfully"}
        else:
            # Increment attempts
            customer.pin_attempts += 1
            
            # Check if max attempts reached
            if customer.pin_attempts >= self.MAX_PIN_ATTEMPTS:
                customer.pin_locked_until = datetime.utcnow() + timedelta(minutes=self.PIN_LOCKOUT_MINUTES)
                self.customer_repo.update(customer)
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Too many failed attempts. PIN locked for {self.PIN_LOCKOUT_MINUTES} minutes"
                )
            
            self.customer_repo.update(customer)
            remaining = self.MAX_PIN_ATTEMPTS - customer.pin_attempts
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid PIN. {remaining} attempts remaining"
            )
    
    def change_pin(self, customer_id: int, current_pin: str, new_pin: str) -> dict:
        """Change a user's PIN"""
        customer = self.customer_repo.get_by_id(customer_id)
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        if not customer.pin_enabled:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="PIN is not enabled"
            )
        
        # Verify current PIN
        if not verify_password(current_pin, customer.hashed_pin):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid current PIN"
            )
        
        # Hash new PIN
        hashed_pin = get_password_hash(new_pin)
        customer.hashed_pin = hashed_pin
        customer.pin_attempts = 0
        customer.pin_locked_until = None
        self.customer_repo.update(customer)
        
        logger.info(f"PIN changed for user: {customer.email}")
        return {
            "message": "PIN changed successfully",
            "enabled": True
        }
    
    def disable_pin(self, customer_id: int, pin: str) -> dict:
        """Disable a user's PIN"""
        customer = self.customer_repo.get_by_id(customer_id)
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        if not customer.pin_enabled:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="PIN is not enabled"
            )
        
        # Verify PIN
        if not verify_password(pin, customer.hashed_pin):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid PIN"
            )
        
        # Disable PIN
        customer.hashed_pin = None
        customer.pin_enabled = False
        customer.pin_attempts = 0
        customer.pin_locked_until = None
        self.customer_repo.update(customer)
        
        logger.info(f"PIN disabled for user: {customer.email}")
        return {
            "message": "PIN disabled successfully",
            "enabled": False
        }
    
    def get_pin_status(self, customer_id: int) -> dict:
        """Get PIN status for a user"""
        customer = self.customer_repo.get_by_id(customer_id)
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        attempts_remaining = None
        locked_until = None
        
        if customer.pin_enabled:
            attempts_remaining = self.MAX_PIN_ATTEMPTS - customer.pin_attempts
            locked_until = customer.pin_locked_until
        
        return {
            "enabled": customer.pin_enabled,
            "attempts_remaining": attempts_remaining,
            "locked_until": locked_until
        }
    
    def require_pin_for_action(self, customer_id: int) -> bool:
        """Check if PIN is required for sensitive actions"""
        customer = self.customer_repo.get_by_id(customer_id)
        if not customer:
            return False
        return customer.pin_enabled
    
    def generate_temp_pin(self) -> str:
        """Generate a temporary 5-digit PIN"""
        return ''.join([str(random.randint(0, 9)) for _ in range(5)])