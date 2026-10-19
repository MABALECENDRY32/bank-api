import logging
from datetime import datetime
from twilio.rest import Client
from app.core.config import settings

logger = logging.getLogger(__name__)

class SMSService:
    def __init__(self):
        self.client = None
        self.enabled = settings.SMS_ENABLED
        
        if self.enabled and settings.TWILIO_ACCOUNT_SID and settings.TWILIO_AUTH_TOKEN:
            try:
                self.client = Client(
                    settings.TWILIO_ACCOUNT_SID,
                    settings.TWILIO_AUTH_TOKEN
                )
                self.from_number = settings.TWILIO_PHONE_NUMBER
                logger.info("SMS service initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize SMS service: {e}")
                self.enabled = False
        else:
            if not settings.SMS_ENABLED:
                logger.info("SMS service is disabled in settings")
            else:
                logger.warning("SMS service is not configured properly. Check TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, and TWILIO_PHONE_NUMBER")
    
    def send_sms(self, to_number: str, message: str) -> bool:
        """Send an SMS message"""
        if not self.enabled or not self.client:
            logger.warning("SMS service is disabled or not initialized. Message not sent.")
            return False
        
        try:
            # Clean phone number
            to_number = to_number.strip()
            if not to_number.startswith('+'):
                to_number = f'+{to_number}'
            
            message = self.client.messages.create(
                body=message,
                from_=self.from_number,
                to=to_number
            )
            
            logger.info(f"SMS sent to {to_number}: {message.sid}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send SMS: {e}")
            return False
    
    def send_login_otp(self, to_number: str, otp: str) -> bool:
        """Send login OTP via SMS"""
        message = f"""
🔐 BLUE Bank Security Alert

Your login OTP is: {otp}

This code will expire in 10 minutes.
Do not share this code with anyone.

If you didn't request this, ignore this message.
"""
        return self.send_sms(to_number, message)
    
    def send_transaction_alert(self, to_number: str, amount: float, transaction_type: str, account_number: str) -> bool:
        """Send transaction alert via SMS"""
        message = f"""
🏦 BLUE Bank Transaction Alert

{transaction_type}: ${amount:.2f}
Account: {account_number}
Time: {datetime.now().strftime('%Y-%m-%d %H:%M')}

If you didn't make this transaction, contact us immediately.
"""
        return self.send_sms(to_number, message)
    
    def send_pin_setup_alert(self, to_number: str) -> bool:
        """Send PIN setup confirmation"""
        message = f"""
🔐 BLUE Bank Security Alert

Your security PIN has been successfully set up.
If you didn't do this, contact us immediately.
"""
        return self.send_sms(to_number, message)
    
    def send_pin_changed_alert(self, to_number: str) -> bool:
        """Send PIN change confirmation"""
        message = f"""
🔐 BLUE Bank Security Alert

Your security PIN has been changed.
If you didn't do this, contact us immediately.
"""
        return self.send_sms(to_number, message)