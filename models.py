from sqlalchemy import Column, String, ForeignKey, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(String(50), primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    password = Column(String(100), nullable=False)
    name = Column(String(100))
    role = Column(String(20), default="employee")
    avatar = Column(String(255))
    
    tasks = relationship("Task", back_populates="assignee")
    instructions_sent = relationship("VoiceInstruction", foreign_keys="[VoiceInstruction.sender_id]", back_populates="sender")
    instructions_received = relationship("VoiceInstruction", foreign_keys="[VoiceInstruction.recipient_id]", back_populates="recipient")

class Task(Base):
    __tablename__ = "tasks"
    
    id = Column(String(50), primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    category = Column(String(50), nullable=False)
    subcategory = Column(String(50), default="Daily Routine")
    status = Column(String(20), default="pending")
    assigned_to = Column(String(50), ForeignKey("users.id"))
    priority = Column(String(20), default="medium")
    
    assignee = relationship("User", back_populates="tasks")
    voice_messages = relationship("VoiceMessage", back_populates="task", cascade="all, delete-orphan")

class VoiceMessage(Base):
    __tablename__ = "voice_messages"
    
    id = Column(String(50), primary_key=True, index=True)
    task_id = Column(String(50), ForeignKey("tasks.id"), nullable=False)
    user_id = Column(String(50), ForeignKey("users.id"), nullable=False)
    file_path = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    task = relationship("Task", back_populates="voice_messages")
    user = relationship("User")

class VoiceInstruction(Base):
    __tablename__ = "voice_instructions"
    
    id = Column(String(50), primary_key=True, index=True)
    sender_id = Column(String(50), ForeignKey("users.id"), nullable=False)
    recipient_id = Column(String(50), ForeignKey("users.id"), nullable=False)
    file_path = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    sender = relationship("User", foreign_keys=[sender_id], back_populates="instructions_sent")
    recipient = relationship("User", foreign_keys=[recipient_id], back_populates="instructions_received")
