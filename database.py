import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# SQLite database file stored locally in your app directory
SQLALCHEMY_DATABASE_URL = "sqlite:///./hireiq.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependency to get the database session in endpoints
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()