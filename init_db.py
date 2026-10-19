from app.core.database import engine, Base
from app.models import customer, account, transaction
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_db():
    logger.info("🗄️  Dropping and recreating database tables...")
    try:
        # Drop all tables
        Base.metadata.drop_all(bind=engine)
        logger.info("✅ Tables dropped successfully!")
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Tables created successfully!")
        logger.info("📋 Tables created:")
        logger.info("   - customers (with new limit columns)")
        logger.info("   - accounts")
        logger.info("   - transactions")
    except Exception as e:
        logger.error(f"❌ Error: {e}")

if __name__ == "__main__":
    init_db()