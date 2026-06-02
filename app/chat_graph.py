from pathlib import Path
from typing import Annotated, Any

from langchain_core.messages import AIMessage, AnyMessage
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict

from app.compare import create_markdown_comparison_table
from app.openai_qa import answer_paper_question_openai
from app.openai_summarizer import create_openai_paper_summary


DEFAULT_PDF_PATH = "data/papers/sample.pdf"

AVAILABLE_PAPERS = {
    "sample": "data/papers/sample.pdf",
    "paper1": "data/papers/sample.pdf",
    "web table": "data/papers/sample.pdf",
    "web table search": "data/papers/sample.pdf",
    "result selection": "data/papers/sample.pdf",
    "paper2": "data/papers/paper2.pdf",
    "coter": "data/papers/paper2.pdf",
    "conditional optimal transport": "data/papers/paper2.pdf",
}


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


def choose_pdf_path(user_message: str) -> str:
    """
    Choose a local PDF based on simple keywords in the user message.

    This is intentionally simple for the demo.
    Later, the UI can support real file upload or paper selection.
    """
    lowered = user_message.lower()

    for keyword, pdf_path in AVAILABLE_PAPERS.items():
        if keyword in lowered:
            return pdf_path

    return DEFAULT_PDF_PATH


def list_available_papers() -> str:
    """
    Show available local demo papers.
    """
    lines = [
        "Available local demo papers:",
        "",
        "- paper1 / sample / web table search -> data/papers/sample.pdf",
        "- paper2 / COTER -> data/papers/paper2.pdf",
        "",
        "Examples:",
        '- "Ask about COTER: what is the method?"',
        '- "Summarize paper2"',
        '- "What is the main limitation of paper1?"',
    ]

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
    - list papers -> show available local demo papers
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