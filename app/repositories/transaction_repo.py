from sqlalchemy.orm import Session
from app.models.transaction import Transaction
from typing import List, Optional

class TransactionRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, transaction_data: dict) -> Transaction:
        transaction = Transaction(**transaction_data)
        self.db.add(transaction)
        self.db.commit()
        self.db.refresh(transaction)
        return transaction
    
    def get_by_account_id(self, account_id: int, limit: int = 100) -> List[Transaction]:
        return self.db.query(Transaction)\
            .filter(Transaction.account_id == account_id)\
            .order_by(Transaction.created_at.desc())\
            .limit(limit)\
            .all()