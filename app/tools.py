from collections import Counter
from pathlib import Path
import re

from langchain_core.tools import tool

from app.compare import (
    create_markdown_comparison_table,
    save_csv_comparison_table,
    save_markdown_comparison_table,
)
from app.ingest import load_pdf, split_documents
from app.summarizer import create_rough_paper_summary


DEFAULT_PDF_PATH = "data/papers/sample.pdf"


STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "by",
    "does",
    "for",
    "from",
    "how",
    "in",
    "is",
    "it",
    "of",
    "on",
    "or",
    "paper",
    "solve",
    "that",
    "the",
    "this",
    "to",
    "what",
    "when",
    "where",
    "which",
    "who",
    "why",
    "with",
}


def tokenize(text: str) -> list[str]:
    """
    Convert text into lowercase words and remove common stopwords.
    """
    words = re.findall(r"\w+", text.lower())
    return [word for word in words if word not in STOPWORDS and len(word) > 2]


def simple_keyword_score(query: str, text: str) -> int:
    """
    Simple keyword search score.

    This is temporary.
    Later we will replace it with vector search using embeddings.
    """
    query_words = tokenize(query)
    text_words = tokenize(text)

    text_counter = Counter(text_words)

    score = 0
    for word in query_words:
        score += text_counter[word]

    return score


def clean_display_text(text: str, max_chars: int = 1200) -> str:
    """
    Normalize text for display.
    """
    text = " ".join(text.split())
    return text[:max_chars]


def find_relevant_chunks(
    query: str,
    pdf_path: str = DEFAULT_PDF_PATH,
    top_k: int = 3,
) -> list[dict]:
    """
    Find relevant chunks in a PDF.

    Returns structured chunk information instead of plain text.
    """
    path = Path(pdf_path)

    if not path.exists():
        return []

    pages = load_pdf(str(path))
    chunks = split_documents(pages)

    scored_chunks = []

    for chunk in chunks:
        score = simple_keyword_score(query, chunk.page_content)

        if score > 0:
            scored_chunks.append((score, chunk))

    scored_chunks.sort(key=lambda item: item[0], reverse=True)

    results = []

    for score, chunk in scored_chunks[:top_k]:
        results.append(
            {
                "score": score,
                "page": chunk.metadata.get("page", "unknown"),
                "text": clean_display_text(chunk.page_content, max_chars=1200),
            }
        )

    return results


def search_paper_text(
    query: str,
    pdf_path: str = DEFAULT_PDF_PATH,
    top_k: int = 3,
) -> str:
    """
    Search inside a PDF and return the most relevant chunks.
    """
    path = Path(pdf_path)

    if not path.exists():
        return f"PDF file not found: {path}"

    chunks = find_relevant_chunks(query=query, pdf_path=pdf_path, top_k=top_k)

    if not chunks:
        return "No relevant chunks found."

    results = []

    for index, chunk in enumerate(chunks, start=1):
        results.append(
            f"Result {index}\n"
            f"Page: {chunk['page']}\n"
            f"Score: {chunk['score']}\n"
            f"Text:\n{chunk['text']}"
        )

    separator = "\n\n" + ("=" * 80) + "\n\n"
    return separator + separator.join(results)


def split_into_sentences(text: str) -> list[str]:
    """
    Very simple sentence splitter.
    """
    text = " ".join(text.split())
    sentences = re.split(r"(?<=[.!?])\s+", text)
    return [sentence.strip() for sentence in sentences if sentence.strip()]


def choose_best_sentences(query: str, text: str, max_sentences: int = 3) -> str:
    """
    Pick relevant sentences from retrieved evidence.

    This is temporary extractive answering.
    Later the LLM will synthesize the answer.
    """
    query_words = set(tokenize(query))
    sentences = split_into_sentences(text)

    if not sentences:
        return text[:500]

    scored_sentences = []

    for index, sentence in enumerate(sentences):
        sentence_words = set(tokenize(sentence))
        score = len(query_words.intersection(sentence_words))

        # Bonus for definition-like sentences.
        definition_markers = [
            "refers to",
            "is defined",
            "we define",
            "problem",
            "identification",
            "such that",
        ]

        if any(marker in sentence.lower() for marker in definition_markers):
            score += 3

        if score > 0:
            scored_sentences.append((score, index, sentence))

    scored_sentences.sort(key=lambda item: item[0], reverse=True)

    if not scored_sentences:
        return text[:500]

    best_indices = []

    for _, index, _ in scored_sentences[:max_sentences]:
        best_indices.append(index)

        # Include the next sentence too, because definitions often continue.
        if index + 1 < len(sentences):
            best_indices.append(index + 1)

    best_indices = sorted(set(best_indices))[:max_sentences]

    best_sentences = [sentences[index] for index in best_indices]

    return " ".join(best_sentences)


def answer_paper_question_text(
    query: str,
    pdf_path: str = DEFAULT_PDF_PATH,
) -> str:
    """
    Create a simple extractive answer using retrieved chunks.

    This is not an LLM answer yet.
    It selects relevant sentences from the best retrieved chunk.
    """
    chunks = find_relevant_chunks(query=query, pdf_path=pdf_path, top_k=3)

    if not chunks:
        return "I could not find relevant evidence in the current paper."

    best_chunk = chunks[0]
    answer = choose_best_sentences(query=query, text=best_chunk["text"])

    evidence_parts = []

    for index, chunk in enumerate(chunks, start=1):
        evidence_parts.append(
            f"Evidence {index}\n"
            f"Page: {chunk['page']}\n"
            f"Score: {chunk['score']}\n"
            f"Text:\n{chunk['text']}"
        )

    separator = "\n\n" + ("=" * 80) + "\n\n"

    return (
        "TEMPORARY EXTRACTIVE ANSWER\n"
        "This answer is selected from retrieved text, not generated by an LLM yet.\n\n"
        f"Answer:\n{answer}\n"
        f"{separator}"
        f"{separator.join(evidence_parts)}"
    )


@tool
def search_current_paper(query: str) -> str:
    """
    Search inside the current research paper and return relevant text chunks.
    Use this when the user asks to find passages or evidence in the paper.
    """
    return search_paper_text(query=query, pdf_path=DEFAULT_PDF_PATH)


@tool
def answer_current_paper_question(query: str) -> str:
    """
    Answer a question about the current paper using retrieved evidence.
    Use this when the user asks what something means or asks for an explanation.
    """
    return answer_paper_question_text(query=query, pdf_path=DEFAULT_PDF_PATH)


@tool
def summarize_current_paper() -> str:
    """
    Create a structured rough summary of the current research paper.
    Use this when the user asks for a summary or paper card.
    """
    summary = create_rough_paper_summary(DEFAULT_PDF_PATH)
    return summary.model_dump_json(indent=2)


@tool
def compare_saved_papers() -> str:
    """
    Create a Markdown comparison table from all approved saved paper summaries.
    Use this when the user asks to compare papers or generate a literature table.
    """
    return create_markdown_comparison_table()


@tool
def export_comparison_table() -> str:
    """
    Export the saved paper summaries as Markdown and CSV comparison tables.
    Use this when the user asks to save, export, or create files.
    """
    markdown_path = save_markdown_comparison_table()
    csv_path = save_csv_comparison_table()

    return (
        "Export complete.\n"
        f"Markdown saved to: {markdown_path}\n"
        f"CSV saved to: {csv_path}"
    )


RESEARCHMATE_TOOLS = [
    search_current_paper,
    answer_current_paper_question,
    summarize_current_paper,
    compare_saved_papers,
    export_comparison_table,
]