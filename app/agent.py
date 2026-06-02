from app.tools import (
    answer_current_paper_question,
    compare_saved_papers,
    export_comparison_table,
    search_current_paper,
    summarize_current_paper,
)


def choose_tool(user_message: str) -> str:
    """
    Choose which tool to call.

    This is a temporary rule-based router.
    Later, an LLM agent will choose tools automatically.
    """
    message = user_message.lower()

    export_keywords = [
        "export",
        "save table",
        "save comparison",
        "csv",
        "markdown",
        "create file",
        "generate file",
    ]

    comparison_keywords = [
        "compare all",
        "compare saved",
        "comparison table",
        "literature table",
        "all saved papers",
        "all papers",
        "saved papers",
    ]

    summary_keywords = [
        "summarize the paper",
        "summary of the paper",
        "paper summary",
        "paper card",
        "extract summary",
        "extract paper card",
        "structured summary",
        "give me the summary",
    ]

    search_keywords = [
        "find",
        "passages",
        "evidence",
        "where does",
        "show me",
        "quote",
    ]

    answer_keywords = [
        "what is",
        "what are",
        "define",
        "explain",
        "meaning",
        "why",
        "how",
        "according to the paper",
        "in the paper",
    ]

    if any(keyword in message for keyword in export_keywords):
        return "export"

    if any(keyword in message for keyword in comparison_keywords):
        return "compare"

    if any(keyword in message for keyword in summary_keywords):
        return "summarize"

    if any(keyword in message for keyword in search_keywords):
        return "search"

    if any(keyword in message for keyword in answer_keywords):
        return "answer"

    return "answer"


def ask_researchmate(user_message: str) -> str:
    """
    Answer a user message by selecting and calling one of the available tools.

    This is not an LLM agent yet.
    It is a simple tool-based assistant that prepares the project structure
    for a real LangChain/LangGraph agent later.
    """
    selected_tool = choose_tool(user_message)

    if selected_tool == "export":
        tool_result = export_comparison_table.invoke({})
        return (
            "Selected tool: export_comparison_table\n\n"
            f"{tool_result}"
        )

    if selected_tool == "compare":
        tool_result = compare_saved_papers.invoke({})
        return (
            "Selected tool: compare_saved_papers\n\n"
            f"{tool_result}"
        )

    if selected_tool == "summarize":
        tool_result = summarize_current_paper.invoke({})
        return (
            "Selected tool: summarize_current_paper\n\n"
            f"{tool_result}"
        )

    if selected_tool == "search":
        tool_result = search_current_paper.invoke({"query": user_message})
        return (
            "Selected tool: search_current_paper\n\n"
            f"{tool_result}"
        )

    tool_result = answer_current_paper_question.invoke({"query": user_message})
    return (
        "Selected tool: answer_current_paper_question\n\n"
        f"{tool_result}"
    )