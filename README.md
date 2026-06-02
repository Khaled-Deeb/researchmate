# ResearchMate

ResearchMate is an agentic literature-review assistant for research papers.

It helps a researcher load PDF papers, search inside them, ask grounded questions, create structured paper summaries, review summaries before saving, and generate comparison tables across papers.

The project is built as a practical LangChain/LangGraph mini-project around a real literature-review workflow, not a toy chatbot.

---

## Why this project

Reading papers for a literature review usually requires extracting the same information again and again:

- What problem does the paper solve?
- What method does it propose?
- What datasets or benchmarks are used?
- What metrics are reported?
- What are the main results?
- What are the limitations?
- How is the paper related to my research topic?

ResearchMate automates part of this workflow while keeping the researcher in control.

The most important design decision is that permanent summaries are not saved blindly. The user can approve, edit, or reject a generated summary before it becomes part of the saved literature table.

---

## Current status

The current version supports both fallback mode and OpenAI-compatible mode.

Implemented:

- PDF loading
- text chunking
- keyword-based fallback paper search
- structured paper-summary schema with Pydantic
- fallback rough summarization
- OpenAI-compatible structured summarization
- human approval before saving summaries
- saved paper cards as JSON
- comparison table export to Markdown and CSV
- quick OpenAI comparison directly from PDFs
- approved comparison from saved summaries
- fallback extractive question answering
- OpenAI grounded question answering over retrieved evidence
- embedding-based semantic retrieval
- LangChain tools
- LangGraph CLI workflow
- Agent Chat UI compatible LangGraph graph
- automatic local PDF discovery from `data/papers/`
- safe API configuration check

Current limitations:

- PDF files must be placed manually in `data/papers/`.
- Direct browser PDF upload from Agent Chat UI is not implemented yet.
- Chat-generated summaries are not saved automatically.
- Permanent literature tables should still use the human-approved `summarize-openai` workflow.
- The Agent Chat UI demo runs on a local LangGraph server.

---

## Tech stack

- Python
- LangChain
- LangGraph
- Pydantic
- PyPDF
- OpenAI-compatible chat models
- OpenAI-compatible embedding models
- uv
- Agent Chat UI

---

## Project structure

```text
researchmate/
|-- app/
|   |-- agent.py              # fallback tool router
|   |-- chat_graph.py         # Agent Chat UI compatible LangGraph graph
|   |-- compare.py            # saved-summary comparison/export
|   |-- config.py             # environment/config settings
|   |-- graph.py              # CLI LangGraph workflow
|   |-- ingest.py             # PDF loading and chunking
|   |-- llm.py                # OpenAI-compatible model/embedding setup
|   |-- openai_compare.py     # quick comparison directly from PDFs
|   |-- openai_qa.py          # grounded OpenAI paper Q&A
|   |-- openai_summarizer.py  # OpenAI structured summarization
|   |-- review.py             # human approve/edit/reject workflow
|   |-- schemas.py            # PaperSummary schema
|   |-- storage.py            # save/load approved summaries
|   |-- summarizer.py         # fallback rough summarization
|   |-- tools.py              # LangChain tools and fallback search
|   |-- vector_store.py       # semantic retrieval over PDFs
|-- data/
|   |-- papers/               # local PDFs, not committed
|   |-- summaries/            # generated summaries, not committed
|   |-- exports/              # generated tables, not committed
|-- demo_commands.md
|-- langgraph.json
|-- main.py
|-- pyproject.toml
|-- uv.lock
|-- .env.example
|-- .gitignore
|-- .gitattributes
|-- README.md
```

---

## Setup

Prerequisite: install `uv` before running the setup commands.

### 1. Clone the repository

```powershell
git clone https://github.com/Khaled-Deeb/researchmate.git
cd researchmate
```

### 2. Install dependencies

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
OPENAI_BASE_URL=
OPENAI_MODEL=gpt-5.4-nano
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
RESEARCHMATE_MODE=fallback
```

For OpenAI-compatible mode, fill in your local `.env`. The example below uses ProxyAPI as an OpenAI-compatible endpoint:

```env
OPENAI_API_KEY=your_real_key_here
OPENAI_BASE_URL=https://api.proxyapi.ru/openai/v1
OPENAI_MODEL=gpt-5.4-nano
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
RESEARCHMATE_MODE=openai
```

Do not commit `.env`.

---

## Add papers

Put PDF files inside:

```text
data/papers/
```

Example:

```text
data/papers/sample.pdf
data/papers/paper2.pdf
```

These files are ignored by Git.

The Agent Chat UI graph automatically discovers local PDFs from `data/papers/`.

---

## Check configuration

Run:

```powershell
uv run python main.py openai-check
```

This command does not call the API. It only checks whether OpenAI-compatible mode is configured.

Example fallback output:

```text
RESEARCHMATE_MODE: fallback
OPENAI_API_KEY present: False
OpenAI mode active: False
```

Example OpenAI-compatible output:

```text
RESEARCHMATE_MODE: openai
OPENAI_API_KEY present: True
OpenAI mode active: True
```

---

## Fallback CLI usage

### Search inside a paper

```powershell
uv run python main.py search "structured table summarization" --pdf data/papers/sample.pdf
```

This loads a PDF, chunks it, and returns relevant passages using fallback keyword search.

### Ask through the fallback LangGraph workflow

```powershell
uv run python main.py graph-ask "What is the structured table summarization problem?"
```

Fallback workflow:

```text
User question
-> LangGraph select_tool node
-> answer/search/summarize/compare/export node
-> final result
```

### Create a fallback summary with human review

```powershell
uv run python main.py summarize data/papers/sample.pdf
```

The assistant shows a structured paper card and asks:

```text
Choose an action: [a]pprove, [e]dit, [r]eject:
```

Only approved summaries are saved.

---

## OpenAI-compatible CLI usage

### Create an OpenAI-powered structured summary

```powershell
uv run python main.py summarize-openai data/papers/sample.pdf
```

This command:

1. loads the PDF,
2. extracts paper text,
3. uses an OpenAI-compatible model to produce a structured `PaperSummary`,
4. shows the result to the user,
5. asks for approve/edit/reject,
6. saves only approved summaries.

This is the recommended workflow for building a reliable literature-review table.

### Ask an OpenAI-grounded question about a paper

```powershell
uv run python main.py ask-openai "What is the main limitation of this paper?" --pdf data/papers/sample.pdf
```

This command:

1. loads and chunks the PDF,
2. retrieves semantically relevant chunks,
3. asks the model to answer only from the retrieved evidence,
4. prints the final answer and the retrieved evidence.

---

## Compare papers

### Compare approved summaries

```powershell
uv run python main.py compare
```

This uses approved summaries stored in:

```text
data/summaries/
```

It exports:

```text
data/exports/paper_comparison.md
data/exports/paper_comparison.csv
```

Generated summaries and exports are ignored by Git.

### Quick comparison from PDFs

In Agent Chat UI, ask:

```text
Compare papers
```

This creates a temporary OpenAI-powered comparison directly from PDFs in `data/papers/`.

It does not save summaries. For a permanent literature table, use:

```powershell
uv run python main.py summarize-openai data/papers/<paper-name>.pdf
```

and approve each summary.

### Approved comparison from saved summaries

In Agent Chat UI, ask:

```text
Compare saved papers
```

This uses only human-approved summaries saved in `data/summaries/`.

---

## Agent Chat UI

ResearchMate includes a LangGraph graph designed for Agent Chat UI.

Start the local LangGraph server:

```powershell
uv run langgraph dev
```

The server should show something like:

```text
API: http://127.0.0.1:2024
Studio UI: https://smith.langchain.com/studio/?baseUrl=http://127.0.0.1:2024
API Docs: http://127.0.0.1:2024/docs
```

Keep this terminal open while using the chat UI.

Open Agent Chat UI:

```text
https://agentchat.vercel.app
```

Use:

```text
Deployment URL: http://127.0.0.1:2024
Graph ID: researchmate
LangSmith API key: leave empty for local use
```

Example chat messages:

```text
Help
```

```text
List papers
```

```text
Summarize paper1
```

```text
What is the main limitation of paper1?
```

```text
Ask about COTER: what is the main method?
```

```text
Compare papers
```

```text
Compare saved papers
```

Behavior:

```text
Help
-> shows available chat commands

List papers
-> scans data/papers/ and lists available local PDFs

Summarize paper1
-> creates a temporary OpenAI summary in chat, not automatically saved

Question about paper1/paper2/title
-> grounded Q&A over the selected local PDF

Compare papers
-> quick temporary OpenAI comparison directly from PDFs

Compare saved papers
-> comparison from approved summaries in data/summaries/
```

---

## LangChain usage

The project uses LangChain for:

- PDF loading via `PyPDFLoader`
- text splitting via `RecursiveCharacterTextSplitter`
- tool wrapping via `@tool`
- OpenAI-compatible chat models
- OpenAI-compatible embeddings
- structured output with the `PaperSummary` Pydantic schema

Main tools include:

- `search_current_paper`
- `answer_current_paper_question`
- `summarize_current_paper`
- `compare_saved_papers`
- `export_comparison_table`

---

## LangGraph usage

The project contains two LangGraph workflows.

CLI workflow:

```text
User message
-> select_tool node
-> answer/search/summarize/compare/export node
-> final result
```

Agent Chat UI workflow:

```text
User message
-> chat_graph.py
-> help/list/summarize/question-answer/compare routing
-> final assistant message
```

The Agent Chat UI graph uses a `messages` state key so it can connect to the chat frontend.

---

## Safety and privacy

The repository does not commit:

- `.env`
- API keys
- local PDFs
- generated summaries
- generated exports
- generated package metadata such as `*.egg-info/`

These are excluded through `.gitignore`.

---

## Interview explanation

ResearchMate is a literature-review assistant built with LangChain and LangGraph.

It loads local PDF papers, retrieves evidence, answers grounded questions, creates structured paper summaries, and compares papers in a literature-review table. The project has two modes. Fallback mode works without an API key using simple search and rule-based routing. OpenAI-compatible mode adds structured summarization, semantic retrieval, quick comparison, and grounded Q&A.

The key design choice is human approval: permanent summaries are not saved directly after generation. The researcher can approve, edit, or reject them before they enter the final comparison table.

The project also has an Agent Chat UI integration. The UI can list local papers, summarize selected papers, answer grounded questions, and compare either all local PDFs quickly or only approved saved summaries.

---

## Roadmap

- [x] PDF loading
- [x] text chunking
- [x] LangChain tools
- [x] structured paper-summary schema
- [x] human approval before saving
- [x] comparison table export
- [x] fallback question answering
- [x] LangGraph CLI workflow
- [x] OpenAI-compatible configuration
- [x] OpenAI structured summary extraction
- [x] embedding-based semantic retrieval
- [x] OpenAI grounded Q&A
- [x] quick comparison from PDFs
- [x] approved comparison from saved summaries
- [x] Agent Chat UI compatible graph
- [x] automatic local PDF discovery
- [ ] direct browser PDF upload
- [ ] persistent UI-based summary approval
- [ ] deployed hosted version
- [ ] richer paper selection in the UI
