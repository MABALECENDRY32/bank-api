from sqlalchemy import Column, Integer, String, DateTime, Boolean, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base

class Customer(Base):
    __tablename__ = "customers"
    
    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, nullable=False)
    phone = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, nullable=True)
    address = Column(String, nullable=True)
    
    # PIN Security
    hashed_pin = Column(String, nullable=False)
    pin_enabled = Column(Boolean, default=True)
    pin_attempts = Column(Integer, default=0)
    pin_locked_until = Column(DateTime, nullable=True)
    
    # Account status
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    
    # Transaction limits
    daily_withdrawal_limit = Column(Float, default=5000.00)
    daily_transfer_limit = Column(Float, default=10000.00)
    daily_withdrawal_used = Column(Float, default=0.0)
    daily_transfer_used = Column(Float, default=0.0)
    last_reset_date = Column(DateTime, default=datetime.utcnow)
    
    # Account freezing
    is_frozen = Column(Boolean, default=False)
    freeze_reason = Column(String, nullable=True)
    frozen_at = Column(DateTime, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships - using string references
    accounts = relationship("Account", back_populates="owner", cascade="all, delete-orphan")