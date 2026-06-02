import json
import re
from datetime import datetime
from pathlib import Path

from app.schemas import PaperSummary


SUMMARY_DIR = Path("data/summaries")


def make_safe_filename(title: str) -> str:
    """
    Convert a paper title into a safe filename.
    """
    filename = title.lower()
    filename = re.sub(r"[^a-z0-9]+", "_", filename)
    filename = filename.strip("_")

    if not filename:
        filename = "paper_summary"

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    return f"{filename}_{timestamp}.json"


def save_summary(summary: PaperSummary) -> Path:
    """
    Save an approved paper summary as a JSON file.
    """
    SUMMARY_DIR.mkdir(parents=True, exist_ok=True)

    filename = make_safe_filename(summary.title)
    output_path = SUMMARY_DIR / filename

    with output_path.open("w", encoding="utf-8") as file:
        json.dump(summary.model_dump(), file, ensure_ascii=False, indent=2)

    return output_path


def load_all_summaries() -> list[PaperSummary]:
    """
    Load all saved paper summaries.
    """
    summaries = []

    if not SUMMARY_DIR.exists():
        return summaries

    for path in SUMMARY_DIR.glob("*.json"):
        with path.open("r", encoding="utf-8") as file:
            data = json.load(file)
            summaries.append(PaperSummary(**data))

    return summaries