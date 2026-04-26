from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_core.retrievers import BaseRetriever
from langchain_core.documents import Document
from langchain_core.messages import BaseMessage
from typing import List, AsyncIterator

from app.chain.prompts import chat_prompt
from app.llm.providers import get_llm


def _format_docs(docs: List[Document]) -> str:
    if not docs:
        return "No hay guía metodológica disponible en la base de conocimiento."
    return "\n\n".join(
        f"[Fuente: {doc.metadata.get('source', 'desconocido')}]\n{doc.page_content}"
        for doc in docs
    )


def build_chain(retriever: BaseRetriever):
    chain = (
        RunnablePassthrough.assign(
            context=lambda x: _format_docs(retriever.invoke(x["question"]))
        )
        | chat_prompt
        | get_llm()
        | StrOutputParser()
    )
    return chain


async def invoke_chain(
    retriever: BaseRetriever,
    question: str,
    history: List[BaseMessage],
) -> str:
    chain = build_chain(retriever)
    return await chain.ainvoke({"question": question, "history": history})


async def stream_chain(
    retriever: BaseRetriever,
    question: str,
    history: List[BaseMessage],
) -> AsyncIterator[str]:
    chain = build_chain(retriever)
    async for chunk in chain.astream({"question": question, "history": history}):
        yield chunk
