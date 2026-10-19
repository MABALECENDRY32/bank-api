from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.repositories.account_repo import AccountRepository
from app.repositories.transaction_repo import TransactionRepository
from app.repositories.customer_repo import CustomerRepository
from app.schemas.transaction import TransferRequest, TransactionResponse
from app.models.transaction import TransactionType
from app.services.email_service import EmailService
from fastapi import HTTPException, status
from typing import List

class TransactionService:
    def __init__(self, db: Session):
        self.db = db
        self.account_repo = AccountRepository(db)
        self.transaction_repo = TransactionRepository(db)
        self.customer_repo = CustomerRepository(db)
        self.email_service = EmailService()
    
    def transfer(self, transfer_data: TransferRequest) -> dict:
        # Get source account
        from_account = self.account_repo.get_by_account_number(transfer_data.from_account_number)
        if not from_account:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Source account not found"
            )
        
        sender = self.customer_repo.get_by_id(from_account.customer_id)
        if sender and sender.is_frozen:
            raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Your account is frozen. Reason: {sender.freeze_reason or 'No reason provided'}"
        )

        
        # Get destination account
        to_account = self.account_repo.get_by_account_number(transfer_data.to_account_number)
        if not to_account:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Destination account not found"
            )

        receiver = self.customer_repo.get_by_id(to_account.customer_id)
        if receiver and receiver.is_frozen:
            raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Destination account is frozen. Cannot transfer."
        )


        # Get sender customer
        sender = self.customer_repo.get_by_id(from_account.customer_id)
        if not sender:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Sender not found"
            )
        
        # Reset daily limits if new day
        self.customer_repo.reset_daily_limits(sender)
        
        # Check if sender has enough daily transfer limit
        remaining_limit = sender.daily_transfer_limit - sender.daily_transfer_used
        if transfer_data.amount > remaining_limit:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Daily transfer limit exceeded. Remaining limit: ${remaining_limit:.2f}"
            )
        
        # Check if same account
        if from_account.id == to_account.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot transfer to the same account"
            )
        
        # Check sufficient balance
        if from_account.balance < transfer_data.amount:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Insufficient funds"
            )
        
        try:
            # Perform transfer with transaction
            # Debit from account
            from_account.balance -= transfer_data.amount
            self.account_repo.update(from_account)
            
            # Credit to account
            to_account.balance += transfer_data.amount
            self.account_repo.update(to_account)
            
            # Update daily transfer usage
            sender.daily_transfer_used += transfer_data.amount
            self.customer_repo.update(sender)
            
            # Create transaction records
            debit_transaction = {
                "amount": transfer_data.amount,
                "transaction_type": TransactionType.TRANSFER,
                "description": f"Transfer to {transfer_data.to_account_number} - {transfer_data.description or 'No description'}",
                "account_id": from_account.id
            }
            self.transaction_repo.create(debit_transaction)
            
            credit_transaction = {
                "amount": transfer_data.amount,
                "transaction_type": TransactionType.TRANSFER,
                "description": f"Transfer from {transfer_data.from_account_number} - {transfer_data.description or 'No description'}",
                "account_id": to_account.id
            }
            self.transaction_repo.create(credit_transaction)
            
            # Send email notification to sender
            if sender:
                self.email_service.send_transfer_email(
                    sender.email,
                    sender.full_name,
                    transfer_data.amount,
                    transfer_data.from_account_number,
                    transfer_data.to_account_number,
                    from_account.balance
                )
            
            # Send email notification to receiver
            receiver = self.customer_repo.get_by_id(to_account.customer_id)
            if receiver and receiver.id != sender.id:
                self.email_service.send_email(
                    to_email=receiver.email,
                    subject=f"Transfer Received - ${transfer_data.amount:.2f}",
                    body=f"""
Dear {receiver.full_name},

You have received a transfer of ${transfer_data.amount:.2f} from account {transfer_data.from_account_number}.

Your new balance: ${to_account.balance:.2f}

Best regards,
The Medium Bank Team
"""
                )
            
            return {
                "message": f"Successfully transferred ${transfer_data.amount:.2f}",
                "from_account": transfer_data.from_account_number,
                "to_account": transfer_data.to_account_number,
                "amount": transfer_data.amount,
                "daily_limit_used": sender.daily_transfer_used,
                "daily_limit_remaining": sender.daily_transfer_limit - sender.daily_transfer_used
            }
            
        except SQLAlchemyError as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Transfer failed: {str(e)}"
            )
    
    def get_transaction_history(self, account_number: str, limit: int = 100) -> List[TransactionResponse]:
        account = self.account_repo.get_by_account_number(account_number)
        if not account:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Account not found"
            )
        
        transactions = self.transaction_repo.get_by_account_id(account.id, limit)
        return [TransactionResponse.model_validate(t) for t in transactions]