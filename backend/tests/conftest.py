# Pytest fixtures: test DB + FastAPI test client
import os
import sys
import tempfile
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Ensure "backend" is on sys.path so "import app" works
BACKEND_DIR = Path(__file__).resolve().parents[1]  # .../backend
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.main import app
from app.db.session import Base

# Import models so Base has tables
from app.db import models  # noqa: F401


@pytest.fixture(scope="session")
def test_db_url():
    # Use a temporary SQLite file for tests
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    return f"sqlite:///{path}"


@pytest.fixture(scope="session")
def engine(test_db_url):
    engine = create_engine(test_db_url, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    return engine


@pytest.fixture(scope="session")
def TestingSessionLocal(engine):
    return sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def client(monkeypatch, TestingSessionLocal):
    """
    Patch SessionLocal used inside routers (movies.py, reviews.py)
    so API uses the test database.
    """
    # Patch app.db.session.SessionLocal (for any code that imports it later)
    import app.db.session as session_module
    monkeypatch.setattr(session_module, "SessionLocal", TestingSessionLocal)

    # Patch routers that already imported SessionLocal at module import time
    import app.routers.movies as movies_router
    import app.routers.reviews as reviews_router

    monkeypatch.setattr(movies_router, "SessionLocal", TestingSessionLocal)
    monkeypatch.setattr(reviews_router, "SessionLocal", TestingSessionLocal)

    with TestClient(app) as c:
        yield c
