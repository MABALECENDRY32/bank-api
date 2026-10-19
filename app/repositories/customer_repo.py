from sqlalchemy.orm import Session
from app.models.customer import Customer
from typing import Optional, List

class CustomerRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, customer_data: dict) -> Customer:
        customer = Customer(**customer_data)
        self.db.add(customer)
        self.db.commit()
        self.db.refresh(customer)
        return customer
    
    def get_by_id(self, customer_id: int) -> Optional[Customer]:
        return self.db.query(Customer).filter(Customer.id == customer_id).first()
    
    def get_by_email(self, email: str) -> Optional[Customer]:
        return self.db.query(Customer).filter(Customer.email == email).first()
    
    def get_by_phone(self, phone: str) -> Optional[Customer]:
        return self.db.query(Customer).filter(Customer.phone == phone).first()
    
    def exists_by_email(self, email: str) -> bool:
        return self.db.query(Customer).filter(Customer.email == email).first() is not None
    
    def exists_by_phone(self, phone: str) -> bool:
        return self.db.query(Customer).filter(Customer.phone == phone).first() is not None
    
    def update(self, customer: Customer) -> Customer:
        self.db.commit()
        self.db.refresh(customer)
        return customer
    
    def get_all(self, skip: int = 0, limit: int = 100) -> List[Customer]:
        """Get all customers with pagination"""
        return self.db.query(Customer).offset(skip).limit(limit).all()