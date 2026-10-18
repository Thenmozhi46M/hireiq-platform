from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel, EmailStr
from datetime import datetime, timedelta
from jose import JWTError, jwt
import bcrypt

from .database import engine, Base, get_db
from .models import User, JobPosting, Application

# Security Configurations
SECRET_KEY = "supersecretkeychangeinproduction"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Create tables automatically
Base.metadata.create_all(bind=engine)

app = FastAPI(title="HireIQ API", version="1.0")

# Pydantic Schemas
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    role: str = "candidate"

class UserResponse(BaseModel):
    id: int
    email: str
    role: str
    created_at: str

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class JobCreate(BaseModel):
    title: str
    description: str
    company: str
    location: str = "Remote"

class JobResponse(JobCreate):
    id: int
    created_at: str

    class Config:
        from_attributes = True

class ApplicationCreate(BaseModel):
    job_id: int
    candidate_name: str
    candidate_email: str
    resume_text: str = ""

class ApplicationResponse(ApplicationCreate):
    id: int
    status: str
    created_at: str

    class Config:
        from_attributes = True

# Helper Functions for Auth using direct bcrypt
def get_password_hash(password: str):
    return bcrypt.hashpw(password[:72].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(plain_password, hashed_password):
    return bcrypt.checkpw(plain_password[:72].encode('utf-8'), hashed_password.encode('utf-8'))

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

@app.get("/")
def read_root():
    return {"message": "Welcome to HireIQ API - Auth Module Ready!"}

# --- Auth Endpoints ---
@app.post("/signup/", response_model=UserResponse)
def signup(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_pwd = get_password_hash(user.password)
    db_user = User(email=user.email, hashed_password=hashed_pwd, role=user.role)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return {
        "id": db_user.id,
        "email": db_user.email,
        "role": db_user.role,
        "created_at": str(db_user.created_at)
    }

@app.post("/login/", response_model=Token)
def login(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(
        data={"sub": db_user.email, "role": db_user.role},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return {"access_token": access_token, "token_type": "bearer"}

# --- Job Endpoints ---
@app.post("/jobs/", response_model=JobResponse)
def create_job(job: JobCreate, db: Session = Depends(get_db)):
    db_job = JobPosting(**job.dict())
    db.add(db_job)
    db.commit()
    db.refresh(db_job)
    return {**db_job.__dict__, "created_at": str(db_job.created_at)}

@app.get("/jobs/", response_model=List[JobResponse])
def list_jobs(db: Session = Depends(get_db)):
    jobs = db.query(JobPosting).all()
    return [{**j.__dict__, "created_at": str(j.created_at)} for j in jobs]

# --- Application Endpoints ---
@app.post("/applications/", response_model=ApplicationResponse)
def submit_application(app_data: ApplicationCreate, db: Session = Depends(get_db)):
    job = db.query(JobPosting).filter(JobPosting.id == app_data.job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job posting not found")
    
    db_app = Application(**app_data.dict())
    db.add(db_app)
    db.commit()
    db.refresh(db_app)
    return {**db_app.__dict__, "created_at": str(db_app.created_at)}

@app.get("/applications/", response_model=List[ApplicationResponse])
def list_applications(db: Session = Depends(get_db)):
    applications = db.query(Application).all()
    return [{**a.__dict__, "created_at": str(a.created_at)} for a in applications]