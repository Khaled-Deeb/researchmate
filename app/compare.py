import csv
from pathlib import Path

from app.storage import load_all_summaries


EXPORT_DIR = Path("data/exports")


def shorten(text: str, max_chars: int = 120) -> str:
    """
    Shorten long text for table display.
    """
    text = " ".join(text.split())

    if len(text) <= max_chars:
        return text

    return text[: max_chars - 3] + "..."


def create_markdown_comparison_table() -> str:
    """
    Create a Markdown comparison table from all approved summaries.
    """
    summaries = load_all_summaries()

    if not summaries:
        return "No approved summaries found."

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


def save_markdown_comparison_table() -> Path:
    """
    Save the Markdown comparison table.
    """
    EXPORT_DIR.mkdir(parents=True, exist_ok=True)

    output_path = EXPORT_DIR / "paper_comparison.md"
    table = create_markdown_comparison_table()

    with output_path.open("w", encoding="utf-8") as file:
        file.write(table)

    return output_path


def save_csv_comparison_table() -> Path:
    """
    Save the comparison table as CSV.
    """
    EXPORT_DIR.mkdir(parents=True, exist_ok=True)

    summaries = load_all_summaries()
    output_path = EXPORT_DIR / "paper_comparison.csv"

    headers = [
        "source_file",
        "title",
        "problem",
        "method",
        "dataset",
        "metrics",
        "main_results",
        "limitations",
        "relation_to_my_topic",
    ]

    with output_path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=headers)
        writer.writeheader()

        for summary in summaries:
            writer.writerow(summary.model_dump())

    return output_path