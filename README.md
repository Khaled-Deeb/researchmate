# ResearchMate

**ResearchMate** is an agentic literature-review assistant for research papers.

The project helps a researcher load papers, search inside them, create structured paper summaries, approve summaries before saving, and export a comparison table across papers.

The project is built as a practical LangChain/LangGraph mini-project and is designed around a real research workflow, not a toy chatbot.

---

## Why this project

Reading research papers for a literature review usually requires repeatedly extracting the same information:

- What problem does the paper solve?
- What method does it propose?
- What datasets or benchmarks are used?
- What metrics are reported?
- What are the main results?
- What are the limitations?
- How is the paper related to my research topic?

ResearchMate automates part of this workflow while keeping the researcher in control through a human approval step.

---

## Current status

The current version works in **fallback mode**, without requiring an OpenAI API key.

Implemented:

- PDF loading
- text chunking
- keyword-based paper search
- structured paper-summary schema
- human approval before saving summaries
- saved paper cards as JSON
- comparison table export to Markdown and CSV
- LangChain tools
- LangGraph routing workflow
- simple extractive question answering over the current paper

Planned:

- OpenAI-powered structured extraction
- embedding-based semantic search
- LLM-generated answers grounded in retrieved chunks
- Agent Chat UI integration

---

## Tech stack

- Python
- LangChain
- LangGraph
- Pydantic
- PyPDF
- uv

---

## Project structure

```text
researchmate/
├── app/
│   ├── agent.py          # temporary rule-based assistant/router
│   ├── compare.py        # comparison table creation/export
│   ├── config.py         # environment/config settings
│   ├── graph.py          # LangGraph workflow
│   ├── ingest.py         # PDF loading and chunking
│   ├── review.py         # human approval/edit/reject workflow
│   ├── schemas.py        # structured paper-summary schema
│   ├── storage.py        # save/load approved summaries
│   └── tools.py          # LangChain tools
├── data/
│   ├── papers/           # local PDFs, not committed
│   ├── summaries/        # generated summaries, not committed
│   └── exports/          # generated tables, not committed
├── main.py               # CLI entry point
├── pyproject.toml
├── .env.example
└── README.md