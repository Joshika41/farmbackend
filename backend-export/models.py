from sqlalchemy import Column, String, ForeignKey
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
