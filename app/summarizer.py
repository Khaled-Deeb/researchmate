from pathlib import Path

from app.ingest import load_pdf
from app.schemas import PaperSummary


DEFAULT_PDF_PATH = "data/papers/sample.pdf"


def clean_text(text: str, max_chars: int = 1000) -> str:
    """
    Normalize PDF text by removing extra spaces and cutting long text.
    """
    text = " ".join(text.split())
    return text[:max_chars]


def extract_title_from_first_page(first_page_text: str) -> str:
    """
    Simple title extraction.

    This is heuristic. Later the LLM will extract the title more reliably.
    """
    lines = [line.strip() for line in first_page_text.splitlines() if line.strip()]

    if not lines:
        return "Unknown title"

    # Many papers have the title in the first 1-3 lines.
    # Stop early if author-like lines appear.
    title_lines = []

    for line in lines[:5]:
        lowered = line.lower()

        if "abstract" in lowered:
            break

        if "@" in line:
            break

        if any(word in lowered for word in ["university", "institute", "department"]):
            break

        title_lines.append(line)

        if len(title_lines) >= 2:
            break

    if title_lines:
        return clean_text(" ".join(title_lines), max_chars=200)

    return clean_text(lines[0], max_chars=200)


def extract_abstract(first_page_text: str) -> str:
    """
    Extract the abstract from the first page if possible.
    """
    text = clean_text(first_page_text, max_chars=6000)

    abstract_markers = [
        "Abstractâ€”",
        "Abstract -",
        "Abstract:",
        "Abstract",
    ]

    introduction_markers = [
        "I. I NTRODUCTION",
        "I. INTRODUCTION",
        "1 Introduction",
        "1. Introduction",
        "Introduction",
    ]

    for abstract_marker in abstract_markers:
        if abstract_marker in text:
            after_abstract = text.split(abstract_marker, 1)[1]

            for intro_marker in introduction_markers:
                if intro_marker in after_abstract:
                    return clean_text(
                        after_abstract.split(intro_marker, 1)[0],
                        max_chars=1500,
                    )

            return clean_text(after_abstract, max_chars=1500)

    return clean_text(first_page_text, max_chars=1500)


def find_keyword_snippet(
    pages_text: list[str],
    keywords: list[str],
    max_chars: int = 900,
) -> str:
    """
    Find a rough evidence snippet containing any of the given keywords.
    """
    lowered_keywords = [keyword.lower() for keyword in keywords]

    for page_text in pages_text:
        normalized = clean_text(page_text, max_chars=6000)
        lowered_text = normalized.lower()

        for keyword in lowered_keywords:
            index = lowered_text.find(keyword)

            if index != -1:
                start = max(index - 250, 0)
                end = min(index + max_chars, len(normalized))
                return clean_text(normalized[start:end], max_chars=max_chars)

    return ""


def create_rough_paper_summary(pdf_path: str = DEFAULT_PDF_PATH) -> PaperSummary:
    """
    Create a rough structured summary without an LLM.

    This version is generic enough to work with multiple PDFs.
    It is intentionally conservative because final saving requires human review.
    Later, this function will use an LLM with structured output.
    """
    path = Path(pdf_path)

    if not path.exists():
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")

    pages = load_pdf(str(path))

    if not pages:
        raise ValueError("No pages found in the PDF.")

    pages_text = [page.page_content for page in pages]
    first_page_text = pages_text[0]

    title = extract_title_from_first_page(first_page_text)
    abstract = extract_abstract(first_page_text)

    method_snippet = find_keyword_snippet(
        pages_text,
        keywords=[
            "method",
            "approach",
            "algorithm",
            "model",
            "we propose",
            "we present",
        ],
    )

    dataset_snippet = find_keyword_snippet(
        pages_text,
        keywords=[
            "dataset",
            "datasets",
            "corpus",
            "collection",
            "experiments",
            "experimental setup",
        ],
    )

    metrics_snippet = find_keyword_snippet(
        pages_text,
        keywords=[
            "metric",
            "metrics",
            "evaluation",
            "accuracy",
            "recall",
            "precision",
            "f1",
            "relevance",
        ],
    )

    results_snippet = find_keyword_snippet(
        pages_text,
        keywords=[
            "results",
            "we achieve",
            "improvement",
            "outperform",
            "performance",
        ],
    )

    limitations_snippet = find_keyword_snippet(
        pages_text,
        keywords=[
            "limitations",
            "limitation",
            "future work",
            "threats to validity",
            "we note",
        ],
    )

    summary = PaperSummary(
        source_file=str(path),
        title=title,
        problem=(
            "Rough extraction from the abstract/introduction. "
            f"Evidence: {clean_text(abstract, max_chars=700)}"
        ),
        method=(
            "Rough method evidence. "
            f"Evidence: {method_snippet or clean_text(abstract, max_chars=700)}"
        ),
        dataset=(
            "Rough dataset/experimental-setting evidence. "
            f"Evidence: {dataset_snippet or 'Not clearly detected in the rule-based extraction.'}"
        ),
        metrics=(
            "Rough metrics/evaluation evidence. "
            f"Evidence: {metrics_snippet or 'Not clearly detected in the rule-based extraction.'}"
        ),
        main_results=(
            "Rough results evidence. "
            f"Evidence: {results_snippet or clean_text(abstract, max_chars=700)}"
        ),
        limitations=(
            "Rough limitations evidence. "
            f"Evidence: {limitations_snippet or 'No explicit limitations section was detected by the rule-based extraction.'}"
        ),
        relation_to_my_topic=(
            "Manual review needed. This paper should be related to the literature-review topic "
            "if it discusses table retrieval, structured evidence retrieval, table search, "
            "table summarization, or table-based question answering."
        ),
    )

    return summary