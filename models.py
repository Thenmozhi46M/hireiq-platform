from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from datetime import datetime
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, default="candidate")  # candidate, recruiter, admin
    created_at = Column(DateTime, default=datetime.utcnow)

class JobPosting(Base):
    __tablename__ = "job_postings"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    description = Column(Text, nullable=False)
    company = Column(String, nullable=False)
    location = Column(String, default="Remote")
    created_at = Column(DateTime, default=datetime.utcnow)

class Application(Base):
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("job_postings.id"), nullable=False)
    candidate_name = Column(String, nullable=False)
    candidate_email = Column(String, nullable=False)
    resume_text = Column(Text, nullable=True)
    status = Column(String, default="Pending")  # Pending, Reviewed, Shortlisted
    created_at = Column(DateTime, default=datetime.utcnow)