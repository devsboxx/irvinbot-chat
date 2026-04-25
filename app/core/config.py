from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/irvinbot_chat"
    SECRET_KEY: str = "change-me-in-production"
    ALGORITHM: str = "HS256"

    # ── LLM ──────────────────────────────────────────────────────────────────
    # Opciones: ollama | groq | openai | anthropic
    LLM_PROVIDER: str = "ollama"
    LLM_MODEL: Optional[str] = None  # vacío = usa el default del proveedor

    # ── Embeddings ───────────────────────────────────────────────────────────
    # Opciones: ollama | openai
    EMBEDDING_PROVIDER: str = "ollama"
    EMBEDDING_MODEL: Optional[str] = None

    # ── Credenciales de proveedores ───────────────────────────────────────────
    ANTHROPIC_API_KEY: str = ""
    OPENAI_API_KEY: str = ""
    GROQ_API_KEY: str = ""

    # ── Ollama (local) ────────────────────────────────────────────────────────
    OLLAMA_BASE_URL: str = "http://localhost:11434"

    # ── ChromaDB ─────────────────────────────────────────────────────────────
    CHROMA_HOST: str = "localhost"
    CHROMA_PORT: int = 8004
    CHROMA_COLLECTION: str = "thesis_docs"

    class Config:
        env_file = ".env"


settings = Settings()
