"""
Migration script for 2FA
"""
from app.core.database import engine
from sqlalchemy import text
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def migrate():
    logger.info("Starting 2FA migration...")
    
    with engine.connect() as conn:
        # Add twofa_secret column
        check_query = """
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'customers' 
        AND column_name = 'twofa_secret'
        """
        result = conn.execute(text(check_query)).fetchone()
        
        if not result:
            logger.info("Adding twofa_secret column...")
            conn.execute(text(
                "ALTER TABLE customers ADD COLUMN twofa_secret VARCHAR"
            ))
        
        # Add twofa_enabled column
        check_query = """
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'customers' 
        AND column_name = 'twofa_enabled'
        """
        result = conn.execute(text(check_query)).fetchone()
        
        if not result:
            logger.info("Adding twofa_enabled column...")
            conn.execute(text(
                "ALTER TABLE customers ADD COLUMN twofa_enabled BOOLEAN DEFAULT FALSE"
            ))
        
        conn.commit()
        logger.info("✅ 2FA migration completed successfully!")

if __name__ == "__main__":
    migrate()