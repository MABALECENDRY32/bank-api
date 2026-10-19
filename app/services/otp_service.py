import random
import time
from datetime import datetime, timedelta
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class OTPService:
    """Service for generating and validating OTPs"""
    
    def __init__(self):
        self.otp_store = {}  # phone -> (otp, expires_at)
        self.OTP_EXPIRY_SECONDS = 600  # 10 minutes
    
    def generate_otp(self, phone: str) -> str:
        """Generate a 6-digit OTP"""
        otp = ''.join([str(random.randint(0, 9)) for _ in range(6)])
        expires_at = datetime.utcnow() + timedelta(seconds=self.OTP_EXPIRY_SECONDS)
        self.otp_store[phone] = (otp, expires_at)
        logger.info(f"OTP generated for {phone}")
        return otp
    
    def verify_otp(self, phone: str, otp: str) -> bool:
        """Verify OTP"""
        if phone not in self.otp_store:
            logger.warning(f"No OTP found for {phone}")
            return False
        
        stored_otp, expires_at = self.otp_store[phone]
        
        # Check if expired
        if datetime.utcnow() > expires_at:
            logger.warning(f"OTP expired for {phone}")
            del self.otp_store[phone]
            return False
        
        # Check if valid
        if stored_otp != otp:
            logger.warning(f"Invalid OTP for {phone}")
            return False
        
        # Clear OTP after successful verification
        del self.otp_store[phone]
        logger.info(f"OTP verified for {phone}")
        return True
    
    def clear_otp(self, phone: str):
        """Clear OTP for a phone number"""
        if phone in self.otp_store:
            del self.otp_store[phone]