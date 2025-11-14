import logging
from pathlib import Path
from sqlalchemy import create_engine, Column, Integer, String, Float, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

logger = logging.getLogger(__name__)

Base = declarative_base()


class Outlet(Base):
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


DATABASE_DIR = Path("data")
DATABASE_DIR.mkdir(exist_ok=True)
DATABASE_URL = f"sqlite:///{DATABASE_DIR / 'outlets.db'}"

engine = create_engine(
    DATABASE_URL,
    connect_args={
        "check_same_thread": False,
        "timeout": 30.0
    },
    echo=False
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
    logger.info(f"Database initialized at {DATABASE_URL}")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_db_sync():
    return SessionLocal()
