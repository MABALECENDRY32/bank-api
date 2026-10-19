from sqlalchemy.orm import Session
from app.models.account import Account
from typing import Optional, List

class AccountRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, account_data: dict) -> Account:
        account = Account(**account_data)
        self.db.add(account)
        self.db.commit()
        self.db.refresh(account)
        return account
    
    def get_by_id(self, account_id: int) -> Optional[Account]:
        return self.db.query(Account).filter(Account.id == account_id).first()
    
    def get_by_account_number(self, account_number: str) -> Optional[Account]:
        return self.db.query(Account).filter(Account.account_number == account_number).first()
    
    def get_by_customer_id(self, customer_id: int) -> List[Account]:
        return self.db.query(Account).filter(Account.customer_id == customer_id).all()
    
    def exists_by_account_number(self, account_number: str) -> bool:
        return self.db.query(Account).filter(Account.account_number == account_number).first() is not None
    
    def update(self, account: Account) -> Account:
        self.db.commit()
        self.db.refresh(account)
        return account