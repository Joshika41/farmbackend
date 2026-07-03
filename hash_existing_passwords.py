import database
from models import User
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password):
    return pwd_context.hash(password)

def hash_passwords():
    db = database.SessionLocal()
    try:
        users = db.query(User).all()
        updated = 0
        for user in users:
            # If the password is not already a bcrypt hash (bcrypt hashes usually start with $2b$ or $2a$)
            if not user.password.startswith("$2"):
                print(f"Hashing password for user: {user.username}")
                user.password = get_password_hash(user.password)
                updated += 1
            else:
                print(f"Password for user {user.username} is already hashed.")
        
        db.commit()
        print(f"Successfully hashed {updated} passwords!")
    except Exception as e:
        print(f"Error during hashing: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    hash_passwords()
