from app.core.database import SessionLocal
from app.core.security import hash_password
from app.models.user import User

def seed_test_user():
    db = SessionLocal()
    try:
        existing = db.query(User).filter(User.username == "demo_officer").first()
        if existing:
            print("User 'demo_officer' already exists. Skipping.")
            return

        test_user = User(
            username="demo_officer",
            password_hash=hash_password("ChangeMe123!"),
            mfa_enabled=False,
            status="ACTIVE",
        )
        db.add(test_user)
        db.commit()
        print("Created user 'demo_officer' with password 'ChangeMe123!'")
    finally:
        db.close()

if __name__ == "__main__":
    seed_test_user()