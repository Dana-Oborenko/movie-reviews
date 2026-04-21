# Movie endpoints: CRUD operations for movies
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.db import models
from app.schemas.movie import MovieCreate, MovieOut
from app.auth.deps import require_admin

router = APIRouter(prefix="/movies", tags=["movies"])


def get_db():
    """Provide a SQLAlchemy session per-request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("", response_model=MovieOut, status_code=201)
def create_movie(payload: MovieCreate, db: Session = Depends(get_db), _=Depends(require_admin)):
    """Create a new movie if title is unique."""
    if db.query(models.Movie).filter_by(title=payload.title).first():
        raise HTTPException(status_code=409, detail="Movie with this title already exists")
    movie = models.Movie(**payload.model_dump())
    db.add(movie)
    db.commit()
    db.refresh(movie)
    return movie


@router.get("", response_model=list[MovieOut])
def list_movies(db: Session = Depends(get_db)):
    """List all movies."""
    return db.query(models.Movie).all()


@router.get("/{movie_id}", response_model=MovieOut)
def get_movie(movie_id: int, db: Session = Depends(get_db)):
    """Get a single movie by id."""
    movie = db.query(models.Movie).get(movie_id)
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    return movie


@router.put("/{movie_id}", response_model=MovieOut)
def update_movie(movie_id: int, payload: MovieCreate, db: Session = Depends(get_db), _=Depends(require_admin)):
    """Update movie title/description."""
    movie = db.query(models.Movie).get(movie_id)
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")

    # Ensure title uniqueness
    exists = (
        db.query(models.Movie)
        .filter(models.Movie.title == payload.title, models.Movie.id != movie_id)
        .first()
    )
    if exists:
        raise HTTPException(status_code=409, detail="Movie with this title already exists")

    movie.title = payload.title
    movie.description = payload.description
    db.commit()
    db.refresh(movie)
    return movie


@router.delete("/{movie_id}", status_code=204)
def delete_movie(movie_id: int, db: Session = Depends(get_db), _=Depends(require_admin)):
    """Delete movie and its reviews (cascade)."""
    movie = db.query(models.Movie).get(movie_id)
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    db.delete(movie)
    db.commit()
