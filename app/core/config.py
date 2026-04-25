from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/irvinbot_chat"
    SECRET_KEY: str = "change-me-in-production"
    ALGORITHM: str = "HS256"

    LLM_PROVIDER: str = "anthropic"  # anthropic | openai
    ANTHROPIC_API_KEY: str = ""
    OPENAI_API_KEY: str = ""
    LLM_MODEL: Optional[str] = None  # falls back to provider default

    CHROMA_HOST: str = "localhost"
    CHROMA_PORT: int = 8004
    CHROMA_COLLECTION: str = "thesis_docs"

    class Config:
        env_file = ".env"


settings = Settings()
