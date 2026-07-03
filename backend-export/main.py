from fastapi import FastAPI, Depends, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Dict, Any
from pydantic import BaseModel

import database
from models import Base, User, Task

app = FastAPI(title="Farm Scheduler API - Production")

origins = [
    "https://farm-work-scheduler.vercel.app",
    "http://localhost:3000",
    "http://localhost:5173",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:8081",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class LoginRequest(BaseModel):
    username: str
    password: str

@app.get("/")
def read_root():
    return {"message": "Welcome to Farm Scheduler API", "status": "active"}

@app.post("/login")
def login(request: LoginRequest, db: Session = Depends(database.get_db)):
    """
    Production-grade login endpoint. Verifies credentials against the database.
    """
    user = db.query(User).filter(User.username == request.username).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    if user.password != request.password:
        raise HTTPException(status_code=401, detail="Invalid password")
        
    return {
        "success": True,
        "message": "Login successful",
        "user": {
            "id": user.id,
            "username": user.username,
            "name": user.name,
            "role": user.role,
            "avatar": user.avatar
        }
    }

@app.get("/tasks")
def get_all_tasks(username: str = None, db: Session = Depends(database.get_db)):
    """
    Fetches tasks from the optimized tasks table.
    Filters by assigned user if username is provided.
    """
    try:
        query = db.query(Task)
        
        if username:
            user = db.query(User).filter(User.username == username).first()
            if user:
                query = query.filter(Task.assigned_to == user.id)
            else:
                return [] # User not found, return empty tasks
                
        tasks = query.all()
        
        # Format for the frontend expectations
        return [
            {
                "id": task.id,
                "title": task.title,
                "category": task.category,
                "subcategory": task.subcategory,
                "status": task.status,
                "assignedTo": task.assignee.name if task.assignee else "Unassigned",
                "priority": task.priority
            }
            for task in tasks
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/tasks/{task_id}/toggle")
def toggle_task(task_id: str, payload: dict = Body(...), db: Session = Depends(database.get_db)):
    """
    Toggles the task status in the tasks table.
    """
    try:
        task = db.query(Task).filter(Task.id == task_id).first()
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
            
        new_status = payload.get("status")
        if new_status not in ["completed", "pending"]:
            raise HTTPException(status_code=400, detail="Invalid status")
            
        task.status = new_status
        db.commit()
        
        return {"success": True, "message": f"Task toggled to {new_status}"}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
