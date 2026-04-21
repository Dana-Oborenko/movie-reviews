# Review endpoints: create (with background ML), list, delete, stats
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.db.session import SessionLocal
from app.db import models
from app.schemas.review import ReviewCreate, ReviewOut
from app.services.ml import analyze_sentiment
from app.auth.deps import require_admin

router = APIRouter(prefix="/reviews", tags=["reviews"])


def get_db():
    """Provide a SQLAlchemy session per-request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def run_sentiment_in_background(review_id: int) -> None:
    """
    Background task: load review from DB, run ML, update fields and status.
    """
    db = SessionLocal()
    try:
        review = db.query(models.Review).get(review_id)
        if not review:
            return

        try:
            label, score = analyze_sentiment(review.text)
            review.sentiment = label
            review.score = score
            review.ml_status = "done"
            review.ml_error = None
        except Exception as exc:
            review.ml_status = "failed"
            review.ml_error = str(exc)

        db.commit()
    finally:
        db.close()

@router.post("", response_model=ReviewOut, status_code=201)
def create_review(
    payload: ReviewCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """
    Create a review for a movie.
    Sentiment analysis is executed in the background.
    """
    movie = db.query(models.Movie).get(payload.movie_id)
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")

    # Create review WITHOUT sentiment for now
    review = models.Review(
        movie_id=payload.movie_id,
        text=payload.text,
        sentiment=None,
        score=None,
        ml_status="pending",
        ml_error=None,
    )
    db.add(review)
    db.commit()
    db.refresh(review)

    # Schedule background ML analysis
    background_tasks.add_task(run_sentiment_in_background, review.id)

    # Return review immediately (sentiment/score may be null)
    return review


@router.get("", response_model=list[ReviewOut])
def list_reviews(
    db: Session = Depends(get_db),
    movie_id: int | None = None,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    """
    List reviews. Optionally filter by movie_id and paginate.
    """
    q = db.query(models.Review)
    if movie_id is not None:
        q = q.filter(models.Review.movie_id == movie_id)

    return (
        q.order_by(models.Review.id.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )


@router.delete("/{review_id}", status_code=204)
def delete_review(review_id: int, db: Session = Depends(get_db), _=Depends(require_admin)):
    """Delete a single review."""
    review = db.query(models.Review).get(review_id)
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    db.delete(review)
    db.commit()


@router.get("/stats", summary="Get sentiment statistics by label")
def reviews_stats(db: Session = Depends(get_db)):
    """
    Simple sentiment distribution:
    returns count of reviews per sentiment label.
    """
    rows = (
        db.query(models.Review.sentiment, func.count(models.Review.id))
        .group_by(models.Review.sentiment)
        .all()
    )
    return {sentiment or "UNKNOWN": count for sentiment, count in rows}

@router.post("/{review_id}/retry", summary="Retry sentiment analysis for a review")
def retry_review(review_id: int, background_tasks: BackgroundTasks, db: Session = Depends(get_db), _=Depends(require_admin)):
    """
    Reset ML status to pending and re-run sentiment analysis in background.
    """
    review = db.query(models.Review).get(review_id)
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")

    review.ml_status = "pending"
    review.ml_error = None
    review.sentiment = None
    review.score = None
    db.commit()

    background_tasks.add_task(run_sentiment_in_background, review.id)
    return {"status": "scheduled", "review_id": review.id}

