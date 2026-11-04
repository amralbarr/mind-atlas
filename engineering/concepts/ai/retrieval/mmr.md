# MMR (Maximal Marginal Relevance)

## Not to be confused with MRR

**MMR** (this file) and **[MRR](../evaluation/mrr.md)** ([Mean Reciprocal Rank](../evaluation/mrr.md)) are two completely unrelated concepts that happen to share a near-identical acronym in the same part of this handbook. MMR is a **retrieval re-ranking/diversification technique** — it picks which results to return. [MRR](../evaluation/mrr.md) is an **evaluation metric** — it measures how high the first relevant result landed in an already-returned ranking. Double-check which one a source actually means before following a link; the one-letter difference ("Maximal Marginal **Relevance**" vs "Mean **Reciprocal** Rank") is easy to misread.

## What problem does this solve?

A plain top-k similarity search over a [vector database](vector-database.md) optimizes for one thing only: how close each result is to the query. That has a failure mode once a corpus contains several near-duplicate or highly similar chunks — the top-5 results can all be variations on the same paragraph (e.g. five chunks from slightly different revisions of the same policy document, all about "remote work eligibility"), while a genuinely different but still-relevant angle on the question never makes it into the returned set at all. The results are individually relevant but collectively redundant — wasted space in a [context window](../generation/context-window.md) that could have carried more distinct information.

MMR fixes this by re-ranking a candidate set to explicitly reward **diversity relative to what's already been selected**, not just raw similarity to the query.

## The original formulation

MMR was introduced by Carbonell and Goldstein in their 1998 SIGIR paper, *"The Use of MMR, Diversity-Based Reranking for Reordering Documents and Producing Summaries."* It builds a result set one item at a time, picking at each step the candidate that scores best on a combination of relevance and novelty:

```
MMR = argmax  [ λ · Sim1(D_i, Q) − (1 − λ) · max  Sim2(D_i, D_j) ]
      D_i ∉ S                              D_j ∈ S
```

- `Q` — the query
- `S` — the set of documents already selected into the result set
- `D_i` — a candidate document not yet selected
- `Sim1(D_i, Q)` — how relevant `D_i` is to the query (e.g. cosine similarity against the query embedding)
- `Sim2(D_i, D_j)` — how similar `D_i` is to a document already selected; only the single **most** similar already-selected document counts (the `max` term), since that's the one `D_i` would be most redundant with
- `λ ∈ [0, 1]` — the knob that balances the two terms

At each step, MMR picks whichever remaining candidate maximizes "how relevant is this" minus "how redundant is this with what I've already picked," then adds it to `S` and repeats until `k` results have been selected.

## The lambda parameter

`λ` is the whole mechanism: it's a single dial between two extremes.

- **`λ = 1`** — the redundancy term is zeroed out entirely; this degenerates into plain top-k similarity ranking, identical to not using MMR at all.
- **`λ = 0`** — the relevance term is zeroed out; results are selected purely to be maximally different from each other, with no regard for whether they answer the query at all.
- **A middle value (commonly `0.5`–`0.7` in practice)** — the useful range, where results stay meaningfully relevant to the query but a genuinely redundant near-duplicate gets penalized in favor of a more novel alternative.

There's no universally correct `λ`, same as `k` in [RRF](reciprocal-rank-fusion.md) — it's worth tuning against real queries and measuring the effect, rather than assuming a default transfers unchanged.

## Worked example

Query: *"What is our remote work policy?"* Candidate pool (already similarity-ranked, `fetch_k = 4`):

| Candidate | Sim to query | Content |
|---|---|---|
| A | 0.91 | "Employees may work remotely up to 3 days/week, manager approval required." |
| B | 0.90 | "Remote work requires manager approval; up to 3 days per week is standard." *(near-duplicate of A, different doc revision)* |
| C | 0.78 | "Remote employees must be reachable during core hours, 10am–3pm local time." |
| D | 0.60 | "The office kitchen is stocked on Mondays." |

Plain top-2 similarity search returns **A, B** — both near-identical restatements of the same rule, and the core-hours requirement (C) never surfaces.

MMR with `λ = 0.5`, selecting 2:

1. **Step 1:** no documents selected yet, so the redundancy term is 0 for everyone — pick the highest-relevance candidate: **A** (0.91).
2. **Step 2:** for each remaining candidate, compute `λ·Sim1 − (1−λ)·Sim2(vs. A)`.
   - B: `0.5(0.90) − 0.5(≈0.97 — near-duplicate of A)` = `0.45 − 0.485` ≈ **−0.035**
   - C: `0.5(0.78) − 0.5(≈0.25 — not very similar to A)` = `0.39 − 0.125` ≈ **0.265**
   - D is low-relevance and would lose on the first term regardless.
   - **C wins** despite B's higher raw similarity score, because B adds almost nothing A didn't already cover.

Final MMR result set: **A, C** — the core rule, plus the distinct "core hours" requirement — genuinely more useful in a bounded [context window](../generation/context-window.md) than A and its near-duplicate B.

## Where it fits in a RAG pipeline

```
Query
  → Vector search (or hybrid search)  → fetch_k candidates (wider than final k, e.g. 20–50)
  → MMR re-ranking                     → final top-k, diversity-adjusted
  → Return to LLM / user
```

MMR is applied to a widened initial candidate set (`fetch_k`), exactly like [cross-encoder re-ranking](cross-encoder-reranking.md) — fetch more than you need, then narrow with the more expensive/structured second pass. This matters specifically for [RAG](../rag/rag.md): a [context window](../generation/context-window.md) is a scarce, bounded resource, and five chunks that are all slight rewordings of the same fact are a worse use of that budget than three chunks that each add something the others didn't.

## MMR vs. cross-encoder re-ranking — related, not the same

Both sit in the same pipeline position (a second pass over an already-retrieved candidate set, before the final result set is returned), and both can run together, but they optimize for different things:

| | MMR | [Cross-encoder re-ranking](cross-encoder-reranking.md) |
|---|---|---|
| Optimizes for | **Diversity** — reducing redundancy among selected results | **Relevance ordering** — scoring how well each candidate actually answers the query |
| How | Penalizes candidates similar to already-selected results | Scores each query-candidate pair jointly with a model that reads both together |
| Fixes | Near-duplicate chunks crowding out distinct information | A relevant result buried low in the initial ranking (improves [MRR](../evaluation/mrr.md)) |
| Cost | Cheap — reuses [embeddings](../ingestion/embeddings.md) already computed for retrieval | Expensive — a separate model inference per candidate |

They address different failure modes and are not substitutes: a candidate set can be maximally diverse (good MMR outcome) while the actual best-matching chunk is still ranked lower than a mediocre one (a [cross-encoder](cross-encoder.md) would fix that), or vice versa. Pipelines that need both typically run [cross-encoder re-ranking](cross-encoder-reranking.md) to fix ordering first, then MMR to trim the final selection for diversity — or the reverse, depending on which failure mode the corpus exhibits more.

## How it's actually implemented

MMR requires access to the embedding vectors of both the query and every candidate (to compute `Sim2` between candidates), which is more than a typical similarity-search API call returns — so support varies by where that computation happens:

| Tool | Support | Notes |
|---|---|---|
| **[LangChain](../agents/langchain.md)** (`max_marginal_relevance_search`) | Client-side, generic | Implemented once in `langchain_core` against any vector store that returns [embeddings](../ingestion/embeddings.md) alongside results — fetches `fetch_k` candidates, then runs the MMR selection algorithm in Python. Exposes `k`, `fetch_k`, and `lambda_mult` (`1` = minimum diversity, `0` = maximum diversity — note this is the **inverse** of [Qdrant](vector-stores/qdrant.md)'s `diversity` parameter below). The naive implementation is O(n²) in `fetch_k` and is only intended for small candidate sets (well under 1,000). |
| **[Qdrant](vector-stores/qdrant.md)** | Native, server-side (added 2025) | Exposed directly on a `NearestQuery` via an `mmr` parameter: `diversity` (`0.0` = pure relevance, `1.0` = pure diversity — the opposite convention from [LangChain](../agents/langchain.md)'s `lambda_mult`) and `candidates_limit` (the candidate pool size before MMR selection, equivalent to `fetch_k`). |
| **[Pinecone](vector-stores/pinecone.md)** | No native support | No server-side MMR parameter as of this writing; users needing it typically fetch a wider candidate set and run [LangChain](../agents/langchain.md)'s client-side MMR on top. |
| **`pgvector`** | No native support | Same pattern as [Pinecone](vector-stores/pinecone.md) — MMR has to be computed in application code (or via [LangChain](../agents/langchain.md)) against a fetched candidate set, not inside the [SQL](../../databases/relational/sql.md) query itself. |
| **[ChromaDB](vector-stores/chromadb.md) / [FAISS](vector-stores/faiss.md) / [Weaviate](vector-stores/weaviate.md)** | Supported via [LangChain](../agents/langchain.md)'s generic client-side method | These don't implement MMR as a native query-time feature of the engine itself, but [LangChain](../agents/langchain.md)'s `VectorStore` base class provides `max_marginal_relevance_search` against any store that can return [embeddings](../ingestion/embeddings.md) with results, which covers all three. |

The practical takeaway: assume MMR is a client-side post-processing step layered on top of a normal similarity search unless the specific engine is documented as computing it natively ([Qdrant](vector-stores/qdrant.md), currently, is the one clear exception in this list) — don't assume a vector store supports it server-side just because it's a popular, well-known feature.

## Related

- [Vector Databases](vector-database.md) — MMR needs each candidate's embedding, which is why support depends on what a given store returns alongside search results
- [Hybrid Search](hybrid-search.md) — a different post-retrieval concern (combining lexical and semantic signals) that MMR is often layered after, not instead of
- [Cross-Encoder Re-Ranking](cross-encoder-reranking.md) — the relevance-ordering counterpart to MMR's diversity focus; the two solve different problems and can be combined
- [Reciprocal Rank Fusion (RRF)](reciprocal-rank-fusion.md) — another rank-manipulation technique, but for merging two ranked lists rather than diversifying one
- [MRR](../evaluation/mrr.md) — an unrelated evaluation metric with a near-identical acronym; see the disambiguation note above
- [Qdrant](vector-stores/qdrant.md) — currently the vector store in this handbook's options with native server-side MMR
- [Retrieval-Augmented Generation (RAG)](../rag/rag.md) — the system MMR typically improves by making better use of a bounded [context window](../generation/context-window.md)
