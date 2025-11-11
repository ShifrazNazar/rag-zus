"""
Database models and connection for SQLite outlets database.
"""
import os
import logging
from pathlib import Path
from sqlalchemy import create_engine, Column, Integer, String, Float, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from typing import Optional

logger = logging.getLogger(__name__)

Base = declarative_base()


class Outlet(Base):
    """SQLAlchemy model for outlets table."""
    __tablename__ = "outlets"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    location = Column(String, nullable=False)
    district = Column(String, nullable=True, index=True)
    hours = Column(String, nullable=True)
    services = Column(Text, nullable=True)
    lat = Column(Float, nullable=True)
    lon = Column(Float, nullable=True)
    
    def to_dict(self) -> dict:
        """Convert outlet to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "location": self.location,
            "district": self.district,
            "hours": self.hours,
            "services": self.services,
            "lat": self.lat,
            "lon": self.lon
        }


# Database connection
DATABASE_DIR = Path("data")
DATABASE_DIR.mkdir(exist_ok=True)
DATABASE_URL = f"sqlite:///{DATABASE_DIR / 'outlets.db'}"

# Create engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},  # Needed for SQLite
    echo=False  # Set to True for SQL query logging
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db() -> None:
    """Initialize database by creating all tables."""
    Base.metadata.create_all(bind=engine)
    logger.info(f"Database initialized at {DATABASE_URL}")


def get_db():
    """
    Get database session.
    
    Yields:
        Database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_db_sync():
    """
    Get synchronous database session (for non-async contexts).
    
    Returns:
        Database session
    """
    return SessionLocal()

