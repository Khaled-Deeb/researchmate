from typing import Literal, TypedDict

from langgraph.graph import END, START, StateGraph

from app.agent import choose_tool
from app.tools import (
    answer_current_paper_question,
    compare_saved_papers,
    export_comparison_table,
    search_current_paper,
    summarize_current_paper,
)


class ResearchMateState(TypedDict):
    """
    State passed between LangGraph nodes.
    """

    message: str
    selected_tool: str
    result: str


def select_tool_node(state: ResearchMateState) -> dict:
    """
    Decide which tool should handle the user message.

    For now this uses a rule-based router.
    Later we will replace this with an LLM router.
    """
    selected_tool = choose_tool(state["message"])

    return {
        "selected_tool": selected_tool,
    }


def route_after_selection(
    state: ResearchMateState,
) -> Literal["answer", "search", "summarize", "compare", "export"]:
    """
    Tell LangGraph which node to run next.
    """
    return state["selected_tool"]


def answer_node(state: ResearchMateState) -> dict:
    """
    Answer a question about the current paper.
    """
    result = answer_current_paper_question.invoke(
        {
            "query": state["message"],
        }
    )

    return {
        "result": result,
    }


def search_node(state: ResearchMateState) -> dict:
    """
    Search inside the current paper.
    """
    result = search_current_paper.invoke(
        {
            "query": state["message"],
        }
    )

    return {
        "result": result,
    }


def summarize_node(state: ResearchMateState) -> dict:
    """
    Summarize the current paper.
    """
    result = summarize_current_paper.invoke({})

    return {
        "result": result,
    }


def compare_node(state: ResearchMateState) -> dict:
    """
    Compare approved saved paper summaries.
    """
    result = compare_saved_papers.invoke({})

    return {
        "result": result,
    }


def export_node(state: ResearchMateState) -> dict:
    """
    Export approved summaries as Markdown and CSV.
    """
    result = export_comparison_table.invoke({})

    return {
        "result": result,
    }


def build_researchmate_graph():
    """
    Build and compile the ResearchMate LangGraph workflow.
    """
    graph_builder = StateGraph(ResearchMateState)

    graph_builder.add_node("select_tool", select_tool_node)
    graph_builder.add_node("answer", answer_node)
    graph_builder.add_node("search", search_node)
    graph_builder.add_node("summarize", summarize_node)
    graph_builder.add_node("compare", compare_node)
    graph_builder.add_node("export", export_node)

    graph_builder.add_edge(START, "select_tool")

    graph_builder.add_conditional_edges(
        "select_tool",
        route_after_selection,
        {
            "answer": "answer",
            "search": "search",
            "summarize": "summarize",
            "compare": "compare",
            "export": "export",
        },
    )

    graph_builder.add_edge("answer", END)
    graph_builder.add_edge("search", END)
    graph_builder.add_edge("summarize", END)
    graph_builder.add_edge("compare", END)
    graph_builder.add_edge("export", END)

    return graph_builder.compile()


researchmate_graph = build_researchmate_graph()


def ask_researchmate_graph(message: str) -> str:
    """
    Ask ResearchMate through the LangGraph workflow.
    """
    final_state = researchmate_graph.invoke(
        {
            "message": message,
            "selected_tool": "",
            "result": "",
        }
    )

    return (
        f"Selected tool: {final_state['selected_tool']}\n\n"
        f"{final_state['result']}"
    )