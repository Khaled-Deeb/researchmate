from pathlib import Path

from app.openai_summarizer import create_openai_paper_summary
from app.schemas import PaperSummary


PAPERS_DIR = Path("data/papers")


def shorten(text: str, max_chars: int = 160) -> str:
    """
    Shorten long text for Markdown table display.
    """
    text = " ".join(text.split())

    if len(text) <= max_chars:
        return text

    return text[: max_chars - 3] + "..."


def get_pdf_files(papers_dir: Path = PAPERS_DIR) -> list[Path]:
    """
    Return all PDFs in the papers directory.
    """
    if not papers_dir.exists():
        return []

    return sorted(
        papers_dir.glob("*.pdf"),
        key=lambda path: path.name.lower(),
    )


def create_markdown_table_from_summaries(
    summaries: list[PaperSummary],
) -> str:
    """
    Create a Markdown comparison table from in-memory summaries.
    """
    if not summaries:
        return "No summaries available for comparison."

    headers = [
        "Source",
        "Title",
        "Problem",
        "Method",
        "Dataset",
        "Metrics",
        "Main Results",
        "Limitations",
        "Relation to Topic",
    ]

    rows = []

    for summary in summaries:
        rows.append(
            [
                shorten(summary.source_file, 60),
                shorten(summary.title, 80),
                shorten(summary.problem),
                shorten(summary.method),
                shorten(summary.dataset),
                shorten(summary.metrics),
                shorten(summary.main_results),
                shorten(summary.limitations),
                shorten(summary.relation_to_my_topic),
            ]
        )

    table_lines = []

    table_lines.append("| " + " | ".join(headers) + " |")
    table_lines.append("| " + " | ".join(["---"] * len(headers)) + " |")

    for row in rows:
        table_lines.append("| " + " | ".join(row) + " |")

    return "\n".join(table_lines)


def create_quick_comparison_from_pdfs(
    max_papers: int = 5,
) -> str:
    """
    Create a temporary OpenAI-powered comparison table directly from PDFs.

    This does not save summaries.
    For permanent summaries, use summarize-openai and approve the result.
    """
    pdf_files = get_pdf_files()

    if not pdf_files:
        return "No PDF files found in data/papers/."

    selected_files = pdf_files[:max_papers]
    summaries = []

    for pdf_path in selected_files:
        summary = create_openai_paper_summary(str(pdf_path))
        summaries.append(summary)

    table = create_markdown_table_from_summaries(summaries)

    note = (
        "QUICK OPENAI COMPARISON\n\n"
        "This comparison was generated directly from PDFs and was not saved.\n"
        "For a permanent literature table, use summarize-openai and approve each summary.\n\n"
    )

    return note + table