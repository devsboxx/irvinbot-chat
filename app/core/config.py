from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/irvinbot_chat"
    SECRET_KEY: str = "change-me-in-production"
    ALGORITHM: str = "HS256"

    # ── LLM ──────────────────────────────────────────────────────────────────
    # Opciones: ollama | groq | openai | anthropic
    LLM_PROVIDER: str = "ollama"
    LLM_MODEL: Optional[str] = None

    # ── Credenciales de proveedores ───────────────────────────────────────────
    ANTHROPIC_API_KEY: str = ""
    OPENAI_API_KEY: str = ""
    GROQ_API_KEY: str = ""

    # ── Ollama (local) ────────────────────────────────────────────────────────
    OLLAMA_BASE_URL: str = "http://localhost:11434"

    # ── Docs service ─────────────────────────────────────────────────────────
    DOCS_SERVICE_URL: str = "http://localhost:8003"

    class Config:
        env_file = ".env"


settings = Settings()
