# Movie Reviews — Admin (FastAPI + Vue + ML)

A full-stack web application for managing movie reviews with automatic sentiment analysis.
The backend is built with **FastAPI**, the frontend is built with **Vue 3**, and the sentiment analysis uses a **Hugging Face** model.
The project demonstrates an **async ML workflow** (review is created instantly, analysis runs in background), statistics, testing, and CI-ready structure.

---

## Features

### Backend (FastAPI)
- CRUD for **movies** and **reviews**
- **Swagger/OpenAPI** docs at `/docs`
- Sentiment analysis with **Hugging Face** (`distilbert-base-uncased-finetuned-sst-2-english`)
- **Async ML pipeline**:
  - review is created immediately (`ml_status="pending"`)
  - analysis is executed in background
  - review is updated later (`ml_status="done"` or `"failed"`)
- Retry analysis endpoint: `POST /reviews/{id}/retry`
- Statistics endpoint: `GET /reviews/stats`
- Database schema management with **Alembic**

### Frontend (Vue 3)
- Admin panel:
  - create and delete movies
  - create and delete reviews
  - filter reviews by movie
- Live ML status in UI:
  - `analyzing...` while `ml_status="pending"`
  - `failed` status + Retry button if analysis failed
- Auto-refresh (polling) while there are pending reviews
- Sentiment statistics + **pie chart**

### Tests
- `pytest` + FastAPI TestClient
- ML behavior is tested with mocking
- Coverage report via `pytest-cov` (current coverage ~82%)

---

## Tech Stack

- **Backend:** Python 3.11, FastAPI, SQLAlchemy, Alembic
- **ML:** Transformers (Hugging Face), Torch
- **Frontend:** Vue 3, Vite, vue-router, chart.js (via vue-chartjs)
- **Testing:** pytest, httpx, pytest-cov

---

## Project Structure
movie-reviews/
├─ backend/
│ ├─ app/
│ │ ├─ core/ # config
│ │ ├─ db/ # models + DB session
│ │ ├─ routers/ # API routes (movies, reviews, health)
│ │ ├─ schemas/ # Pydantic schemas
│ │ ├─ services/ # ML service (Hugging Face pipeline)
│ │ └─ main.py # FastAPI app entry
│ ├─ alembic/ # migrations
│ ├─ tests/ # pytest tests
│ ├─ requirements.txt
│ ├─ pytest.ini
│ └─ .coveragerc
├─ frontend/
│ ├─ src/
│ │ ├─ views/ # MoviesAdminView, MovieDetailView
│ │ ├─ components/ # SentimentChart, etc.
│ │ ├─ router/ # vue-router config
│ │ └─ api.js # axios client
│ └─ package.json
└─ .github/workflows/ # CI workflows (optional)

## Getting Started (Local)

### 1) Backend setup

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # macOS/Linux
# .venv\Scripts\activate   # Windows

pip install -r requirements.txt