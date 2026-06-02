from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter


def load_pdf(pdf_path: str) -> list[Document]:
    """
    Load a PDF file and return one Document per page.
    """
    path = Path(pdf_path)

    if not path.exists():
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")

    if path.suffix.lower() != ".pdf":
        raise ValueError(f"Expected a PDF file, got: {path.suffix}")

    loader = PyPDFLoader(str(path))
    documents = loader.load()

    return documents


def split_documents(
    documents: list[Document],
    chunk_size: int = 1200,
    chunk_overlap: int = 200,
) -> list[Document]:
    """
    Split loaded PDF pages into smaller chunks for retrieval.
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )

    chunks = splitter.split_documents(documents)

    return chunks


def inspect_pdf(pdf_path: str) -> None:
    """
    Load and split a PDF, then print basic information.
    This is only for testing the ingestion pipeline.
    """
    documents = load_pdf(pdf_path)
    chunks = split_documents(documents)

    print("=" * 80)
    print("PDF loaded successfully")
    print("=" * 80)
    print(f"PDF path: {pdf_path}")
    print(f"Number of pages: {len(documents)}")
    print(f"Number of chunks: {len(chunks)}")

    print("\n" + "=" * 80)
    print("First chunk preview")
    print("=" * 80)

    if chunks:
        first_chunk = chunks[0]
        print(first_chunk.page_content[:1000])
        print("\nMetadata:")
        print(first_chunk.metadata)
    else:
        print("No chunks were created.")