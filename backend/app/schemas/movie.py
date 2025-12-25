# Pydantic schemas for Movie I/O validation
from pydantic import BaseModel
from pydantic import ConfigDict

class MovieBase(BaseModel):
    title: str
    description: str | None = None

class MovieCreate(MovieBase):
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "title": "Inception",
            "description": "Sci-fi heist film by Christopher Nolan"
        }
    })

class MovieOut(MovieBase):
    id: int

    class Config:
        from_attributes = True  # allow ORM objects to be returned
