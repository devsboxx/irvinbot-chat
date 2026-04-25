import chromadb
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from app.core.config import settings


def get_retriever():
    # Anthropic does not provide embedding models; OpenAI embeddings are used regardless of LLM_PROVIDER.
    embeddings = OpenAIEmbeddings(api_key=settings.OPENAI_API_KEY)

    chroma_client = chromadb.HttpClient(
        host=settings.CHROMA_HOST,
        port=settings.CHROMA_PORT,
    )

    vectorstore = Chroma(
        client=chroma_client,
        collection_name=settings.CHROMA_COLLECTION,
        embedding_function=embeddings,
    )
    return vectorstore.as_retriever(search_kwargs={"k": 4})
