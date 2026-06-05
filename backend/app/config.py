import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    API_KEY: str = "trap_talk_secret_key_2026"
    DATABASE_URL: str = "sqlite:///./traptalk.db"
    LLM_PROVIDER: str = "mock"  # Can be "mock", "gemini", "openai"
    CALLBACK_URL: str = "http://localhost:8000/api/v1/mock-callback"
    GEMINI_API_KEY: str = ""
    OPENAI_API_KEY: str = ""

    # Load from .env file if it exists
    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
