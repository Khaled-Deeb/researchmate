from pathlib import Path

from app.ingest import load_pdf
from app.llm import get_chat_model
from app.schemas import PaperSummary
from app.summarizer import (
    clean_text,
    extract_abstract,
    extract_title_from_first_page,
    find_keyword_snippet,
)


def build_summary_evidence(pdf_path: str) -> str:
    """
    Build compact evidence for LLM-based structured extraction.

    We intentionally avoid sending the full PDF to control cost.
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
            "map",
            "mrr",
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
            "state-of-the-art",
        ],
    )

    limitations_snippet = find_keyword_snippet(
        pages_text,
        keywords=[
            "limitations",
            "limitation",
            "future work",
            "threats to validity",
        ],
    )

    return f"""
SOURCE FILE:
{pdf_path}

DETECTED TITLE:
{title}

ABSTRACT:
{clean_text(abstract, max_chars=1500)}

METHOD EVIDENCE:
{clean_text(method_snippet, max_chars=1000)}

DATASET / EXPERIMENT EVIDENCE:
{clean_text(dataset_snippet, max_chars=1000)}

METRICS EVIDENCE:
{clean_text(metrics_snippet, max_chars=1000)}

RESULTS EVIDENCE:
{clean_text(results_snippet, max_chars=1000)}

LIMITATIONS EVIDENCE:
{clean_text(limitations_snippet, max_chars=1000)}
"""


def create_openai_paper_summary(pdf_path: str) -> PaperSummary:
    """
    Create a structured paper summary using an OpenAI chat model.

    This is planned for OpenAI-powered mode.
    It is not used by the fallback mode yet.
    """
    evidence = build_summary_evidence(pdf_path)

    model = get_chat_model()
    structured_model = model.with_structured_output(PaperSummary)

    prompt = f"""
You are ResearchMate, an assistant for academic literature review.

Create a concise structured summary of the research paper using only the evidence below.

Rules:
- Be faithful to the evidence.
- Do not invent datasets, metrics, or limitations.
- If something is unclear, say "Not clearly stated in the provided evidence."
- Keep each field concise but useful for a literature-review comparison table.
- The field relation_to_my_topic should explain relevance to table retrieval,
  structured evidence retrieval, table search, table summarization, or table QA.

Evidence:
{evidence}
"""

    summary = structured_model.invoke(prompt)

    return summary.model_copy(
        update={
            "source_file": pdf_path,
        }
    )