# app/database.py

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from redis import Redis
from typing import Generator
from app.config import settings

# PostgreSQL Database Engine
engine = create_engine(
    settings.DATABASE_URL,
    pool_size=settings.DATABASE_POOL_SIZE,
    max_overflow=settings.DATABASE_MAX_OVERFLOW,
    pool_pre_ping=True,  # Verify connections before using them
    echo=settings.DEBUG,
)

# Session Factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base Class for Models
Base = declarative_base()

# Redis Connection
redis_client = Redis.from_url(settings.REDIS_URL, decode_responses=True)


def get_db() -> Generator[Session, None, None]:
    """
    Dependency for getting database sessions.
    Use with FastAPI Depends().
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_redis() -> Redis:
    """
    Dependency for getting Redis client.
    Use with FastAPI Depends().
    """
    return redis_client


def init_db() -> None:
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)


def drop_db() -> None:
    """Drop all database tables (use with caution!)"""
    Base.metadata.drop_all(bind=engine)
