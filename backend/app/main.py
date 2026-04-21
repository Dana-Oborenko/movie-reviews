# FastAPI application entry point
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import health, movies, reviews
from fastapi import Depends
from app.auth.deps import get_current_user


app = FastAPI(title="Movie Reviews API", version="0.1.0")

# CORS for local Vue dev server
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(health.router)
app.include_router(movies.router)
app.include_router(reviews.router)

@app.get("/me")
async def me(user=Depends(get_current_user)):
    return user
