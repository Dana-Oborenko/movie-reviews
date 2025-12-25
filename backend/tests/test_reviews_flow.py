# Tests for reviews endpoints including async ML background behavior
import time


def test_create_review_pending_then_done(client, monkeypatch):
    """
    Review should be created immediately with ml_status='pending',
    then background task updates it to done with sentiment/score.
    """

    # Mock analyze_sentiment to be fast and deterministic
    import app.routers.reviews as reviews_router

    def fake_analyze(text: str):
        return "POSITIVE", "0.9000"

    monkeypatch.setattr(reviews_router, "analyze_sentiment", fake_analyze)


    # 1) Create movie
    r = client.post("/movies", json={"title": "Inception", "description": "Nolan"})
    assert r.status_code == 201
    movie_id = r.json()["id"]

    # 2) Create review (background ML)
    r = client.post("/reviews", json={"movie_id": movie_id, "text": "Amazing!"})
    assert r.status_code == 201
    data = r.json()

    # created immediately
    assert data["movie_id"] == movie_id
    assert data["ml_status"] in ("pending", "done")  # depending on how fast bg runs

    # 3) Poll until done (max ~2 seconds)
    done = False
    for _ in range(20):
        rr = client.get(f"/reviews?movie_id={movie_id}")
        assert rr.status_code == 200
        items = rr.json()
        assert len(items) >= 1

        item = items[0]
        if item.get("ml_status") == "done":
            assert item["sentiment"] == "POSITIVE"
            assert item["score"] == "0.9000"
            done = True
            break

        time.sleep(0.1)

    assert done, "Review ML analysis did not complete in time"


def test_retry_endpoint(client, monkeypatch):
    import app.routers.reviews as reviews_router

    def fake_analyze(text: str):
        return "NEGATIVE", "0.8000"

    monkeypatch.setattr(reviews_router, "analyze_sentiment", fake_analyze)

    # Create movie
    r = client.post("/movies", json={"title": "Interstellar", "description": "Space"})
    movie_id = r.json()["id"]

    # Create review
    r = client.post("/reviews", json={"movie_id": movie_id, "text": "Ok"})
    review_id = r.json()["id"]

    # Retry
    r = client.post(f"/reviews/{review_id}/retry")
    assert r.status_code == 200
    assert r.json()["status"] == "scheduled"

import time
import app.routers.reviews as reviews_router

def test_review_analysis_failed_sets_status(client, monkeypatch):
    def boom(_text: str):
        raise RuntimeError("ml crashed")

    monkeypatch.setattr(reviews_router, "analyze_sentiment", boom)

    r = client.post("/movies", json={"title": "BadML", "description": "x"})
    movie_id = r.json()["id"]

    r = client.post("/reviews", json={"movie_id": movie_id, "text": "test"})
    assert r.status_code == 201

    failed = False
    for _ in range(20):
        rr = client.get(f"/reviews?movie_id={movie_id}")
        item = rr.json()[0]
        if item.get("ml_status") == "failed":
            assert "ml crashed" in (item.get("ml_error") or "")
            failed = True
            break
        time.sleep(0.1)

    assert failed, "Review ML failure status did not appear"
