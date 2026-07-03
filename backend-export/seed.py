import database
from models import Base, User, Task
from sqlalchemy.orm import Session
import uuid

# Create tables
Base.metadata.create_all(bind=database.engine)

# Seed data
def seed_database():
    db = database.SessionLocal()
    
    # Check if we already have users
    if db.query(User).first():
        print("Database already seeded!")
        return

    users_data = [
        {"id": "emp_david", "name": "David", "username": "david", "password": "employee123", "role": "employee", "avatar": "https://images.unsplash.com/photo-1599566150163-29194dcaad36?w=150&auto=format&fit=crop&q=80"},
        {"id": "emp_kalyan", "name": "Kalyan", "username": "kalyan", "password": "employee123", "role": "employee", "avatar": "https://images.unsplash.com/photo-1527980965255-d3b416303d12?w=150&auto=format&fit=crop&q=80"},
        {"id": "emp_selvaraj", "name": "Selvaraj", "username": "selvaraj", "password": "employee123", "role": "employee", "avatar": "https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?w=150&auto=format&fit=crop&q=80"},
        {"id": "emp_savari", "name": "Savari", "username": "savari", "password": "employee123", "role": "employee", "avatar": "https://images.unsplash.com/photo-1633332755192-727a05c4013d?w=150&auto=format&fit=crop&q=80"},
        {"id": "emp_vishwa", "name": "Vishwa", "username": "vishwa", "password": "employee123", "role": "employee", "avatar": "https://images.unsplash.com/photo-1580489944761-15a19d654956?w=150&auto=format&fit=crop&q=80"},
        {"id": "emp_mani", "name": "Mani", "username": "mani", "password": "employee123", "role": "employee", "avatar": "https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?w=150&auto=format&fit=crop&q=80"},
        {"id": "emp_shanmugam", "name": "Shanmugam", "username": "shanmugam", "password": "employee123", "role": "employee", "avatar": "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=150&auto=format&fit=crop&q=80"},
        {"id": "mgr_marcus", "name": "Marcus Brody", "username": "marcus", "password": "manager123", "role": "manager", "avatar": "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=150&auto=format&fit=crop&q=80"}
    ]

    for user_data in users_data:
        user = User(**user_data)
        db.add(user)
    
    db.commit()

    # Create some initial tasks based on assignment mapping
    # David: vehicles, birds, fish
    # Kalyan: vehicles
    # Selvaraj: vehicles
    # Savari: vehicles, calves
    # Vishwa: vehicles
    # Mani: vehicles
    # Shanmugam: birds, fish, pond

    tasks_data = [
        {"title": "Morning Poultry Feeding", "category": "birds", "assigned_to": "emp_david"},
        {"title": "Water Line Check", "category": "birds", "assigned_to": "emp_shanmugam"},
        {"title": "Tractor Refueling", "category": "vehicles", "assigned_to": "emp_kalyan"},
        {"title": "Delivery Truck Inspection", "category": "vehicles", "assigned_to": "emp_selvaraj"},
        {"title": "Pond Water Level Check", "category": "pond", "assigned_to": "emp_shanmugam"},
        {"title": "Calf Milk Replacer Feeding", "category": "calves", "assigned_to": "emp_savari"},
        {"title": "Fish Pond A-D Feeding", "category": "fish", "assigned_to": "emp_david"},
        {"title": "Check Water pH", "category": "fish", "assigned_to": "emp_shanmugam"},
        {"title": "Bike Maintenance", "category": "vehicles", "assigned_to": "emp_vishwa"},
        {"title": "Car Cleaning", "category": "vehicles", "assigned_to": "emp_mani"},
    ]

    for i, task_data in enumerate(tasks_data):
        task = Task(
            id=f"t_{uuid.uuid4().hex[:8]}",
            title=task_data["title"],
            category=task_data["category"],
            subcategory="Daily Routine",
            status="pending",
            assigned_to=task_data["assigned_to"],
            priority="medium"
        )
        db.add(task)
    
    db.commit()
    db.close()
    print("Database seeded successfully with new production schema!")

if __name__ == "__main__":
    seed_database()
