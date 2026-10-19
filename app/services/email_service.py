import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self):
        self.host = settings.SMTP_HOST
        self.port = settings.SMTP_PORT
        self.user = settings.SMTP_USER
        self.password = settings.SMTP_PASSWORD
        self.from_email = settings.EMAIL_FROM
        self.enabled = settings.EMAIL_ENABLED
    
    def send_email(self, to_email: str, subject: str, body: str, html_body: str = None):
        """Send an email"""
        if not self.enabled:
            logger.info("Email is disabled. Skipping email send.")
            return True
        
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = self.from_email
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # Attach plain text version
            msg.attach(MIMEText(body, 'plain'))
            
            # Attach HTML version if provided
            if html_body:
                msg.attach(MIMEText(html_body, 'html'))
            
            # Send email
            with smtplib.SMTP(self.host, self.port) as server:
                server.starttls()
                server.login(self.user, self.password)
                server.send_message(msg)
            
            logger.info(f"Email sent to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return False
    
    def send_welcome_email(self, to_email: str, full_name: str):
        """Send welcome email on registration"""
        subject = f"Welcome to Medium Bank, {full_name}!"
        
        body = f"""
        Dear {full_name},
        
        Welcome to Medium Bank! 🎉
        
        Your account has been successfully created. You can now:
        
        - Create checking and savings accounts
        - Deposit and withdraw money
        - Transfer funds between accounts
        - Track your transaction history
        
        To get started, visit our API documentation:
        http://localhost:8000/docs
        
        Thank you for choosing Medium Bank!
        
        Best regards,
        The Medium Bank Team
        """
        
        html_body = f"""
        <html>
        <body>
            <h2>Welcome to Medium Bank, {full_name}! 🎉</h2>
            
            <p>Your account has been successfully created. You can now:</p>
            
            <ul>
                <li>Create checking and savings accounts</li>
                <li>Deposit and withdraw money</li>
                <li>Transfer funds between accounts</li>
                <li>Track your transaction history</li>
            </ul>
            
            <p>To get started, visit our <a href="http://localhost:8000/docs">API Documentation</a></p>
            
            <p>Thank you for choosing Medium Bank!</p>
            
            <p>Best regards,<br>
            The Medium Bank Team</p>
        </body>
        </html>
        """
        
        return self.send_email(to_email, subject, body, html_body)
    
    def send_deposit_email(self, to_email: str, full_name: str, amount: float, balance: float, account_number: str):
        """Send deposit confirmation email"""
        subject = f"Deposit Confirmation - ${amount:.2f}"
        
        body = f"""
        Dear {full_name},
        
        A deposit of ${amount:.2f} has been made to your account.
        
        Account: {account_number}
        New Balance: ${balance:.2f}
        
        If you did not make this transaction, please contact us immediately.
        
        Best regards,
        The Medium Bank Team
        """
        
        html_body = f"""
        <html>
        <body>
            <h2>Deposit Confirmation</h2>
            
            <p>Dear {full_name},</p>
            
            <p>A deposit of <strong>${amount:.2f}</strong> has been made to your account.</p>
            
            <ul>
                <li><strong>Account:</strong> {account_number}</li>
                <li><strong>New Balance:</strong> ${balance:.2f}</li>
            </ul>
            
            <p>If you did not make this transaction, please contact us immediately.</p>
            
            <p>Best regards,<br>
            The Medium Bank Team</p>
        </body>
        </html>
        """
        
        return self.send_email(to_email, subject, body, html_body)
    
    def send_withdrawal_email(self, to_email: str, full_name: str, amount: float, balance: float, account_number: str):
        """Send withdrawal confirmation email"""
        subject = f"Withdrawal Confirmation - ${amount:.2f}"
        
        body = f"""
        Dear {full_name},
        
        A withdrawal of ${amount:.2f} has been made from your account.
        
        Account: {account_number}
        New Balance: ${balance:.2f}
        
        If you did not make this transaction, please contact us immediately.
        
        Best regards,
        The Medium Bank Team
        """
        
        html_body = f"""
        <html>
        <body>
            <h2>Withdrawal Confirmation</h2>
            
            <p>Dear {full_name},</p>
            
            <p>A withdrawal of <strong>${amount:.2f}</strong> has been made from your account.</p>
            
            <ul>
                <li><strong>Account:</strong> {account_number}</li>
                <li><strong>New Balance:</strong> ${balance:.2f}</li>
            </ul>
            
            <p>If you did not make this transaction, please contact us immediately.</p>
            
            <p>Best regards,<br>
            The Medium Bank Team</p>
        </body>
        </html>
        """
        
        return self.send_email(to_email, subject, body, html_body)
    
    def send_transfer_email(self, to_email: str, full_name: str, amount: float, from_account: str, to_account: str, balance: float):
        """Send transfer confirmation email"""
        subject = f"Transfer Confirmation - ${amount:.2f}"
        
        body = f"""
        Dear {full_name},
        
        A transfer of ${amount:.2f} has been made from your account.
        
        From Account: {from_account}
        To Account: {to_account}
        New Balance: ${balance:.2f}
        
        If you did not make this transaction, please contact us immediately.
        
        Best regards,
        The Medium Bank Team
        """
        
        html_body = f"""
        <html>
        <body>
            <h2>Transfer Confirmation</h2>
            
            <p>Dear {full_name},</p>
            
            <p>A transfer of <strong>${amount:.2f}</strong> has been made from your account.</p>
            
            <ul>
                <li><strong>From Account:</strong> {from_account}</li>
                <li><strong>To Account:</strong> {to_account}</li>
                <li><strong>New Balance:</strong> ${balance:.2f}</li>
            </ul>
            
            <p>If you did not make this transaction, please contact us immediately.</p>
            
            <p>Best regards,<br>
            The Medium Bank Team</p>
        </body>
        </html>
        """
        
        return self.send_email(to_email, subject, body, html_body)