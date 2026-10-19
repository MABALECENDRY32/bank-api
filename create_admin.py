"""
Create the first admin user
"""
from app.core.database import get_db
from app.services.admin_service import AdminService

def create_admin():
    print("Creating admin user...")
    
    db = next(get_db())
    admin_service = AdminService(db)
    
    try:
        admin = admin_service.create_admin_user(
            full_name="Admin User",
            email="admin@bank.com",
            phone="+1234567890",
            password="Admin123!"
        )
        print("✅ Admin user created successfully!")
        print(f"Email: {admin.email}")
        print(f"Password: Admin123!")
        print("\n⚠️  Please change the password after first login!")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    create_admin()