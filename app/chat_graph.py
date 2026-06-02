from typing import Annotated, Any

from langchain_core.messages import AIMessage, AnyMessage
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict

from app.compare import create_markdown_comparison_table
from app.openai_qa import answer_paper_question_openai
from app.openai_summarizer import create_openai_paper_summary


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


def format_summary(summary: Any) -> str:
    """
    Format a PaperSummary object for chat display.
    """
    return (
        "OPENAI STRUCTURED PAPER SUMMARY\n\n"
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

    This is intentionally simple:
    - summarize -> OpenAI structured summary for the default paper
    - compare -> comparison table from approved summaries
    - otherwise -> OpenAI grounded Q&A over the default paper
    """
    user_message = get_last_user_message(state["messages"])
    lowered = user_message.lower()

    try:
        if "compare" in lowered or "comparison" in lowered:
            answer = create_markdown_comparison_table()

        elif "summarize" in lowered or "summary" in lowered:
            summary = create_openai_paper_summary(DEFAULT_PDF_PATH)
            answer = format_summary(summary)

        else:
            answer = answer_paper_question_openai(
                query=user_message,
                pdf_path=DEFAULT_PDF_PATH,
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