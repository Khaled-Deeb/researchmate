# ResearchMate demo commands

This file contains a simple demo script for showing ResearchMate in an interview.

The demo has three parts:

1. CLI fallback mode
2. OpenAI-compatible CLI mode
3. Agent Chat UI mode

---

## 0. Start from the project root

```powershell
cd C:\Users\Khaled\Desktop\researchmate
```

Check Git status:

```powershell
git status
```

Do not commit:

```text
.env
data/papers/
data/summaries/
data/exports/
researchmate.egg-info/
```

---

## 1. Check configuration

```powershell
uv run python main.py openai-check
```

Expected in OpenAI-compatible mode:

```text
RESEARCHMATE_MODE: openai
OPENAI_API_KEY present: True
OpenAI mode active: True
```

This command does not call the API.

---

## 2. Add local papers

Put PDFs in:

```text
data/papers/
```

Example:

```text
data/papers/sample.pdf
data/papers/paper2.pdf
```

These files are ignored by Git.

---

## 3. Fallback search demo

```powershell
uv run python main.py search "structured table summarization" --pdf data/papers/sample.pdf
```

What to say:

```text
This is the fallback search mode. It loads a PDF, chunks it, and retrieves passages using simple keyword scoring.
```

---

## 4. Fallback LangGraph demo

```powershell
uv run python main.py graph-ask "What is the structured table summarization problem?"
```

What to say:

```text
This command goes through a LangGraph workflow. The current fallback graph uses a rule-based router to choose a tool.
```

---

## 5. OpenAI structured summarization demo

```powershell
uv run python main.py summarize-openai data/papers/sample.pdf
```

When asked:

```text
Choose an action: [a]pprove, [e]dit, [r]eject:
```

Type:

```text
a
```

only if the summary is good.

What to say:

```text
This uses an OpenAI-compatible model to create a structured PaperSummary. The result is not saved automatically. The researcher must approve, edit, or reject it.
```

---

## 6. OpenAI grounded Q&A demo

```powershell
uv run python main.py ask-openai "What is the main limitation of this paper?" --pdf data/papers/sample.pdf
```

What to say:

```text
This is retrieval-augmented question answering. The system retrieves relevant evidence chunks from the PDF and asks the model to answer only from that evidence.
```

---

## 7. Compare approved summaries

```powershell
uv run python main.py compare
```

What to say:

```text
This comparison table is built from human-approved summaries saved in data/summaries/.
```

The command exports:

```text
data/exports/paper_comparison.md
data/exports/paper_comparison.csv
```

---

## 8. Start the LangGraph server

```powershell
uv run langgraph dev
```

Expected output:

```text
API: http://127.0.0.1:2024
Studio UI: https://smith.langchain.com/studio/?baseUrl=http://127.0.0.1:2024
API Docs: http://127.0.0.1:2024/docs
```

Keep this terminal open.

---

## 9. Connect Agent Chat UI

Open:

```text
https://agentchat.vercel.app
```

Use:

```text
Deployment URL: http://127.0.0.1:2024
Graph ID: researchmate
LangSmith API key: leave empty for local use
```

---

## 10. Agent Chat UI demo prompts

Ask:

```text
Help
```

Expected:

```text
ResearchMate shows available chat commands.
```

Ask:

```text
List papers
```

Expected:

```text
ResearchMate lists PDFs from data/papers/.
```

Ask:

```text
What is the main limitation of paper1?
```

Expected:

```text
ResearchMate answers using grounded evidence from paper1.
```

Ask:

```text
Ask about COTER: what is the main method?
```

Expected:

```text
ResearchMate selects the COTER paper and answers using retrieved evidence.
```

Ask:

```text
Compare papers
```

Expected:

```text
ResearchMate creates a quick temporary OpenAI comparison directly from PDFs in data/papers/.
```

Ask:

```text
Compare saved papers
```

Expected:

```text
ResearchMate creates a comparison table from approved summaries in data/summaries/.
```

---

## 11. Stop the local server

In the terminal running `uv run langgraph dev`, press:

```text
Ctrl + C
```

---

## 12. Interview explanation

Use this 45-second explanation:

```text
ResearchMate is a literature-review assistant built with LangChain and LangGraph.

It loads local PDF papers, retrieves evidence, answers grounded questions, creates structured paper summaries, and compares papers in a literature-review table.

The project has two modes. Fallback mode works without an API key using simple search and rule-based routing. OpenAI-compatible mode adds structured summarization, semantic retrieval, quick comparison, and grounded Q&A.

The key design choice is human approval: summaries are not saved directly after generation. The researcher can approve, edit, or reject them before they enter the final comparison table.

The project also has an Agent Chat UI integration. The UI can list local papers, summarize selected papers, answer grounded questions, and compare either all local PDFs quickly or only approved saved summaries.
```

---

## 13. Final Git commands after documentation changes

```powershell
git status
git add README.md demo_commands.md
git commit -m "Update documentation for OpenAI and Agent Chat UI workflow"
git push
```
