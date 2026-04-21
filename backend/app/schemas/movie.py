# Pydantic schemas for Movie I/O validation
from pydantic import BaseModel, ConfigDict


class MovieBase(BaseModel):
    title: str
    description: str | None = None
    year: int | None = None
    genres: str | None = None
    poster_url: str | None = None
    external_rating: int | None = None


class MovieCreate(MovieBase):
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "title": "Inception",
            "description": "Sci-fi heist film by Christopher Nolan",
            "year": 2010,
            "genres": '["Sci-Fi", "Thriller"]',
            "poster_url": "https://example.com/inception.jpg",
            "external_rating": 9
        }
    })


class MovieOut(MovieBase):
    id: int

    class Config:
        from_attributes = True