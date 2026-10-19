import pyotp
import qrcode
import base64
from io import BytesIO
from sqlalchemy.orm import Session
from app.repositories.customer_repo import CustomerRepository
from app.core.security import verify_password
from fastapi import HTTPException, status
import secrets
import logging

logger = logging.getLogger(__name__)

class TwoFAService:
    def __init__(self, db: Session):
        self.db = db
        self.customer_repo = CustomerRepository(db)
    
    def generate_backup_codes(self, count: int = 10) -> list[str]:
        """Generate backup codes for account recovery"""
        codes = []
        for _ in range(count):
            # Generate 8-character alphanumeric codes
            code = secrets.token_hex(4).upper()
            codes.append(code)
        return codes
    
    def setup_2fa(self, customer_id: int) -> dict:
        """Setup 2FA for a user"""
        customer = self.customer_repo.get_by_id(customer_id)
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        if customer.twofa_enabled:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="2FA is already enabled"
            )
        
        # Generate secret
        secret = pyotp.random_base32()
        customer.twofa_secret = secret
        self.customer_repo.update(customer)
        
        # Generate QR code
        totp = pyotp.TOTP(secret)
        provisioning_uri = totp.provisioning_uri(
            name=customer.email,
            issuer_name="Medium Bank"
        )
        
        # Create QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(provisioning_uri)
        qr.make(fit=True)
        
        # Convert QR to base64
        img = qr.make_image(fill_color="black", back_color="white")
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        qr_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
        
        # Generate backup codes
        backup_codes = self.generate_backup_codes()
        
        # In a real app, you would store encrypted backup codes
        # For simplicity, we're returning them and the user must save them
        
        return {
            "secret": secret,
            "qr_code": f"data:image/png;base64,{qr_base64}",
            "backup_codes": backup_codes
        }
    
    def enable_2fa(self, customer_id: int, secret: str, totp_code: str) -> dict:
        """Enable 2FA after verification"""
        customer = self.customer_repo.get_by_id(customer_id)
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        if customer.twofa_enabled:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="2FA is already enabled"
            )
        
        # Verify TOTP code
        totp = pyotp.TOTP(secret)
        if not totp.verify(totp_code):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid TOTP code"
            )
        
        # Enable 2FA
        customer.twofa_enabled = True
        customer.twofa_secret = secret
        self.customer_repo.update(customer)
        
        return {
            "message": "2FA enabled successfully",
            "enabled": True
        }
    
    def verify_totp(self, customer_id: int, totp_code: str) -> bool:
        """Verify TOTP code"""
        customer = self.customer_repo.get_by_id(customer_id)
        if not customer:
            return False
        
        if not customer.twofa_enabled or not customer.twofa_secret:
            return False
        
        totp = pyotp.TOTP(customer.twofa_secret)
        return totp.verify(totp_code)
    
    def verify_login_with_2fa(self, email: str, password: str, totp_code: str) -> dict:
        """Verify login with 2FA"""
        customer = self.customer_repo.get_by_email(email)
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
        
        # Verify password
        if not verify_password(password, customer.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
        
        # If 2FA is enabled, verify TOTP
        if customer.twofa_enabled:
            if not self.verify_totp(customer.id, totp_code):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid TOTP code"
                )
        
        return {
            "customer": customer,
            "twofa_required": customer.twofa_enabled
        }
    
    def disable_2fa(self, customer_id: int, totp_code: str) -> dict:
        """Disable 2FA"""
        customer = self.customer_repo.get_by_id(customer_id)
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        if not customer.twofa_enabled:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="2FA is not enabled"
            )
        
        # Verify TOTP
        if not self.verify_totp(customer_id, totp_code):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid TOTP code"
            )
        
        # Disable 2FA
        customer.twofa_enabled = False
        customer.twofa_secret = None
        self.customer_repo.update(customer)
        
        return {
            "message": "2FA disabled successfully",
            "enabled": False
        }
    
    def get_2fa_status(self, customer_id: int) -> dict:
        """Get 2FA status"""
        customer = self.customer_repo.get_by_id(customer_id)
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return {
            "enabled": customer.twofa_enabled,
            "secret": customer.twofa_secret if customer.twofa_enabled else None
        }