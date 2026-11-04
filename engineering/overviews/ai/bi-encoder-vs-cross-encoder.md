# Bi-Encoder vs. Cross-Encoder

This is the single most important distinction behind a "retrieve-then-rerank" [RAG](../../concepts/ai/rag/rag.md) pipeline, and the thing an interview question about re-ranking is actually testing: two different ways of scoring how relevant a document is to a query, trading speed for accuracy in opposite directions.

## How each one scores a query-document pair

**[Bi-encoder](../../concepts/ai/retrieval/bi-encoder.md)** (what embedding models are): encodes the query and the document **separately**, each compressed into its own vector with no visibility into the other, then compares the two vectors with a cheap similarity function (cosine).

```
Query    → model → query vector   ─┐
                                    ├─► cosine → 0.82
Document → model → document vector ─┘
           (each one encoded independently)
```

**[Cross-encoder](../../concepts/ai/retrieval/cross-encoder.md)** (what re-rankers are, among other uses — see the [Cross-Encoder](../../concepts/ai/retrieval/cross-encoder.md) concept file for its other major application, NLI/entailment classification): encodes the query **and** the document **together**, in a single forward pass, letting the model attend directly between every query token and every document token, and outputs one relevance score directly.

```
[Query + Document] → model → 0.97
      (both together, in one input)
```

## The comparison

| | **[Bi-encoder](../../concepts/ai/retrieval/bi-encoder.md)** | **[Cross-encoder](../../concepts/ai/retrieval/cross-encoder.md)** |
|---|---|---|
| **How it scores a pair** | Encodes query and document **separately**, then compares the two vectors | Reads query and document **together**, outputs a relevance score directly |
| **Can it precompute document vectors ahead of time?** | ✅ Yes — this is exactly what makes a [vector database](../../concepts/ai/retrieval/vector-database.md) possible at all | ❌ No — the model needs the query **and** a specific document together, so nothing can be precomputed per-document |
| **Speed at query time** | Fast — one query vector, then a cheap comparison against millions of precomputed document vectors | Slow — one full model forward pass **per query-document pair** being scored |
| **Accuracy** | Good, but misses subtler signals since query and document never actually "see" each other | **Higher** — direct attention between the two texts catches relevance signals a [bi-encoder](../../concepts/ai/retrieval/bi-encoder.md)'s separate encodings miss |

## Worked example: what a bi-encoder misses that a cross-encoder catches

**Query:** "Am I entitled to maternity leave if I haven't completed a year at the company?"

| Passage | [Bi-encoder](../../concepts/ai/retrieval/bi-encoder.md) score | [Cross-encoder](../../concepts/ai/retrieval/cross-encoder.md) score |
|---|---|---|
| **A:** "Maternity leave is 10 weeks paid, starting four weeks before the due date…" | **0.89** 🥇 (very similar topic) | 0.61 |
| **B:** "Eligibility for special leave, including maternity, requires completing 12 months of service…" | 0.78 🥈 | **0.96** 🥇 (directly answers the eligibility condition) |
| **C:** "Annual leave policy for new employees during their first year…" | 0.76 🥉 | 0.22 |

**What happened:** the [bi-encoder](../../concepts/ai/retrieval/bi-encoder.md) saw that passage A "talks about maternity leave" and ranked it highest — that's **topical similarity**. The [cross-encoder](../../concepts/ai/retrieval/cross-encoder.md) noticed that *"haven't completed a year"* in the query directly matches *"completing 12 months"* in passage B, and recognized that B is the one that actually **answers** the question — that's **relevance to the answer**, not just the topic. It correctly rejected passage C, which shares surface vocabulary ("first year") but is about an entirely different leave policy.

This is the core failure mode a [bi-encoder](../../concepts/ai/retrieval/bi-encoder.md) has structurally: it can't tell "mentions the same topic" apart from "actually answers the specific question asked," because the query and document are never compared token-by-token — only as two independent, already-compressed vectors.

## Why not just use a cross-encoder for everything

The compute cost scales with the number of documents being scored, not just the query:

| Approach | Model forward passes per query, over 1M documents |
|---|---|
| Bi-encoder | **1** (just the query vector — documents were already embedded once, ahead of time) |
| [Cross-encoder](../../concepts/ai/retrieval/cross-encoder.md) over the whole corpus | **1,000,000** ❌ not practical |
| Cross-encoder over a pre-filtered top-20 | **20** ✅ affordable |

That's why a cross-encoder is **always the second stage of a pipeline, never the first**: a bi-encoder's precomputed vectors are what make the initial retrieval step fast enough at scale to narrow a million documents down to a short candidate list a cross-encoder can then afford to re-score. See [Cross-Encoder Re-Ranking](../../concepts/ai/retrieval/cross-encoder-reranking.md) for the full two-stage pipeline, the libraries/tools that implement this re-scoring step, and why re-ranking can't recover a relevant document that the first-stage bi-encoder failed to retrieve at all.

## Related

- [Bi-Encoder](../../concepts/ai/retrieval/bi-encoder.md) / [Cross-Encoder](../../concepts/ai/retrieval/cross-encoder.md) — the standalone atomic concept files this comparison is built from, including where each architecture shows up beyond [RAG](../../concepts/ai/rag/rag.md) retrieval
- [Cross-Encoder Re-Ranking](../../concepts/ai/retrieval/cross-encoder-reranking.md) — the second-stage pipeline this comparison is the foundation of; covers the full retrieve-then-rerank flow and concrete tools (`sentence-transformers`, BGE-reranker, [Cohere Rerank](../../concepts/ai/retrieval/cohere-rerank.md), [Azure AI Search](../../concepts/cloud/azure/azure-ai-search.md) semantic ranking)
- [Vector Database](../../concepts/ai/retrieval/vector-database.md) — what a bi-encoder's precomputed vectors make possible in the first place
- [MRR](../../concepts/ai/evaluation/mrr.md) — the metric a [cross-encoder re-ranking](../../concepts/ai/retrieval/cross-encoder-reranking.md) stage most directly improves, by pushing the best-matching result up toward rank 1
- [Retrieval Metrics](../../concepts/ai/evaluation/retrieval-metrics.md) — where the full retrieve-then-rerank settings comparison shows this two-stage pattern outperforming either stage alone
- [Hybrid Search](../../concepts/ai/retrieval/hybrid-search.md) — the merge step ([RRF](../../concepts/ai/retrieval/reciprocal-rank-fusion.md) or alpha blending) that typically sits between bi-encoder retrieval and [cross-encoder re-ranking](../../concepts/ai/retrieval/cross-encoder-reranking.md)
