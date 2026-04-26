import logging
from typing import List

import httpx
from langchain_core.callbacks.manager import CallbackManagerForRetrieverRun
from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever

from app.core.config import settings

logger = logging.getLogger(__name__)


class DocsServiceRetriever(BaseRetriever):
    docs_url: str
    k: int = 4

    def _get_relevant_documents(
        self, query: str, *, run_manager: CallbackManagerForRetrieverRun
    ) -> List[Document]:
        try:
            resp = httpx.get(
                f"{self.docs_url}/methodology/search",
                params={"q": query, "k": self.k},
                timeout=5.0,
            )
            resp.raise_for_status()
            return [
                Document(page_content=c["content"], metadata={"source": c["source"]})
                for c in resp.json()
            ]
        except Exception as exc:
            logger.warning("Docs service unavailable (%s). Continuing without context.", exc)
            return []


def get_retriever() -> DocsServiceRetriever:
    return DocsServiceRetriever(docs_url=settings.DOCS_SERVICE_URL, k=4)
