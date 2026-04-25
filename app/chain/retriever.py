import logging
from typing import List

import chromadb
from langchain_chroma import Chroma
from langchain_core.retrievers import BaseRetriever
from langchain_core.documents import Document
from langchain_core.callbacks.manager import CallbackManagerForRetrieverRun

from app.core.config import settings
from app.llm.providers import get_embeddings

logger = logging.getLogger(__name__)


class _NullRetriever(BaseRetriever):
    """Fallback cuando ChromaDB no está disponible: devuelve siempre vacío."""

    def _get_relevant_documents(
        self, query: str, *, run_manager: CallbackManagerForRetrieverRun
    ) -> List[Document]:
        return []


def get_retriever() -> BaseRetriever:
    try:
        chroma_client = chromadb.HttpClient(
            host=settings.CHROMA_HOST,
            port=settings.CHROMA_PORT,
        )
        vectorstore = Chroma(
            client=chroma_client,
            collection_name=settings.CHROMA_COLLECTION,
            embedding_function=get_embeddings(),
        )
        return vectorstore.as_retriever(search_kwargs={"k": 4})
    except Exception as exc:
        logger.warning(
            "ChromaDB no disponible en %s:%s (%s). "
            "El chat funcionará sin contexto de documentos.",
            settings.CHROMA_HOST, settings.CHROMA_PORT, exc,
        )
        return _NullRetriever()
