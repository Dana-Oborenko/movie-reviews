# Database models for Movie and Review
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from app.db.session import Base

class Movie(Base):
    __tablename__ = "movies"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), unique=True, index=True, nullable=False)
    description = Column(Text, nullable=True)

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
