"""
Central configuration. All secrets/keys come from environment variables
(see .env.example) - never hardcode keys here.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql://postgres:postgres@localhost:5432/job_assistant"

    # Auth
    jwt_secret: str = "change-this-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24 * 7  # 7 days

    # Job data providers
    adzuna_app_id: str = ""
    adzuna_app_key: str = ""
    jooble_api_key: str = ""

    # Google Sign-In
    google_client_id: str = ""

    # AI provider (stubbed for now - plug in Groq/OpenAI/etc later)
    ai_provider: str = "stub"  # "groq" | "openai" | "stub"
    ai_api_key: str = ""

    # CORS
    frontend_origin: str = "http://localhost:5173"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()