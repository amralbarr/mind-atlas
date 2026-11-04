# Retrieval Metrics

Metrics for measuring how well a retriever finds the right documents or chunks. Critical in [RAG](../rag/rag.md) systems — if the retriever misses a relevant chunk, the [LLM](../generation/llm.md) never sees it and the answer will be wrong regardless of generation quality.

## Recall@k

**The core question:** Out of all truly relevant chunks for a query, what fraction does the retriever return in the top K results?

```
Recall@k = (number of relevant chunks in top-k results) / (total relevant chunks for that query)
```

**Example:**
- Query: "What is the leave policy?"
- Ground truth: 5 chunks in the corpus are relevant to this query
- Retriever returns 3 of those 5 in its top-5 results
- **Recall@5 = 3/5 = 0.60**

A Recall@5 of 1.0 means the retriever found every chunk needed — nothing relevant was left behind.

**Why Recall@k is the primary [RAG](../rag/rag.md) metric:** [RAG](../rag/rag.md) quality has a hard ceiling set by retrieval. If the correct chunk is not in the top-k [context window](../generation/context-window.md), the [LLM](../generation/llm.md) cannot use it. High generation quality cannot compensate for a missed retrieval. Recall@k directly measures this ceiling.

## Precision@k

**The core question:** Of the k results returned, what fraction are actually relevant?

```
Precision@k = (number of relevant chunks in top-k results) / k
```

**Example:** Retriever returns 5 results, 2 are relevant → Precision@5 = 2/5 = 0.40

Precision@k matters when [context window](../generation/context-window.md) size is limited — you want the chunks you include to actually be useful.

## MRR (Mean Reciprocal Rank)

Rewards surfacing at least one relevant result near the top of the ranking, rather than just somewhere in the top-k — useful when a query only needs one good chunk to be answered correctly. See [MRR](mrr.md) for the formula, a worked example, and why it catches a failure mode Recall@k and Precision@k both miss.

## NDCG (Normalized Discounted Cumulative Gain)

Accounts for the position of relevant results AND their degree of relevance (if you have graded relevance, e.g. "highly relevant" vs "somewhat relevant"). More complex to compute but gives a richer signal than binary relevant/not-relevant metrics. Less common in [RAG](../rag/rag.md) evaluation than Recall@k/[MRR](mrr.md) specifically because it needs graded relevance labels rather than a binary one. See [NDCG](ndcg.md) for the full formula, a worked numerical example, and why the discount/gain terms are shaped the way they are.

## How k Is Actually Chosen at Query Time

Recall@k/Precision@k assume you explicitly requested k results — that's the normal retrieval mechanic, not an afterthought:

```python
# You pass top_k / n_results / limit to the search call itself.
# The vector store computes similarity against every indexed vector
# (or an ANN approximation of it — see Approximate Nearest Neighbor
# Search (ANN) & HNSW) and returns exactly k results,
# already sorted by score — it does not return everything for you to filter.
results = collection.query(
    query_embeddings=[query_vector],
    n_results=5,        # <- k, chosen by you before the call
)
```

You are **not** given the full result set to filter down yourself — k bounds what the store computes and returns. What you *do* get back alongside each result is its similarity score, which opens a second, independent control: a **minimum-similarity threshold**, applied on top of (or instead of) k:

```python
# Retrieve a wider net, then threshold-filter by score
results = collection.query(query_embeddings=[query_vector], n_results=20)
kept = [r for r in results if r.score >= 0.75]   # may return fewer than 20, even zero
```

This is what powers retrieval-level abstention: if nothing clears the threshold, there's no confident match — the system should say so rather than pass weak candidates into generation. See [RAG](../rag/rag.md) and the retrieval-level abstention check in the [architecture design exercise](../../../interview/interview-01/06-design.md).

**The two-stage pattern this feeds into:** retrieve a larger k (e.g. top-20, casting a wide net favoring recall) → [cross-encoder re-rank](../retrieval/cross-encoder-reranking.md) or threshold-filter down to a smaller final k (e.g. top-5, favoring precision) before it reaches the [LLM](../generation/llm.md)'s [context window](../generation/context-window.md). See [Hybrid Search](../retrieval/hybrid-search.md) for the merge step that usually sits between those two stages.

A higher requested k mechanically raises Recall@k (more chances to include every relevant chunk) but can lower Precision@k (more irrelevant chunks ride along) and costs more context tokens — the k you choose is itself a tuning decision, measured the same way any other retrieval change is measured.

## Worked Example: Scoring a Real Result Set

**Query:** *"What is the leave policy?"*
**Ground truth** (relevant chunks, established ahead of time): `doc_42_chunk_3`, `doc_42_chunk_4`, `doc_15_chunk_1`

| Rank | id | score | department | page | Relevant? |
|---|---|---|---|---|---|
| 1 | doc_42_chunk_3 | 0.89 | HR | 12 | ✅ |
| 2 | doc_8_chunk_2 | 0.81 | HR | 4 | ❌ |
| 3 | doc_42_chunk_4 | 0.79 | HR | 13 | ✅ |
| 4 | doc_30_chunk_1 | 0.71 | HR | 2 | ❌ |
| 5 | doc_12_chunk_6 | 0.68 | HR | 9 | ❌ |

Note that `doc_15_chunk_1` was **never retrieved at all** — the model will never see it, no matter how good generation is.

- **Recall@5** = 2 relevant retrieved ÷ 3 relevant total = **0.67**
- **Precision@5** = 2 ÷ 5 = **0.40**
- **Reciprocal Rank** = first relevant hit at rank 1 → **1.0**

**Applying a `score_threshold` of 0.75** keeps only the top 3 (0.89, 0.81, 0.79), dropping the two weakest hits:
- Recall stays at **0.67** — nothing relevant was lost, both relevant hits scored above the cutoff
- Precision rises to 2 ÷ 3 = **0.67** — fewer irrelevant chunks reach the [context window](../generation/context-window.md), and fewer tokens are spent

A second query, *"How do I submit an expense report?"*, has one relevant chunk (`doc_7_chunk_2`) which lands at rank 2: Recall@5 = 1/1 = **1.0**, Precision@5 = 1/5 = **0.20**, RR = 1/2 = **0.50**.

A third, out-of-scope query — *"What is the CEO's salary?"* — has **no** relevant chunk in the corpus. The top result scores 0.52, below the 0.75 threshold, so nothing is returned. Recall and Precision don't apply here (there's nothing to recall); instead, measure **abstention accuracy** — did the system correctly return nothing rather than force an answer from weak matches? Here: yes. See [Groundedness and Correctness](groundedness-and-correctness.md) for how this abstention signal carries through to generation.

Averaged across the two answerable queries: Recall@5 = (0.67 + 1.0) / 2 = **0.83**, Precision@5 = (0.40 + 0.20) / 2 = **0.30**, [MRR](mrr.md) = (1.0 + 0.50) / 2 = **0.75**. Abstention accuracy on the out-of-scope query: 1/1 = **100%**.

## In Practice: Building a Retrieval Evaluation Set

```python
# A fixed test set for measuring retrieval quality — relevant: [] marks an
# intentionally out-of-scope query, where the expected result is "retrieve nothing"
eval_set = [
    {"query": "What is the leave policy?",
     "relevant": ["doc_42_chunk_3", "doc_42_chunk_4", "doc_15_chunk_1"]},
    {"query": "How do I submit an expense report?",
     "relevant": ["doc_7_chunk_2"]},
    {"query": "What is the CEO's salary?",
     "relevant": []},
    # ... 100+ queries covering normal, edge, out-of-scope, adversarial
]

def evaluate(retrieve_fn, eval_set, k=5, threshold=0.75):
    """retrieve_fn(query, k) -> list[(chunk_id, score)], already ranked."""
    recalls, precisions, rrs, abstain_correct = [], [], [], []

    for item in eval_set:
        hits = retrieve_fn(item["query"], k)
        kept = [chunk_id for chunk_id, score in hits if score >= threshold]
        relevant = set(item["relevant"])

        if not relevant:                                   # out-of-scope query
            abstain_correct.append(len(kept) == 0)
            continue

        found = [c for c in kept if c in relevant]
        recalls.append(len(found) / len(relevant))
        precisions.append(len(found) / len(kept) if kept else 0.0)
        rank = next((i + 1 for i, c in enumerate(kept) if c in relevant), None)
        rrs.append(1 / rank if rank else 0.0)

    avg = lambda xs: round(sum(xs) / len(xs), 2) if xs else None
    return {
        f"Recall@{k}": avg(recalls),
        f"Precision@{k}": avg(precisions),
        "MRR": avg(rrs),
        "Abstention accuracy": avg(abstain_correct),
    }
```

Build this test set before tuning chunking strategy, embedding models, or re-ranking — without a baseline, you're guessing whether changes helped.

## Comparing Retrieval Settings

This is the kind of table `evaluate()` above produces when run against the same fixed test set under different configurations (illustrative numbers):

| Setting | Recall@k | Precision@k | [MRR](mrr.md) | Context tokens |
|---|---|---|---|---|
| k=5, no filter | 0.72 | 0.31 | 0.68 | ~2,500 |
| k=10, no filter | 0.86 | 0.19 | 0.68 | ~5,000 |
| k=5 + metadata filter | 0.81 | 0.42 | 0.79 | ~2,500 |
| k=20 → re-rank to 5 | **0.89** | **0.55** | **0.88** | ~2,500 |

**Reading it:**
- Raising k from 5 to 10 improved Recall but doubled token cost and lowered Precision — more candidates, more noise.
- The metadata filter (see [Vector Databases](../retrieval/vector-database.md)) improved everything at no extra token cost, because it removed chunks from irrelevant departments before they could compete for a rank slot.
- The two-stage pattern — retrieve a wide top-20, then [cross-encoder re-rank](../retrieval/cross-encoder-reranking.md) down to 5 — gave the best balance of all three metrics at the same token budget as the naive k=5 baseline.

## A Practical Warning About Metadata

Filtering is a double-edged sword: if metadata is wrong or incomplete — a leave-policy chunk mistakenly tagged `department: "Finance"` — the filter excludes it permanently and Recall@k drops **silently**, with no error to signal it. Measure Recall@k both **with and without** the metadata filter during evaluation to catch this before it reaches production.

## Related

- [MRR](mrr.md) — its own atomic file now; formula, worked example, and the specific failure mode it catches that Recall@k/Precision@k miss
- [LLM Evaluation](llm-evaluation.md)
- [Fixed Evaluation Dataset](fixed-evaluation-dataset.md)
- [Groundedness and Correctness](groundedness-and-correctness.md)
- [RAG](../rag/rag.md)
- [Hybrid Search](../retrieval/hybrid-search.md)
- [Approximate Nearest Neighbor Search (ANN)](../retrieval/approximate-nearest-neighbor.md) / [HNSW](../retrieval/hnsw.md) — [ANN](../retrieval/approximate-nearest-neighbor.md) recall vs. [RAG](../rag/rag.md) Recall@k is a distinct, related measurement
- [Cross-Encoder Re-Ranking](../retrieval/cross-encoder-reranking.md) — the second-stage mechanism behind the best-performing settings in the comparison table above
- [Bi-Encoder vs. Cross-Encoder](../../../overviews/ai/bi-encoder-vs-cross-encoder.md) — why the first-stage retriever alone tends to under-perform on [MRR](mrr.md) specifically
- [Reciprocal Rank Fusion (RRF)](../retrieval/reciprocal-rank-fusion.md)
