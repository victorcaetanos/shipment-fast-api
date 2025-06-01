import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """Database dependency for FastAPI"""
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        db.rollback()
        raise
    finally:
        db.close()


def create_tables():
    """Create all tables in the database"""

    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully!")


def drop_tables():
    """Drop all tables (useful for development)"""
    Base.metadata.drop_all(bind=engine)
    print("🗑️ All tables dropped!")


def reset_database():
    """Drop and recreate all tables"""
    drop_tables()
    create_tables()
