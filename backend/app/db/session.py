# SQLAlchemy engine/session factory and declarative base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

# For SQLite in single-thread dev mode
engine = create_engine(settings.DB_URL, connect_args={"check_same_thread": False} if settings.DB_URL.startswith("sqlite") else {})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
