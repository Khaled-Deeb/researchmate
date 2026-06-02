from pathlib import Path

from langchain_core.documents import Document
from langchain_core.vectorstores import InMemoryVectorStore

from app.ingest import load_pdf, split_documents
from app.llm import get_embedding_model


def build_in_memory_vector_store(pdf_path: str) -> InMemoryVectorStore:
    """
    Build an in-memory semantic vector store for one PDF.

    This is planned for OpenAI-powered mode.
    It is not used by the fallback mode.
    """
    path = Path(pdf_path)

    if not path.exists():
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")

    pages = load_pdf(str(path))
    chunks = split_documents(pages)

    embedding_model = get_embedding_model()

    vector_store = InMemoryVectorStore(embedding_model)
    vector_store.add_documents(chunks)

    return vector_store


def semantic_search_pdf(
    pdf_path: str,
    query: str,
    k: int = 4,
) -> list[Document]:
    """
    Search a PDF semantically using embeddings.

    This is planned for OpenAI-powered mode.
    It is not used by the fallback mode.
    """
    vector_store = build_in_memory_vector_store(pdf_path)
    return vector_store.similarity_search(query, k=k)