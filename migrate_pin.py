"""
Database migration script for PIN security
"""
from app.core.database import engine
from sqlalchemy import text
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def migrate():
    logger.info("Starting PIN migration...")
    
    with engine.connect() as conn:
        # Add hashed_pin column
        check_query = """
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'customers' 
        AND column_name = 'hashed_pin'
        """
        result = conn.execute(text(check_query)).fetchone()
        
        if not result:
            logger.info("Adding hashed_pin column...")
            conn.execute(text(
                "ALTER TABLE customers ADD COLUMN hashed_pin VARCHAR"
            ))
        
        # Add pin_enabled column
        check_query = """
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'customers' 
        AND column_name = 'pin_enabled'
        """
        result = conn.execute(text(check_query)).fetchone()
        
        if not result:
            logger.info("Adding pin_enabled column...")
            conn.execute(text(
                "ALTER TABLE customers ADD COLUMN pin_enabled BOOLEAN DEFAULT FALSE"
            ))
        
        # Add pin_attempts column
        check_query = """
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'customers' 
        AND column_name = 'pin_attempts'
        """
        result = conn.execute(text(check_query)).fetchone()
        
        if not result:
            logger.info("Adding pin_attempts column...")
            conn.execute(text(
                "ALTER TABLE customers ADD COLUMN pin_attempts INTEGER DEFAULT 0"
            ))
        
        # Add pin_locked_until column
        check_query = """
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'customers' 
        AND column_name = 'pin_locked_until'
        """
        result = conn.execute(text(check_query)).fetchone()
        
        if not result:
            logger.info("Adding pin_locked_until column...")
            conn.execute(text(
                "ALTER TABLE customers ADD COLUMN pin_locked_until TIMESTAMP"
            ))
        
        conn.commit()
        logger.info("✅ PIN migration completed successfully!")

if __name__ == "__main__":
    migrate()