# Pydantic schemas for Review I/O validation
from pydantic import BaseModel, ConfigDict

class ReviewCreate(BaseModel):
    movie_id: int
    text: str

    # OpenAPI example shown in Swagger UI for POST /reviews
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "movie_id": 1,
            "text": "Amazing movie with a mind-bending plot and great visuals!"
        }
    })

class ReviewOut(BaseModel):
    id: int
    movie_id: int
    text: str
    sentiment: str | None = None
    score: str | None = None
    ml_status: str | None = None
    ml_error: str | None = None

    class Config:
        from_attributes = True


