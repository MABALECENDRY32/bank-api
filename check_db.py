from app.core.database import engine
from sqlalchemy import text

def check_columns():
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'customers'
        """))
        
        print("📋 Columns in customers table:")
        for row in result:
            print(f"   - {row[0]} ({row[1]})")

if __name__ == "__main__":
    check_columns()