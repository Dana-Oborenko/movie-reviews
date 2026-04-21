# App settings loaded from environment variables (Pydantic v2)
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    APP_NAME: str = "Movie Reviews API"
    DB_URL: str = "sqlite:///./app.db"   # Replace with Postgres URL later if needed
    HF_TASK: str = "sentiment-analysis"  # Hugging Face pipeline task
    SUPABASE_URL: str = ""
    SUPABASE_JWT_AUD: str = "authenticated"
    SUPABASE_SERVICE_ROLE_KEY: str = ""

    # Tell pydantic-settings to read from .env in project root of backend
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = Settings()
