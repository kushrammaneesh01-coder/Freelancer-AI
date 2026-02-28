<<<<<<< HEAD
﻿"""
SQLAlchemy database models
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


class User(Base):
    """User model for authentication"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    proposals = relationship("Proposal", back_populates="user")


class Job(Base):
    """Job model for scraped freelance jobs"""
    __tablename__ = "jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=False)
    source = Column(String(100), nullable=False)  # remoteok, weworkremotely, adzuna
    source_url = Column(String(1000), nullable=True)
    company = Column(String(255), nullable=True)
    location = Column(String(255), nullable=True)
    job_type = Column(String(100), nullable=True)  # full-time, contract, etc.
    tags = Column(Text, nullable=True)  # comma-separated tags
    posted_date = Column(DateTime, nullable=True)
    scraped_at = Column(DateTime, default=datetime.utcnow)
    is_relevant = Column(Boolean, default=False)  # filtered by filter_agent
    relevance_score = Column(Float, nullable=True)
    
    # Relationships
    proposals = relationship("Proposal", back_populates="job")


class Proposal(Base):
    """Proposal model for generated proposals"""
    __tablename__ = "proposals"
    
    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    content = Column(Text, nullable=False)
    suggested_price = Column(Float, nullable=True)
    pricing_rationale = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_submitted = Column(Boolean, default=False)
    submitted_at = Column(DateTime, nullable=True)
    
    # Relationships
    job = relationship("Job", back_populates="proposals")
    user = relationship("User", back_populates="proposals")
=======
from sqlalchemy import Column, Integer, String, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    plan = Column(String, default="free")

class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True)
    platform = Column(String)
    title = Column(String)
    score = Column(Integer)
    proposal = Column(Text)
    approved = Column(Boolean, default=False)
>>>>>>> 65e52cf1c6d95a55f86841050ddc5f9f1b34c086
