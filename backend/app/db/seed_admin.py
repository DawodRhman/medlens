from sql_models import SessionLocal, create_user, get_user_by_username
from app.utils.jwt import get_password_hash

def seed_admin():
    db = SessionLocal()
    if not get_user_by_username(db, "admin"):
        create_user(db, "admin", get_password_hash("admin"), role="admin")
        print("Admin user created: admin/admin")
    else:
        print("Admin user already exists.")
    db.close()

if __name__ == "__main__":
    seed_admin()
