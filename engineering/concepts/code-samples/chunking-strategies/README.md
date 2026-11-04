# Chunking Strategies — Runnable Example

Three real chunking strategies (fixed-size, recursive-character,
structure-aware) compared on the same sample document — companion to
[How do you choose chunk size and overlap?](../../interview/interview-01/01-rag.md)
and [Chunking Strategies & Libraries](../../../overviews/ai/chunking-strategies.md).

The tests prove the concrete claim the handbook makes: fixed-size chunking
can bleed text across a section boundary (one chunk ends up containing both
the tail of "Leave Policy" and the head of "Expense Reimbursement");
structure-aware chunking never does, because it splits on headings first.

## Run it

```bash
cd code-samples
python3 -m venv .venv
.venv/bin/pip install -r chunking-strategies/requirements.txt
.venv/bin/python3 chunking-strategies/chunking_strategies.py
.venv/bin/pytest chunking-strategies/tests/ -v
```

## Concepts this demonstrates

- [Chunking Strategies & Libraries](../../../overviews/ai/chunking-strategies.md)

## Related

- [RAG — Interview Q&A](../../interview/interview-01/01-rag.md)
- [RAG Deep Dive](../../interview/interview-01/11-rag-deep-dive.md)
