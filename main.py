import argparse

from app.agent import ask_researchmate
from app.compare import (
    create_markdown_comparison_table,
    save_csv_comparison_table,
    save_markdown_comparison_table,
)
from app.config import settings
from app.graph import ask_researchmate_graph
from app.review import review_summary
from app.storage import save_summary
from app.summarizer import create_rough_paper_summary
from app.openai_summarizer import create_openai_paper_summary
from app.tools import search_paper_text


def run_summarize(pdf_path: str) -> None:
    """
    Create a rough summary, ask for human approval, then save it.
    """
    summary = create_rough_paper_summary(pdf_path)

    approved_summary = review_summary(summary)

    if approved_summary is None:
        print("\nSummary rejected. Nothing was saved.")
        return

    output_path = save_summary(approved_summary)

    print("\nSummary approved and saved.")
    print(f"Saved to: {output_path}")

def run_summarize_openai(pdf_path: str) -> None:
    """
    Create an OpenAI-powered structured summary, ask for human approval,
    then save it.
    """
    summary = create_openai_paper_summary(pdf_path)

    approved_summary = review_summary(summary)

    if approved_summary is None:
        print("\nSummary rejected. Nothing was saved.")
        return

    output_path = save_summary(approved_summary)

    print("\nOpenAI summary approved and saved.")
    print(f"Saved to: {output_path}")


def run_compare() -> None:
    """
    Create and export a comparison table from approved summaries.
    """
    table = create_markdown_comparison_table()

    print("=" * 80)
    print("PAPER COMPARISON TABLE")
    print("=" * 80)
    print(table)

    markdown_path = save_markdown_comparison_table()
    csv_path = save_csv_comparison_table()

    print("\n" + "=" * 80)
    print("Export complete")
    print("=" * 80)
    print(f"Markdown saved to: {markdown_path}")
    print(f"CSV saved to: {csv_path}")


def run_search(pdf_path: str, query: str) -> None:
    """
    Search inside a PDF.
    """
    result = search_paper_text(query=query, pdf_path=pdf_path)

    print("=" * 80)
    print("PAPER SEARCH")
    print("=" * 80)
    print(f"PDF: {pdf_path}")
    print(f"Query: {query}")
    print(result)


def run_ask(message: str) -> None:
    """
    Ask the simple tool-based ResearchMate assistant.
    """
    result = ask_researchmate(message)

    print("=" * 80)
    print("RESEARCHMATE ASSISTANT")
    print("=" * 80)
    print(f"User message: {message}")
    print("=" * 80)
    print(result)


def run_graph_ask(message: str) -> None:
    """
    Ask ResearchMate through the LangGraph workflow.
    """
    result = ask_researchmate_graph(message)

    print("=" * 80)
    print("RESEARCHMATE LANGGRAPH ASSISTANT")
    print("=" * 80)
    print(f"User message: {message}")
    print("=" * 80)
    print(result)


def run_openai_check() -> None:
    """
    Check whether OpenAI-powered mode is configured.

    This does not call the API.
    """
    print("=" * 80)
    print("OPENAI CONFIG CHECK")
    print("=" * 80)
    print(f"RESEARCHMATE_MODE: {settings.mode}")
    print(f"OPENAI_MODEL: {settings.openai_model}")
    print(f"OPENAI_EMBEDDING_MODEL: {settings.openai_embedding_model}")
    print(f"OPENAI_API_KEY present: {bool(settings.openai_api_key)}")
    print(f"OpenAI mode active: {settings.use_openai}")

    if settings.use_openai:
        print("\nOpenAI-powered mode is configured.")
    else:
        print(
            "\nFallback mode is active. "
            "This is expected if you have not added an API key yet."
        )


def main():
    parser = argparse.ArgumentParser(
        description="ResearchMate: Agentic literature review assistant"
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    summarize_parser = subparsers.add_parser(
        "summarize",
        help="Create, review, and save a structured summary for a PDF",
    )
    summarize_parser.add_argument(
        "pdf_path",
        help="Path to the PDF file",
    )

    summarize_openai_parser = subparsers.add_parser(
        "summarize-openai",
        help="Create, review, and save an OpenAI-powered structured summary for a PDF",
    )
    summarize_openai_parser.add_argument(
        "pdf_path",
        help="Path to the PDF file",
    )

    subparsers.add_parser(
        "compare",
        help="Create a comparison table from approved summaries",
    )

    search_parser = subparsers.add_parser(
        "search",
        help="Search inside a PDF",
    )
    search_parser.add_argument(
        "query",
        help="Search query",
    )
    search_parser.add_argument(
        "--pdf",
        default="data/papers/sample.pdf",
        help="Path to the PDF file. Default: data/papers/sample.pdf",
    )

    ask_parser = subparsers.add_parser(
        "ask",
        help="Ask the simple ResearchMate assistant",
    )
    ask_parser.add_argument(
        "message",
        help="Message/question for ResearchMate",
    )

    graph_ask_parser = subparsers.add_parser(
        "graph-ask",
        help="Ask the LangGraph ResearchMate assistant",
    )
    graph_ask_parser.add_argument(
        "message",
        help="Message/question for ResearchMate",
    )

    subparsers.add_parser(
        "openai-check",
        help="Check whether OpenAI-powered mode is configured",
    )

    args = parser.parse_args()

    if args.command == "summarize":
        run_summarize(args.pdf_path)
    
    elif args.command == "summarize-openai":
        run_summarize_openai(args.pdf_path)

    elif args.command == "compare":
        run_compare()

    elif args.command == "search":
        run_search(pdf_path=args.pdf, query=args.query)

    elif args.command == "ask":
        run_ask(args.message)

    elif args.command == "graph-ask":
        run_graph_ask(args.message)

    elif args.command == "openai-check":
        run_openai_check()


if __name__ == "__main__":
    main()