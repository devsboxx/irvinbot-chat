"""
LLM provider factory.

Soportados
----------
LLM_PROVIDER    | Modelo por defecto              | API key requerida
----------------|---------------------------------|------------------
ollama          | llama3.2                        | no (local)
groq            | llama-3.3-70b-versatile         | GROQ_API_KEY
openai          | gpt-4o                          | OPENAI_API_KEY
anthropic       | claude-sonnet-4-6               | ANTHROPIC_API_KEY

EMBEDDING_PROVIDER | Modelo por defecto         | API key requerida
-------------------|----------------------------|------------------
ollama             | nomic-embed-text           | no (local)
openai             | text-embedding-3-small     | OPENAI_API_KEY

Para cambiar de proveedor basta con ajustar LLM_PROVIDER / EMBEDDING_PROVIDER
en el .env — el código de pipeline y retriever no cambia.
"""

from langchain_core.language_models import BaseChatModel
from langchain_core.embeddings import Embeddings

from app.core.config import settings

_LLM_DEFAULTS: dict[str, str] = {
    "ollama": "llama3.2",
    "groq": "llama-3.3-70b-versatile",
    "openai": "gpt-4o",
    "anthropic": "claude-sonnet-4-6",
}

_EMBEDDING_DEFAULTS: dict[str, str] = {
    "ollama": "nomic-embed-text",
    "openai": "text-embedding-3-small",
}


def get_llm() -> BaseChatModel:
    """Return a LangChain chat model for the configured provider."""
    provider = settings.LLM_PROVIDER.lower()
    model = settings.LLM_MODEL or _LLM_DEFAULTS.get(provider)

    if provider == "ollama":
        from langchain_ollama import ChatOllama
        return ChatOllama(model=model, base_url=settings.OLLAMA_BASE_URL)

    if provider == "groq":
        from langchain_groq import ChatGroq
        return ChatGroq(model=model, api_key=settings.GROQ_API_KEY)

    if provider == "openai":
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(model=model, api_key=settings.OPENAI_API_KEY)

    if provider == "anthropic":
        from langchain_anthropic import ChatAnthropic
        return ChatAnthropic(model=model, api_key=settings.ANTHROPIC_API_KEY)

    raise ValueError(
        f"LLM_PROVIDER '{provider}' no reconocido. "
        "Opciones: ollama, groq, openai, anthropic"
    )


def get_embeddings() -> Embeddings:
    """Return a LangChain embeddings model for the configured provider."""
    provider = settings.EMBEDDING_PROVIDER.lower()
    model = settings.EMBEDDING_MODEL or _EMBEDDING_DEFAULTS.get(provider)

    if provider == "ollama":
        from langchain_ollama import OllamaEmbeddings
        return OllamaEmbeddings(model=model, base_url=settings.OLLAMA_BASE_URL)

    if provider == "openai":
        from langchain_openai import OpenAIEmbeddings
        return OpenAIEmbeddings(model=model, api_key=settings.OPENAI_API_KEY)

    raise ValueError(
        f"EMBEDDING_PROVIDER '{provider}' no reconocido. "
        "Opciones: ollama, openai"
    )
