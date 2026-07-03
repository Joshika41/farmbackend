import database
from models import User
from auth import get_password_hash
import uuid

def update_db():
    db = database.SessionLocal()
    try:
        # Use generic hashed passwords instead of plaintext phone numbers
        default_emp_pass = get_password_hash("FarmWorker#2026")
        default_admin_pass = get_password_hash("Admin!Secure2026")
        default_owner_pass = get_password_hash("Owner!Secure2026")

        employee_usernames = [
            "david", "kalyan", "selvaraj", "savari", 
            "vishwa", "mani", "shanmugam", "raja"
        ]
        
        # 1. Update existing employees
        for username in employee_usernames:
            user = db.query(User).filter(User.username == username).first()
            if user:
                user.password = default_emp_pass
                user.role = "employee"
                print(f"Updated password for {username}")
            else:
                print(f"Warning: {username} not found in DB")
        
        # 2. Add/Update Admin (Jayanthi)
        jayanthi = db.query(User).filter(User.username == "jayanthi").first()
        if not jayanthi:
            jayanthi = User(
                id=f"emp_{uuid.uuid4().hex[:8]}",
                name="Jayanthi",
                username="jayanthi",
                password=default_admin_pass,
                role="admin",
                avatar="https://ui-avatars.com/api/?name=Jayanthi&background=random"
            )
            db.add(jayanthi)
            print("Added Jayanthi (Admin)")
        else:
            jayanthi.password = default_admin_pass
            jayanthi.role = "admin"
            print("Updated Jayanthi (Admin)")

        # 3. Add/Update Owner (Chairman)
        chairman = db.query(User).filter(User.username == "chairman").first()
        if not chairman:
            chairman = User(
                id=f"emp_{uuid.uuid4().hex[:8]}",
                name="Chairman",
                username="chairman",
                password=default_owner_pass,
                role="owner",
                avatar="https://ui-avatars.com/api/?name=Chairman&background=random"
            )
            db.add(chairman)
            print("Added Chairman (Owner)")
        else:
            chairman.password = default_owner_pass
            chairman.role = "owner"
            print("Updated Chairman (Owner)")

        db.commit()
        print("Database credentials update complete!")
        
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    update_db()
