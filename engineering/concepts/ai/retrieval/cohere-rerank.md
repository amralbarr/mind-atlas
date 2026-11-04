# Cohere Rerank

Cohere Rerank is a managed, hosted [cross-encoder re-ranking](cross-encoder-reranking.md) API: send it a query and a list of candidate documents, and it returns those documents re-ordered by relevance with a score per document — reranking-as-a-service, with no model to train, host, or scale yourself.

## How it works

Like any [cross-encoder](../../../overviews/ai/bi-encoder-vs-cross-encoder.md), Rerank reads the query and each candidate document together rather than comparing precomputed, separately-encoded vectors, which is what lets it catch relevance signals a first-pass [vector search](vector-database.md) or [hybrid search](hybrid-search.md) misses. It supports over 100 languages, and newer model versions (v3.5+) handle semi-structured data (e.g. [JSON](../../programming/fundamentals/json.md)-like records) in addition to plain text, so it can rerank structured search results, not just prose passages.

## Basic usage

```bash
pip install cohere
```

```python
import cohere

co = cohere.ClientV2(api_key="...")

results = co.rerank(
    model="rerank-v3.5",
    query="Am I entitled to maternity leave if I haven't completed a year at the company?",
    documents=candidate_passages,  # list[str], typically the top-20/50 from a first-pass retrieval
    top_n=5,
)

for r in results.results:
    print(r.index, r.relevance_score)  # index back into the original documents list
```

The response is a ranked list of `(index, relevance_score)` pairs pointing back into the original `documents` list — the caller re-orders its own candidate set using those indices rather than getting document text back from the API.

## Pricing model

Rerank is billed per **search unit**, not per token: one query against up to roughly 100 documents of up to ~500 tokens each counts as one search unit, and documents longer than that are chunked internally with each chunk counted separately. This makes cost roughly proportional to (number of queries) × (candidate-set size), which is exactly why re-ranking is always run on an already-narrowed candidate set (e.g. top-20/50 from a first-pass retrieval) rather than against a full corpus — see [Cross-Encoder Re-Ranking](cross-encoder-reranking.md)'s cost table for why that two-stage shape is unavoidable for any [cross-encoder](cross-encoder.md), hosted or self-run.

## When to use it vs. a self-hosted cross-encoder

| | Cohere Rerank | `sentence-transformers` / BGE-reranker |
|---|---|---|
| **Hosting** | Fully managed — no GPU, no model ops | Self-hosted — needs inference infrastructure |
| **Cost shape** | Pay-per-search-unit, scales with usage | Fixed infra cost regardless of volume |
| **Latency control** | Network round-trip to Cohere's API | Runs in-process / in your own infra, no external call |
| **Multilingual coverage** | 100+ languages out of the box | Depends on the specific open model chosen |
| **Data residency** | Documents leave your infrastructure for the API call | Stays entirely in-house |

The practical decision mirrors any build-vs-buy call: Cohere Rerank is the faster path to a working re-ranking stage with no infra to operate, while a self-hosted [cross-encoder](cross-encoder.md) is preferable when data can't leave the environment, or at a scale where per-call pricing would exceed the cost of running the model yourself.

## Related

- [Cross-Encoder Re-Ranking](cross-encoder-reranking.md) — the general pipeline pattern this is a managed implementation of, including its own Libraries and Technologies table
- [Bi-Encoder vs. Cross-Encoder](../../../overviews/ai/bi-encoder-vs-cross-encoder.md) — why reranking has to run on a pre-narrowed candidate set, not the full corpus
- [Hybrid Search](hybrid-search.md) / [Vector Database](vector-database.md) — the first-pass retrieval stage that produces the candidate set Rerank re-scores
- [Azure AI Search](../../cloud/azure/azure-ai-search.md) — a comparable managed semantic-ranking feature bundled into a search platform rather than offered as a standalone API
- [MRR](../evaluation/mrr.md) — the metric a reranking stage like this most directly improves
