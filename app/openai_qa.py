from app.llm import get_chat_model
from app.summarizer import clean_text
from app.vector_store import semantic_search_pdf


DEFAULT_PDF_PATH = "data/papers/sample.pdf"


def answer_paper_question_openai(
    query: str,
    pdf_path: str = DEFAULT_PDF_PATH,
    top_k: int = 4,
) -> str:
    """
    Answer a question about a paper using semantic retrieval
    and an OpenAI-compatible chat model.

    This is a grounded answer:
    - first retrieve semantically relevant chunks
    - then ask the LLM to answer only from those chunks
    """
    documents = semantic_search_pdf(
        pdf_path=pdf_path,
        query=query,
        k=top_k,
    )

    if not documents:
        return "I could not find relevant evidence in the selected paper."

    evidence_blocks = []

    for index, document in enumerate(documents, start=1):
        page = document.metadata.get("page", "unknown")
        text = clean_text(document.page_content, max_chars=1500)

        evidence_blocks.append(
            f"Evidence {index}\n"
            f"Page: {page}\n"
            f"Text:\n{text}"
        )

    evidence = "\n\n" + ("=" * 80) + "\n\n"
    evidence = evidence.join(evidence_blocks)

    prompt = f"""
You are ResearchMate, an academic literature-review assistant.

Answer the user's question using only the evidence below.

Rules:
- Be concise.
- Do not invent information.
- If the evidence is insufficient, say that the paper evidence is insufficient.
- Mention the page numbers used as evidence.
- Distinguish between limitations of the proposed method and limitations of previous related work.
- Use clear academic language.

User question:
{query}

Evidence:
{evidence}
"""

    model = get_chat_model()
    response = model.invoke(prompt)

    return (
        "OPENAI GROUNDED ANSWER\n\n"
        f"Question:\n{query}\n\n"
        f"Answer:\n{response.content}\n\n"
        f"{'=' * 80}\n\n"
        f"Retrieved evidence:\n{evidence}"
    )