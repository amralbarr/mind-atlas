# Code Samples

Real, runnable mini-projects illustrating a pattern discussed in `concepts/`
or `interview/` — the docs explain the *why*, each project here is the
actual, tested *what*. Every project is two-way linked: the markdown doc
links to the project folder, and the project's own code/README link back
to the concept files and interview Q&A that motivate it.

| Project | Companion doc | Tests |
|---|---|---|
| [python-assistant-api/](python-assistant-api/) | [Python Assistant API Deep Dive](../interview/interview-01/20-python-assistant-api-deep-dive.md) | 3 passing |
| [rag-hybrid-search/](rag-hybrid-search/) | [RAG — Interview Q&A](../interview/interview-01/01-rag.md) | 3 passing |
| [eval-harness/](eval-harness/) | [Evaluation & Validation — Interview Q&A](../interview/interview-01/02-eval.md) | 3 passing |
| [chunking-strategies/](chunking-strategies/) | [RAG — Interview Q&A](../interview/interview-01/01-rag.md) | 3 passing |
| [sql-analytics-queries/](sql-analytics-queries/) | [Structured Data, Analytics & ML — Interview Q&A](../interview/interview-01/08-sql-analytics-ml.md) | 4 passing |
| [bounded-concurrent-worker/](bounded-concurrent-worker/) | [Python & SQL Coding Round — Interview Q&A](../interview/interview-01/13-python-sql-coding-round.md) | 4 passing |

## Running any project

Each project has its own `requirements.txt`. Most share the venv at
`code-samples/.venv` (created once, reused across projects):

```bash
cd code-samples
python3 -m venv .venv
.venv/bin/pip install -r <project>/requirements.txt
.venv/bin/pytest <project>/tests/ -v
```

`python-assistant-api/` keeps its own separate `.venv` since it needs
`fastapi`/`httpx`, a heavier dependency set than the other projects.
