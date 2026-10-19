from pydantic import BaseModel
from typing import Optional

class TwoFASetupResponse(BaseModel):
    secret: str
    qr_code: str  # Base64 encoded QR code
    backup_codes: list[str]

class TwoFAEnableRequest(BaseModel):
    secret: str
    totp_code: str

class TwoFAVerifyRequest(BaseModel):
    email: str
    password: str
    totp_code: str

class TwoFADisableRequest(BaseModel):
    totp_code: str

class TwoFAStatusResponse(BaseModel):
    enabled: bool
    secret: Optional[str] = None