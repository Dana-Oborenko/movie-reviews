# Database models for Movie and Review
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from app.db.session import Base

class Movie(Base):
    __tablename__ = "movies"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), unique=True, index=True, nullable=False)
    description = Column(Text, nullable=True)

    year = Column(Integer, nullable=True)
    genres = Column(Text, nullable=True)  # store as JSON string or plain comma-separated text
    poster_url = Column(String(500), nullable=True)
    external_rating = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # One-to-many relationship: Movie -> Review
    reviews = relationship("Review", back_populates="movie", cascade="all,delete")

class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    movie_id = Column(Integer, ForeignKey("movies.id"), nullable=False, index=True)
    text = Column(Text, nullable=False)

    # Model output fields
    sentiment = Column(String(32), nullable=True)  # e.g., POSITIVE/NEGATIVE/NEUTRAL
    score = Column(String(32), nullable=True)      # stored as string to avoid float precision hassle

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Back reference to Movie
    movie = relationship("Movie", back_populates="reviews")

    # ML processing status: pending -> done/failed
    ml_status = Column(String(16), nullable=False, default="pending")
    ml_error = Column(Text, nullable=True)

# User roles table: maps Supabase user_id -> role (admin/user)
class UserRole(Base):
    __tablename__ = "user_roles"

    # Supabase user id (UUID string) stored as text
    user_id = Column(String(64), primary_key=True, index=True)
    role = Column(String(16), nullable=False, default="user")

