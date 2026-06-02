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
- demo command guide
- OpenAI-ready configuration scaffold
- inactive OpenAI summarizer scaffold
- inactive semantic vector-search scaffold

Planned:

- OpenAI-powered structured extraction
- embedding-based semantic search
- LLM-generated answers grounded in retrieved chunks
- LLM-based tool routing
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
│   ├── agent.py              # temporary rule-based assistant/router
│   ├── compare.py            # comparison table creation/export
│   ├── config.py             # environment/config settings
│   ├── graph.py              # LangGraph workflow
│   ├── ingest.py             # PDF loading and chunking
│   ├── llm.py                # OpenAI model factory scaffold, inactive in fallback mode
│   ├── openai_summarizer.py  # OpenAI structured summarizer scaffold, inactive for now
│   ├── review.py             # human approval/edit/reject workflow
│   ├── schemas.py            # structured paper-summary schema
│   ├── storage.py            # save/load approved summaries
│   ├── tools.py              # LangChain tools
│   └── vector_store.py       # semantic vector-search scaffold, inactive for now
├── data/
│   ├── papers/               # local PDFs, not committed
│   ├── summaries/            # generated summaries, not committed
│   └── exports/              # generated tables, not committed
├── demo_commands.md          # ready-to-use demo commands
├── main.py                   # CLI entry point
├── pyproject.toml
├── .env.example
└── README.md
```

---

## Setup

### 1. Clone the repository

```powershell
git clone <your-repo-url>
cd researchmate
```

### 2. Create the environment

```powershell
uv sync
```

### 3. Create `.env`

Copy the example file:

```powershell
Copy-Item .env.example .env
```

For fallback mode, no API key is needed:

```env
OPENAI_API_KEY=
OPENAI_MODEL=gpt-4o-mini
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
RESEARCHMATE_MODE=fallback
```

---

## Usage

Put PDF files inside:

```text
data/papers/
```

Example:

```text
data/papers/sample.pdf
data/papers/paper2.pdf
```

These local PDFs are ignored by Git.

---

## Search inside a paper

```powershell
uv run python main.py search "structured table summarization"
```

This loads the default paper, chunks it, and returns relevant passages.

---

## Ask through the LangGraph workflow

```powershell
uv run python main.py graph-ask "What is the structured table summarization problem?"
```

The current fallback workflow does this:

```text
User question
→ LangGraph select_tool node
→ answer/search/summarize/compare/export node
→ final result
```

---

## Summarize a paper with human review

```powershell
uv run python main.py summarize data/papers/sample.pdf
```

The assistant shows a structured paper card and asks:

```text
Choose an action: [a]pprove, [e]dit, [r]eject:
```

Only approved summaries are saved.

---

## Compare approved papers

```powershell
uv run python main.py compare
```

This exports:

```text
data/exports/paper_comparison.md
data/exports/paper_comparison.csv
```

Generated summaries and exports are ignored by Git.

---

## Demo commands

A separate file, `demo_commands.md`, contains a ready-to-use demo script for showing the project in an interview.

Example commands:

```powershell
uv run python main.py graph-ask "What is the structured table summarization problem?"
uv run python main.py summarize data/papers/sample.pdf
uv run python main.py summarize data/papers/paper2.pdf
uv run python main.py compare
uv run python main.py openai-check
```

The current version runs in fallback mode and does not require an OpenAI API key.

---

## OpenAI config check

The project includes a safe config check command:

```powershell
uv run python main.py openai-check
```

This command does **not** call the OpenAI API. It only checks whether OpenAI mode is configured.

Example fallback output:

```text
RESEARCHMATE_MODE: fallback
OPENAI_API_KEY present: False
OpenAI mode active: False
```

---

## LangChain usage

The project currently uses LangChain for:

- PDF loading via `PyPDFLoader`
- text splitting via `RecursiveCharacterTextSplitter`
- tool wrapping via `@tool`

The tools include:

- `search_current_paper`
- `answer_current_paper_question`
- `summarize_current_paper`
- `compare_saved_papers`
- `export_comparison_table`

---

## LangGraph usage

The project includes a LangGraph workflow:

```text
User message
→ select_tool node
→ answer/search/summarize/compare/export node
→ final result
```

The current router is rule-based so the project can run without an API key.

The graph is designed so that the router node can later be replaced with an LLM-based router.

---

## OpenAI-powered mode

The repository is prepared for future OpenAI-powered mode through:

```text
app/config.py
app/llm.py
app/openai_summarizer.py
app/vector_store.py
.env.example
```

Current fallback components and planned OpenAI upgrades:

| Current fallback component | Future OpenAI component |
| --- | --- |
| keyword search | embedding-based semantic search |
| rule-based rough summary | LLM structured extraction |
| extractive answer | LLM-generated grounded answer |
| rule-based router | LLM tool-calling router |

When OpenAI mode is implemented, the `.env` file will use:

```env
OPENAI_API_KEY=your_real_key_here
RESEARCHMATE_MODE=openai
```

---

## Safety and privacy

The repository does not commit:

- `.env`
- API keys
- local PDFs
- generated summaries
- generated exports

These are excluded through `.gitignore`.

---

## Architecture summary

ResearchMate is built in layers:

1. **Ingestion layer**: loads PDF papers and splits them into chunks.
2. **Tool layer**: exposes paper search, question answering, summarization, comparison, and export as LangChain tools.
3. **Workflow layer**: routes user requests through a LangGraph state machine.
4. **Review layer**: asks for human approval before saving structured paper summaries.
5. **Export layer**: creates Markdown and CSV comparison tables.

The current version runs in fallback mode without an API key. The architecture is prepared for future OpenAI-powered semantic search, structured extraction, and LLM-based routing.
---

## Roadmap

- [x] PDF loading
- [x] text chunking
- [x] LangChain tools
- [x] structured paper-summary schema
- [x] human approval before saving
- [x] comparison table export
- [x] LangGraph workflow
- [x] fallback question answering
- [x] demo command guide
- [x] OpenAI-ready configuration scaffold
- [x] inactive OpenAI summarizer scaffold
- [x] inactive semantic vector-search scaffold
- [ ] OpenAI structured summary extraction
- [ ] embedding-based vector search
- [ ] LLM-generated grounded answers
- [ ] LLM-based tool routing
- [ ] Agent Chat UI integration