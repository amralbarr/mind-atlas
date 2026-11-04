# BM25 vs. Hybrid Search vs. RRF

These three are not alternatives to choose between — they're **three different layers of the same system**.

| Concept | What is it? | Answers the question |
|---|---|---|
| **[BM25](../../concepts/ai/retrieval/bm25.md)** | A **scoring algorithm** for keyword search | How do I rank the documents that contain the query's words? |
| **[Hybrid Search](../../concepts/ai/retrieval/hybrid-search.md)** | An **architecture** that runs two searches together | How do I combine the strengths of keyword search and semantic search? |
| **[RRF](../../concepts/ai/retrieval/reciprocal-rank-fusion.md)** | A **fusion method** for merging ranked lists | How do I merge two result lists scored on different scales? |

**Analogy — a competition judged by two panels:**
- **[BM25](../../concepts/ai/retrieval/bm25.md)** is the first panel's scoring method.
- **Cosine similarity** is the second panel's scoring method.
- **[Hybrid search](../../concepts/ai/retrieval/hybrid-search.md)** is the decision to have two panels in the first place.
- **[RRF](../../concepts/ai/retrieval/reciprocal-rank-fusion.md)** is how the two panels' rankings get combined into one final ranking.

---

## 1. BM25: how keyword search scores results

After the [inverted index](../../concepts/ai/retrieval/inverted-index.md) finds the documents containing the query's words, [BM25](../../concepts/ai/retrieval/bm25.md) gives each one a score based on three factors:

| Factor | The idea | Example |
|---|---|---|
| **Term frequency (TF), with saturation** | The more a word repeats in a document, the higher the score — **but with diminishing returns** | "leave" appearing 10 times isn't ten times better than appearing once |
| **Term rarity ([IDF](../../concepts/ai/retrieval/idf.md))** | A word that's rare across the whole corpus is weighted higher | "maternity" matters more than "the" or "in" |
| **Document length** | A long document is penalized slightly | A term appearing twice in a short paragraph counts for more than appearing twice across 50 pages |

**The output:** an unbounded score — something like 14.2, 9.8, or 3.1 — dependent on the corpus and the query.

**Its weakness:** no concept of meaning. "Vacation" and "leave" are two completely unrelated words as far as [BM25](../../concepts/ai/retrieval/bm25.md) is concerned.

## 2. Hybrid Search: running both searches together

```
                    Query
                      │
        ┌─────────────┴─────────────┐
        ▼                           ▼
  Keyword search                Vector search
  (Inverted Index + BM25)       (HNSW + cosine)
        │                           │
  Ranked list A                Ranked list B
        └─────────────┬─────────────┘
                      ▼
               Merge  ← this is where RRF comes in
                      ▼
                Final result
```

**The idea:** each search covers the other's blind spot. Keywords win on exact codes, names, and precise terminology; vectors win on synonyms and paraphrasing.

## 3. RRF: how the two lists actually get merged

### The problem it solves

The scores come from two completely different scales:
- [BM25](../../concepts/ai/retrieval/bm25.md): 14.2, 9.8, 6.1 (unbounded)
- Cosine: 0.91, 0.88, 0.80 (roughly 0 to 1)

Adding them directly would let [BM25](../../concepts/ai/retrieval/bm25.md) dominate every time, simply because its numbers are bigger — 9.8 and 0.88 aren't fairly comparable.

### The fix: ignore the scores, use only the **rank**

```
RRF_score(doc) = Σ  1 / (k + rank)
```
- `rank` = the document's position in each list
- `k` = a constant, commonly **60**, which softens the gap between the top positions
- summed across every list the document appears in

### Worked example

| Rank | [BM25](../../concepts/ai/retrieval/bm25.md) list | Vector list |
|---|---|---|
| 1 | doc_A (14.2) | doc_C (0.91) |
| 2 | doc_B (9.8) | doc_A (0.88) |
| 3 | doc_C (6.1) | doc_D (0.80) |

Computed with `k = 60`:

| Document | From BM25 | From Vector | **Total** |
|---|---|---|---|
| doc_A | 1/61 = 0.01639 | 1/62 = 0.01613 | **0.03252** 🥇 |
| doc_C | 1/63 = 0.01587 | 1/61 = 0.01639 | **0.03226** 🥈 |
| doc_B | 1/62 = 0.01613 | — | **0.01613** 🥉 |
| doc_D | — | 1/63 = 0.01587 | **0.01587** |

**What happened:**
- **doc_A and doc_C rose to the top** because both searches agreed on them — this is [RRF](../../concepts/ai/retrieval/reciprocal-rank-fusion.md)'s core behavior: **a document that shows up in both lists gets rewarded**.
- doc_B was 2nd in BM25 but fell, because the vector search never found it at all.
- 14.2 was never compared against 0.91 — it never had to be.

### RRF's strengths and weaknesses

| ✅ Strengths | ⚠️ Weaknesses |
|---|---|
| No need to normalize score scales | Throws away the **magnitude** of the difference — a 0.99 and a 0.50 can be treated almost the same if their ranks are adjacent |
| No weights to tune | Its output score can't be used directly as a relevance threshold — it doesn't represent "how relevant," only "how well-agreed-upon" |
| Simple and robust in practice | |

**The alternative:** **score normalization** (e.g. min-max) followed by a weighted sum, e.g. `0.3 × BM25 + 0.7 × vector`. This preserves the magnitude of the differences but requires tuning and evaluating the weights. This is exactly what [OpenSearch](../../concepts/databases/search/opensearch.md)'s `hybrid` query type does via its search pipeline, while [Elasticsearch](../../concepts/databases/search/elasticsearch.md) supports both approaches.

---

## The one-line summary

**BM25** ranks keyword results, **vector search** ranks meaning-based results, **[hybrid search](../../concepts/ai/retrieval/hybrid-search.md)** is the decision to run both together, and **[RRF](../../concepts/ai/retrieval/reciprocal-rank-fusion.md)** is the most common way to merge their two rankings into one list.

## Related

- [BM25](../../concepts/ai/retrieval/bm25.md)
- [Hybrid Search](../../concepts/ai/retrieval/hybrid-search.md)
- [Reciprocal Rank Fusion (RRF)](../../concepts/ai/retrieval/reciprocal-rank-fusion.md)
- [Cross-Encoder Re-Ranking](../../concepts/ai/retrieval/cross-encoder-reranking.md) — the alternative/complementary merge strategy when magnitude and deeper relevance judgment matter more than [RRF](../../concepts/ai/retrieval/reciprocal-rank-fusion.md)'s rank-only approach
- [Vector Databases](../../concepts/ai/retrieval/vector-database.md)
- [Approximate Nearest Neighbor Search (ANN)](../../concepts/ai/retrieval/approximate-nearest-neighbor.md) / [HNSW](../../concepts/ai/retrieval/hnsw.md) — what the vector side of [hybrid search](../../concepts/ai/retrieval/hybrid-search.md) actually runs against
