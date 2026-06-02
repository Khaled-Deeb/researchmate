from pathlib import Path
from typing import Annotated, Any

from langchain_core.messages import AIMessage, AnyMessage
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from pypdf import PdfReader
from typing_extensions import TypedDict

from app.compare import create_markdown_comparison_table
from app.openai_qa import answer_paper_question_openai
from app.openai_summarizer import create_openai_paper_summary
from app.summarizer import extract_title_from_first_page


PAPERS_DIR = Path("data/papers")
DEFAULT_PDF_PATH = "data/papers/sample.pdf"


class ChatState(TypedDict):
    """
    State for Agent Chat UI.

    Agent Chat UI expects a graph state with a 'messages' key.
    """

    messages: Annotated[list[AnyMessage], add_messages]


def get_last_user_message(messages: list[AnyMessage]) -> str:
    """
    Extract the latest user message text from the message history.
    """
    for message in reversed(messages):
        if message.type == "human":
            content = message.content

            if isinstance(content, str):
                return content

            if isinstance(content, list):
                parts = []

                for item in content:
                    if isinstance(item, dict) and item.get("type") == "text":
                        parts.append(item.get("text", ""))

                return "\n".join(parts)

    return ""


def get_pdf_files() -> list[Path]:
    """
    Return all local PDF files available for the demo.

    sample.pdf is placed first if it exists, so the demo remains stable:
    paper1 -> sample.pdf
    paper2 -> the next PDF
    """
    if not PAPERS_DIR.exists():
        return []

    pdf_files = sorted(
        PAPERS_DIR.glob("*.pdf"),
        key=lambda path: (
            path.name.lower() != "sample.pdf",
            path.name.lower(),
        ),
    )

    return pdf_files


def extract_pdf_title(pdf_path: Path) -> str:
    """
    Extract a rough title from the first page of a PDF.

    This is only for paper selection/listing in the chat UI.
    The real structured summary still uses the summarizer.
    """
    try:
        reader = PdfReader(str(pdf_path))

        if not reader.pages:
            return pdf_path.stem

        first_page_text = reader.pages[0].extract_text() or ""
        title = extract_title_from_first_page(first_page_text)

        if title and title != "Unknown title":
            return title

        return pdf_path.stem

    except Exception:
        return pdf_path.stem


def normalize_text(text: str) -> str:
    """
    Normalize text for simple matching.
    """
    return " ".join(text.lower().replace("_", " ").replace("-", " ").split())


def get_paper_catalog() -> list[dict[str, Any]]:
    """
    Build a small catalog of available local PDFs.

    Each item has:
    - index: paper number shown to the user
    - path: local PDF path
    - title: rough extracted title
    - aliases: simple keywords for selection
    """
    catalog = []

    for index, pdf_path in enumerate(get_pdf_files(), start=1):
        title = extract_pdf_title(pdf_path)

        aliases = [
            f"paper{index}",
            f"paper {index}",
            pdf_path.stem,
            normalize_text(pdf_path.stem),
            normalize_text(title),
        ]

        catalog.append(
            {
                "index": index,
                "path": pdf_path,
                "title": title,
                "aliases": aliases,
            }
        )

    return catalog


def choose_pdf_path(user_message: str) -> str:
    """
    Choose a local PDF based on simple keywords in the user message.

    Examples:
    - "paper1"
    - "paper 2"
    - "COTER"
    - "sample"
    - part of the title
    """
    lowered = normalize_text(user_message)
    catalog = get_paper_catalog()

    for paper in catalog:
        for alias in paper["aliases"]:
            normalized_alias = normalize_text(alias)

            if normalized_alias and normalized_alias in lowered:
                return str(paper["path"])

    default_path = Path(DEFAULT_PDF_PATH)

    if default_path.exists():
        return DEFAULT_PDF_PATH

    if catalog:
        return str(catalog[0]["path"])

    return DEFAULT_PDF_PATH


def list_available_papers() -> str:
    """
    Show available local demo papers.
    """
    catalog = get_paper_catalog()

    if not catalog:
        return (
            "No PDF files were found.\n\n"
            "Put PDF files inside data/papers/ and ask again."
        )

    lines = [
        "Available local demo papers:",
        "",
    ]

    for paper in catalog:
        lines.append(
            f"- paper{paper['index']} -> {paper['path']} | {paper['title']}"
        )

    lines.extend(
        [
            "",
            "Examples:",
            '- "Summarize paper1"',
            '- "What is the main limitation of paper2?"',
            '- "Ask about COTER: what is the main method?"',
        ]
    )

    return "\n".join(lines)


def format_summary(summary: Any, pdf_path: str) -> str:
    """
    Format a PaperSummary object for chat display.
    """
    return (
        "OPENAI STRUCTURED PAPER SUMMARY\n\n"
        f"Source file:\n{pdf_path}\n\n"
        f"Title:\n{summary.title}\n\n"
        f"Problem:\n{summary.problem}\n\n"
        f"Method:\n{summary.method}\n\n"
        f"Dataset:\n{summary.dataset}\n\n"
        f"Metrics:\n{summary.metrics}\n\n"
        f"Main results:\n{summary.main_results}\n\n"
        f"Limitations:\n{summary.limitations}\n\n"
        f"Relation to my topic:\n{summary.relation_to_my_topic}\n\n"
        "Note: This chat summary is not automatically saved. "
        "Use the CLI command summarize-openai for human review and saving."
    )


def chat_node(state: ChatState) -> dict:
    """
    Main chat node for ResearchMate.

    Demo behavior:
    - list papers -> show available local PDFs
    - compare -> comparison table from approved summaries
    - summarize -> OpenAI structured summary for selected/default paper
    - otherwise -> OpenAI grounded Q&A over selected/default paper
    """
    user_message = get_last_user_message(state["messages"])
    lowered = user_message.lower()
    pdf_path = choose_pdf_path(user_message)

    try:
        if "list papers" in lowered or "available papers" in lowered:
            answer = list_available_papers()

        elif "compare" in lowered or "comparison" in lowered:
            answer = create_markdown_comparison_table()

        elif "summarize" in lowered or "summary" in lowered:
            if not Path(pdf_path).exists():
                answer = f"PDF file not found: {pdf_path}"
            else:
                summary = create_openai_paper_summary(pdf_path)
                answer = format_summary(summary, pdf_path)

        else:
            if not Path(pdf_path).exists():
                answer = f"PDF file not found: {pdf_path}"
            else:
                answer = answer_paper_question_openai(
                    query=user_message,
                    pdf_path=pdf_path,
                )

    except Exception as error:
        answer = (
            "ResearchMate encountered an error while handling the request.\n\n"
            f"Error type: {type(error).__name__}\n"
            f"Error message: {error}"
        )

    return {
        "messages": [
            AIMessage(content=answer),
        ]
    }


graph_builder = StateGraph(ChatState)

graph_builder.add_node("chat", chat_node)
graph_builder.add_edge(START, "chat")
graph_builder.add_edge("chat", END)

graph = graph_builder.compile()