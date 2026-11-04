# Cross-Encoder Re-Ranking (Re-Ranker)

Re-ranking is the second-pass stage in a retrieve-then-rerank pipeline: retrieve a wide candidate set cheaply (e.g. top-20 or top-50 via vector/[hybrid search](hybrid-search.md)), then re-score that smaller set with a slower, more accurate model before returning the final top-k. The model that does the re-scoring is almost always a **[cross-encoder](cross-encoder.md)** — which is the thing worth actually understanding, since "re-ranking" just names the pipeline position, not the mechanism.

## Cross-encoder vs. bi-encoder — the distinction that matters

This is the single most important thing to know about re-ranking, and the thing an interview question is actually testing: a [cross-encoder](cross-encoder.md) reads the query and document **together** in one forward pass (slow, but accurate), while the [bi-encoder](bi-encoder.md) that did the initial retrieval encoded them **separately** into precomputed vectors (fast, but blind to how the two texts actually relate). See [Bi-Encoder vs. Cross-Encoder](../../../overviews/ai/bi-encoder-vs-cross-encoder.md) for the full comparison, including a worked example of a [bi-encoder](bi-encoder.md) ranking a topically-similar-but-wrong passage above the one that actually answers the question.

## How the full pipeline fits together

```
Query
  → Bi-encoder retrieval (vector search, or hybrid + RRF)   → top-20/50 candidates (fast, approximate)
  → Cross-encoder re-ranking                                 → final top-5 (slow, but on a small set — affordable)
  → Return to LLM / user
```

This is the same two-stage, retrieve-wide-then-narrow pattern referenced throughout this handbook's [RAG](../rag/rag.md) material — see the [Architecture Design Exercise](../../../interview/interview-01/06-design.md)'s retrieval stage, which explicitly re-ranks "top-20 → top-5" before context assembly, and [Retrieval Metrics](../evaluation/retrieval-metrics.md)'s settings-comparison table, where "k=20 → re-rank to 5" is the best-performing configuration.

## Why it's worth the extra latency

A [bi-encoder](bi-encoder.md)'s precomputed, separately-encoded vectors are a necessary compromise for speed — they systematically miss relevance signals that only show up when the query and document are considered jointly (e.g. whether a specific phrase in the document directly answers a specific clause in the query, rather than just being generally topically similar). A cross-encoder recovers that signal, at the cost of being too slow to run as the primary retrieval mechanism. Running it only on an already-narrowed candidate set is what makes the trade-off worthwhile: better final ranking, bounded extra cost.

## Libraries and technologies

| Tool                                                                                | Type                     | Notes                                                                                                                                                                                                                                                          |
| ----------------------------------------------------------------------------------- | ------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **`sentence-transformers` `CrossEncoder`**                                          | Open-source, self-hosted | The standard Python library; ships pretrained cross-encoder models (e.g. `ms-marco-MiniLM`) ready to score query-document pairs directly                                                                                                                       |
| **BGE-reranker**                                                                    | Open-source, self-hosted | A strong, commonly-benchmarked open cross-encoder reranker, multilingual variants available                                                                                                                                                                    |
| **[Cohere Rerank](cohere-rerank.md)**                                                                   | Managed API              | Hosted reranking-as-a-service — no model to host yourself, pay per call                                                                                                                                                                                        |
| **[Azure AI Search](../../cloud/azure/azure-ai-search.md) semantic ranking**        | Managed, built-in        | A Microsoft-managed cross-encoder/machine-reading-comprehension model applied automatically as an optional second pass — see [Azure AI Search](../../cloud/azure/azure-ai-search.md), which documents its own `k=50`-candidates-for-the-reranker best practice |
| **[Qdrant](vector-stores/qdrant.md) / most [vector databases](vector-database.md)** | No built-in re-ranker    | [Qdrant](vector-stores/qdrant.md)'s `score_threshold` and similar mechanisms narrow or filter candidates, but actual cross-encoder re-ranking is typically bolted on as a separate step using one of the tools above, not provided by the vector store itself  |

## Related

- [MMR (Maximal Marginal Relevance)](mmr.md) — the diversity-focused counterpart to this file's relevance-ordering focus; the two solve different problems in the same pipeline position and can be combined
- [Bi-Encoder vs. Cross-Encoder](../../../overviews/ai/bi-encoder-vs-cross-encoder.md) — the full comparison this file's first section used to contain inline, including a worked example
- [Hybrid Search](hybrid-search.md) — re-ranking is one of its three merge strategies, alongside [RRF](reciprocal-rank-fusion.md) and alpha blending
- [Reciprocal Rank Fusion (RRF)](reciprocal-rank-fusion.md) — the cheaper merge method re-ranking is usually layered on top of, not a substitute for
- [Vector Databases](vector-database.md) — what makes bi-encoder retrieval fast enough to feed a re-ranker in the first place
- [Azure AI Search](../../cloud/azure/azure-ai-search.md) — a managed cross-encoder re-ranker as a built-in feature
- [MRR](../evaluation/mrr.md) — the metric this stage most directly improves, by pushing the best-matching result up toward rank 1
- [Retrieval Metrics](../evaluation/retrieval-metrics.md) — where the retrieve-then-rerank pattern is shown to outperform either stage alone
