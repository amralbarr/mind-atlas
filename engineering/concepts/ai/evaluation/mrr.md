# MRR (Mean Reciprocal Rank)

**The core question:** How high up in the ranked list does the *first* relevant result appear?

```
Reciprocal Rank = 1 / (rank of first relevant result)
MRR = average Reciprocal Rank across all queries
```

**Example:** The first relevant result appears at position 3 → RR = 1/3 = **0.33**. If a second query's first relevant result lands at rank 1, its RR = 1/1 = **1.0**. Averaged across the two queries: MRR = (0.33 + 1.0) / 2 = **0.67**.

## Why MRR, when Recall@k and Precision@k already exist

[Recall@k](retrieval-metrics.md#recallk) asks "did we find everything relevant," and [Precision@k](retrieval-metrics.md#precisionk) asks "how much of what we returned is actually relevant" — neither one cares *where* in the ranked list a relevant result landed, only whether it's present in the top-k set at all. MRR is the metric that specifically rewards surfacing at least one relevant result **near the top** of the ranking, which matters most when a query only needs one good chunk to be answered correctly — a common shape in [RAG](../rag/rag.md) question-answering, where the [LLM](../generation/llm.md) just needs one solidly relevant passage in its context, not an exhaustive set.

A system can have identical Recall@5 and Precision@5 scores while differing sharply in MRR: one puts its only relevant hit at rank 1, the other at rank 5 — both "found" it, but the first is far more useful to a user who only reads the top result, or to an [LLM](../generation/llm.md) whose [context window](../generation/context-window.md) is ordered by rank.

## What a low MRR signals

A low average MRR despite decent Recall@k means the retriever is finding relevant chunks but burying them low in the ranking — exactly the failure mode [cross-encoder re-ranking](../retrieval/cross-encoder-reranking.md) is designed to fix: a [bi-encoder](../../../overviews/ai/bi-encoder-vs-cross-encoder.md)'s initial retrieval can surface a relevant chunk anywhere in its top-k (good Recall@k), while a [cross-encoder](../retrieval/cross-encoder-reranking.md) re-score afterward pushes the genuinely best-matching chunk up toward rank 1 (improving MRR specifically), because it can judge *how well* each candidate actually answers the query rather than just whether it's topically similar.

## Related

- [Retrieval Metrics](retrieval-metrics.md) — the full metrics family (Recall@k, Precision@k, [NDCG](ndcg.md)) MRR belongs to, plus a worked example computing all of them together
- [Cross-Encoder Re-Ranking](../retrieval/cross-encoder-reranking.md) — the stage that most directly improves MRR by re-scoring an already-retrieved candidate set
- [Bi-Encoder vs. Cross-Encoder](../../../overviews/ai/bi-encoder-vs-cross-encoder.md) — why the first-stage retriever alone tends to leave relevant results buried lower in rank than a second-stage [re-ranker](../retrieval/cross-encoder-reranking.md) would
- [RAG](../rag/rag.md) — the system MRR is usually measured within, since one well-ranked chunk is often enough to answer a question correctly
