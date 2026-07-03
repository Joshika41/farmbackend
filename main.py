from fastapi import FastAPI, Depends, HTTPException, Body, UploadFile, File, Form
from fastapi.staticfiles import StaticFiles
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Dict, Any
from pydantic import BaseModel
import os
import logging

from auth import get_current_user_token, verify_password, create_access_token

import database
from models import Base, User, Task, VoiceMessage, VoiceInstruction
import uuid
import shutil

app = FastAPI(title="Farm Scheduler API - Production")

cors_env = os.getenv("CORS_ORIGINS")
if cors_env:
    origins = [origin.strip() for origin in cors_env.split(",")]
else:
    # Safe default if env not set
    origins = [
        "https://farm-work-scheduler.vercel.app"
    ]

# Ensure uploads directory exists
os.makedirs("uploads/voice_messages", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

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
    from fastapi.responses import JSONResponse
    
    # Lowercase the username to ensure case-insensitive matching
    search_username = request.username.strip().lower()
    user = db.query(User).filter(User.username == search_username).first()
    
    if not user:
        return JSONResponse(status_code=404, content={"success": False, "message": "User not found. Please check your username."})
        
    if not verify_password(request.password, user.password):
        return JSONResponse(status_code=401, content={"success": False, "message": "Invalid password. Please try again."})

    # Generate JWT
    access_token = create_access_token(data={"sub": user.username})
        
    return {
        "success": True,
        "message": "Login successful",
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "username": user.username,
            "name": user.name,
            "role": user.role,
            "avatar": user.avatar,
            "assigned_checklists": [] # Employee checklist array
        }
    }

@app.post("/token")
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db)):
    """
    OAuth2 compatible token login, required for Swagger UI's Authorize button.
    """
    search_username = form_data.username.strip().lower()
    user = db.query(User).filter(User.username == search_username).first()
    
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users")
def get_users(db: Session = Depends(database.get_db), current_username: str = Depends(get_current_user_token)):
    users = db.query(User).all()
    return [
        {
            "id": u.id,
            "username": u.username,
            "name": u.name,
            "role": u.role,
            "avatar": u.avatar
        }
        for u in users
    ]

@app.get("/tasks")
def get_all_tasks(username: str = None, db: Session = Depends(database.get_db), current_username: str = Depends(get_current_user_token)):
    """
    Fetches tasks from the optimized tasks table.
    Filters by assigned user if username is provided.
    Requires authentication.
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
        logging.error(f"Error fetching tasks: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/tasks/{task_id}/toggle")
def toggle_task(task_id: str, payload: dict = Body(...), db: Session = Depends(database.get_db), current_username: str = Depends(get_current_user_token)):
    """
    Toggles the task status in the tasks table.
    Requires authentication.
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
        logging.error(f"Error toggling task {task_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/tasks/{task_id}/voice")
def upload_voice_message(task_id: str, file: UploadFile = File(...), db: Session = Depends(database.get_db), current_username: str = Depends(get_current_user_token)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
        
    user = db.query(User).filter(User.username == current_username).first()
    
    file_id = str(uuid.uuid4())
    file_ext = file.filename.split('.')[-1] if '.' in file.filename else 'm4a'
    filename = f"task_{task_id}_{user.id}_{file_id}.{file_ext}"
    file_path = f"uploads/voice_messages/{filename}"
    
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        voice_msg = VoiceMessage(
            id=file_id,
            task_id=task_id,
            user_id=user.id,
            file_path=f"/uploads/voice_messages/{filename}"
        )
        db.add(voice_msg)
        db.commit()
        
        return {"success": True, "message": "Voice message uploaded", "voice_id": file_id}
    except Exception as e:
        db.rollback()
        logging.error(f"Error uploading voice message: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/tasks/{task_id}/voice")
def get_voice_messages(task_id: str, db: Session = Depends(database.get_db), current_username: str = Depends(get_current_user_token)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
        
    messages = db.query(VoiceMessage).filter(VoiceMessage.task_id == task_id).order_by(VoiceMessage.created_at.desc()).all()
    
    return [
        {
            "id": msg.id,
            "user": msg.user.name,
            "file_url": msg.file_path,
            "created_at": msg.created_at
        }
        for msg in messages
    ]

@app.post("/instructions/voice")
def upload_voice_instruction(recipient_username: str = Form(...), file: UploadFile = File(...), db: Session = Depends(database.get_db), current_username: str = Depends(get_current_user_token)):
    sender = db.query(User).filter(User.username == current_username).first()
    recipient = db.query(User).filter(User.username == recipient_username).first()
    if not recipient:
        raise HTTPException(status_code=404, detail="Recipient not found")
        
    if sender.role not in ["manager", "admin", "owner"]:
        # Employees can only send to managers
        if recipient.role not in ["manager", "admin", "owner"]:
            raise HTTPException(status_code=403, detail="Employees can only send messages to management")
        
    file_id = str(uuid.uuid4())
    file_ext = file.filename.split('.')[-1] if '.' in file.filename else 'm4a'
    filename = f"instruction_{sender.id}_to_{recipient.id}_{file_id}.{file_ext}"
    file_path = f"uploads/voice_messages/{filename}"
    
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        instruction = VoiceInstruction(
            id=file_id,
            sender_id=sender.id,
            recipient_id=recipient.id,
            file_path=f"/uploads/voice_messages/{filename}"
        )
        db.add(instruction)
        db.commit()
        
        return {"success": True, "message": "Instruction uploaded", "instruction_id": file_id}
    except Exception as e:
        db.rollback()
        logging.error(f"Error uploading voice instruction: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/instructions/voice")
def get_voice_instructions(db: Session = Depends(database.get_db), current_username: str = Depends(get_current_user_token)):
    user = db.query(User).filter(User.username == current_username).first()
    
    if user.role in ["manager", "admin", "owner"]:
        # Manager/Owner sees instructions they sent
        instructions = db.query(VoiceInstruction).filter(VoiceInstruction.sender_id == user.id).order_by(VoiceInstruction.created_at.desc()).all()
    else:
        # Employee sees instructions sent to them
        instructions = db.query(VoiceInstruction).filter(VoiceInstruction.recipient_id == user.id).order_by(VoiceInstruction.created_at.desc()).all()
        
    return [
        {
            "id": inst.id,
            "sender": inst.sender.name,
            "recipient": inst.recipient.name,
            "file_url": inst.file_path,
            "created_at": inst.created_at
        }
        for inst in instructions
    ]
