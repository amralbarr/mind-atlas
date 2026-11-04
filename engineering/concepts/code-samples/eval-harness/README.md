# Retrieval Eval Harness — Runnable Example

A real `evaluate()` function computing Recall@k, Precision@k, MRR, and
abstention accuracy against a fixed test set — companion to
[How would you evaluate a RAG system?](../../interview/interview-01/02-eval.md)
and [the evaluation metrics workshop](../../interview/interview-01/15-evaluation-metrics-workshop.md).

Runs against a fake, dictionary-backed retriever with zero external
dependencies — swap `make_fake_retriever()` for a real vector-store call and
`evaluate()` itself needs no changes.

## Run it

```bash
cd code-samples
python3 -m venv .venv
.venv/bin/pip install -r eval-harness/requirements.txt
.venv/bin/python3 eval-harness/eval_harness.py
.venv/bin/pytest eval-harness/tests/ -v
```

## Concepts this demonstrates

- [Retrieval Metrics](../../concepts/ai/evaluation/retrieval-metrics.md) — Recall@k, Precision@k, MRR, abstention accuracy
- [Fixed Evaluation Dataset](../../concepts/ai/evaluation/fixed-evaluation-dataset.md) — why `EVAL_SET` must stay stable across runs

## Related

- [Evaluation & Validation — Interview Q&A](../../interview/interview-01/02-eval.md)
- [Evaluation Metrics Workshop](../../interview/interview-01/15-evaluation-metrics-workshop.md)
