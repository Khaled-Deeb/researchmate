# ResearchMate Demo Commands

This file contains simple commands for demonstrating the current fallback version of ResearchMate.

The current version does **not** require an OpenAI API key.

---

## 1. Prepare local papers

Put PDFs inside:

```text
data/papers/
```

Example local files:

```text
data/papers/sample.pdf
data/papers/paper2.pdf
```

These PDFs are ignored by Git and should not be committed.

---

## 2. Search inside a paper

```powershell
uv run python main.py search "structured table summarization"
```

Expected behavior:

- loads `data/papers/sample.pdf`
- splits the PDF into chunks
- returns relevant passages

---

## 3. Ask through LangGraph

```powershell
uv run python main.py graph-ask "What is the structured table summarization problem?"
```

Expected behavior:

- routes the message through LangGraph
- selects the `answer` node
- retrieves evidence from the paper
- returns a temporary extractive answer

---

## 4. Find evidence

```powershell
uv run python main.py graph-ask "Find passages about information loss"
```

Expected behavior:

- selects the `search` node
- returns raw evidence chunks

---

## 5. Summarize a paper with human review

```powershell
uv run python main.py summarize data/papers/sample.pdf
```

The assistant shows a structured paper card and asks:

```text
Choose an action: [a]pprove, [e]dit, [r]eject:
```

Use:

```text
a
```

to approve and save.

Use:

```text
e
```

to edit one field before saving.

Use:

```text
r
```

to reject and save nothing.

---

## 6. Summarize a second paper

```powershell
uv run python main.py summarize data/papers/paper2.pdf
```

Approve the summary after editing any weak fields.

---

## 7. Compare approved papers

```powershell
uv run python main.py compare
```

Expected output:

- Markdown comparison table in the terminal
- exported Markdown file
- exported CSV file

Generated files:

```text
data/exports/paper_comparison.md
data/exports/paper_comparison.csv
```

These files are ignored by Git.

---

## 8. Ask for comparison through LangGraph

```powershell
uv run python main.py graph-ask "Compare all saved papers"
```

Expected behavior:

- selects the `compare` node
- returns a literature comparison table

---

## 9. Export through LangGraph

```powershell
uv run python main.py graph-ask "Export the comparison table to CSV"
```

Expected behavior:

- selects the `export` node
- saves Markdown and CSV comparison files

---

## Good interview demo order

Use this order in a live demo:

```powershell
uv run python main.py graph-ask "What is the structured table summarization problem?"
uv run python main.py summarize data/papers/sample.pdf
uv run python main.py summarize data/papers/paper2.pdf
uv run python main.py compare
uv run python main.py graph-ask "Export the comparison table to CSV"
```

---

## Current limitation

The current fallback mode uses:

- keyword-based retrieval
- rule-based rough summary extraction
- extractive answering

The project is prepared for future OpenAI-powered mode with:

- semantic vector search
- LLM structured paper-card extraction
- LLM grounded answers
- LLM tool-routing