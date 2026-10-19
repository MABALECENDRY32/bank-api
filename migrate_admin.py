"""
Database migration script to add admin and frozen columns
"""
from app.core.database import engine
from sqlalchemy import text
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def migrate():
    """Add new columns to customers table"""
    logger.info("Starting admin migration...")
    
    with engine.connect() as conn:
        # Check if is_admin column exists
        check_query = """
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'customers' 
        AND column_name = 'is_admin'
        """
        result = conn.execute(text(check_query)).fetchone()
        
        if not result:
            logger.info("Adding is_admin column...")
            conn.execute(text(
                "ALTER TABLE customers ADD COLUMN is_admin BOOLEAN DEFAULT FALSE"
            ))
        
        # Check if is_frozen column exists
        check_query = """
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'customers' 
        AND column_name = 'is_frozen'
        """
        result = conn.execute(text(check_query)).fetchone()
        
        if not result:
            logger.info("Adding is_frozen column...")
            conn.execute(text(
                "ALTER TABLE customers ADD COLUMN is_frozen BOOLEAN DEFAULT FALSE"
            ))
        
        # Check if freeze_reason column exists
        check_query = """
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'customers' 
        AND column_name = 'freeze_reason'
        """
        result = conn.execute(text(check_query)).fetchone()
        
        if not result:
            logger.info("Adding freeze_reason column...")
            conn.execute(text(
                "ALTER TABLE customers ADD COLUMN freeze_reason VARCHAR"
            ))
        
        # Check if frozen_at column exists
        check_query = """
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'customers' 
        AND column_name = 'frozen_at'
        """
        result = conn.execute(text(check_query)).fetchone()
        
        if not result:
            logger.info("Adding frozen_at column...")
            conn.execute(text(
                "ALTER TABLE customers ADD COLUMN frozen_at TIMESTAMP"
            ))
        
        conn.commit()
        logger.info("✅ Migration completed successfully!")

if __name__ == "__main__":
    migrate()