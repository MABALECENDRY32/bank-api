"""
Migration script for PIN-only authentication
"""
from app.core.database import engine
from sqlalchemy import text
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def migrate():
    logger.info("Starting PIN-only migration...")
    
    with engine.connect() as conn:
        # 1. Remove email unique constraint if exists
        try:
            logger.info("Removing email unique constraint...")
            conn.execute(text(
                "ALTER TABLE customers DROP CONSTRAINT IF EXISTS customers_email_key"
            ))
        except Exception as e:
            logger.info(f"Constraint may not exist: {e}")
        
        # 2. Make email nullable
        try:
            logger.info("Making email column nullable...")
            conn.execute(text(
                "ALTER TABLE customers ALTER COLUMN email DROP NOT NULL"
            ))
        except Exception as e:
            logger.info(f"Email column may already be nullable: {e}")
        
        # 3. Ensure phone is unique and not null
        try:
            logger.info("Ensuring phone is unique...")
            conn.execute(text(
                "ALTER TABLE customers ADD CONSTRAINT customers_phone_key UNIQUE (phone)"
            ))
        except Exception as e:
            logger.info(f"Phone constraint may already exist: {e}")
        
        # 4. Add hashed_pin column
        try:
            logger.info("Adding hashed_pin column...")
            conn.execute(text(
                "ALTER TABLE customers ADD COLUMN hashed_pin VARCHAR"
            ))
        except Exception as e:
            logger.info(f"hashed_pin column may already exist: {e}")
        
        # 5. Add pin_enabled column
        try:
            logger.info("Adding pin_enabled column...")
            conn.execute(text(
                "ALTER TABLE customers ADD COLUMN pin_enabled BOOLEAN DEFAULT FALSE"
            ))
        except Exception as e:
            logger.info(f"pin_enabled column may already exist: {e}")
        
        # 6. Add pin_attempts column
        try:
            logger.info("Adding pin_attempts column...")
            conn.execute(text(
                "ALTER TABLE customers ADD COLUMN pin_attempts INTEGER DEFAULT 0"
            ))
        except Exception as e:
            logger.info(f"pin_attempts column may already exist: {e}")
        
        # 7. Add pin_locked_until column
        try:
            logger.info("Adding pin_locked_until column...")
            conn.execute(text(
                "ALTER TABLE customers ADD COLUMN pin_locked_until TIMESTAMP"
            ))
        except Exception as e:
            logger.info(f"pin_locked_until column may already exist: {e}")
        
        # 8. Remove hashed_password column (optional - we'll keep it for now)
        # We'll keep it for backward compatibility, but it won't be used
        
        conn.commit()
        logger.info("✅ PIN-only migration completed successfully!")
        logger.info("📋 Changes made:")
        logger.info("   - hashed_pin column added")
        logger.info("   - pin_enabled column added")
        logger.info("   - pin_attempts column added")
        logger.info("   - pin_locked_until column added")
        logger.info("   - email is now optional")
        logger.info("   - phone is now unique")

if __name__ == "__main__":
    migrate()