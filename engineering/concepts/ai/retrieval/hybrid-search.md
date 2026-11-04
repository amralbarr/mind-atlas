# Hybrid Search

## What is it?

Hybrid search combines **vector similarity search** (semantic, embedding-based) with **keyword/full-text search** (lexical, exact-term-based) in a single retrieval step, then merges the two result sets into one ranking. It exists because vector-only search and keyword-only search fail in opposite, complementary ways — combining them covers both failure modes at once.

```
Query: "PG-13 model number XR-4500 error code"

Vector-only search:
  Understands "error" and "model" conceptually,
  but embeddings blur exact identifiers like "XR-4500" —
  may return semantically similar but wrong-model results.

Keyword-only search:
  Finds exact matches for "XR-4500", but misses documents
  that describe the same issue using different wording
  ("unit won't power on" instead of "error code").

Hybrid search:
  Runs both, merges results → gets documents that either
  match the exact part number OR are semantically about the issue.
```

## Why not just vector search?

| Vector search alone | Keyword search alone | Hybrid |
|---|---|---|
| Great at synonyms, paraphrasing, "meaning" | Great at exact terms: IDs, codes, names, acronyms | Both |
| Weak on rare/specific tokens (product codes, error codes, proper nouns often embed poorly) | Weak on paraphrasing and synonyms | Covers both |
| Can return confidently-wrong "semantically close" results | Zero recall if the exact word isn't present | Balances precision and recall |

This matters directly for [RAG](../rag/rag.md): a [RAG](../rag/rag.md) system that only does vector search will systematically miss queries about specific SKUs, ticket numbers, legal clause references, or exact error strings — cases where lexical matching is what actually answers the question.

## How it works

Two searches run in parallel against the same corpus, then their results are combined:

```
Query
  ├── Vector search  → embed query → cosine/dot-product similarity → ranked list A
  └── Keyword search → tokenize query → BM25/TF-IDF full-text score  → ranked list B
                                              ↓
                              Merge A and B into one ranked list
                                              ↓
                                    Return top-N to the LLM
```

The vector side runs against an [ANN index](approximate-nearest-neighbor.md) (typically [HNSW](hnsw.md)) rather than comparing against every vector; the keyword side runs the query through the same [tokenization/normalization pipeline](text-analysis.md) used at indexing time, looks terms up in an [inverted index](inverted-index.md), and scores matches with **[BM25](bm25.md)** (Best Matching 25) — the standard lexical scoring algorithm today, which weighs term frequency against document length and term rarity across the corpus. Older systems (and the diagram above) sometimes reference **[TF-IDF](tf-idf.md)** instead — the simpler statistic [BM25](bm25.md) was built to improve on.

## Merging the two result sets

The two searches produce scores on different, incompatible scales (cosine similarity vs. [BM25](bm25.md) score), so they can't just be added together. Common merge strategies:

| Strategy | How it works |
|---|---|
| **Weighted sum (`alpha` blending)** | Normalize both score sets to 0–1, combine as `alpha * vector_score + (1 - alpha) * keyword_score`. `alpha = 1` is pure vector, `alpha = 0` is pure keyword. |
| **[Reciprocal Rank Fusion (RRF)](reciprocal-rank-fusion.md)** | Ignore raw scores entirely; combine based on each result's *rank position* in each list — `score = sum(1 / (k + rank))` across lists. More robust than score blending since it sidesteps the scale-mismatch problem. |
| **[Cross-encoder re-ranking](cross-encoder-reranking.md)** | Retrieve a larger candidate set from both searches, then pass all candidates through a separate [cross-encoder re-ranking](cross-encoder-reranking.md) model to produce the final order — more accurate, more expensive per query. |
| **[MMR](mmr.md)** | Not a merge strategy in itself, but often layered on afterward: re-ranks the merged result set to penalize near-duplicate results and favor diversity, rather than ordering purely by relevance. |

## Example (Weaviate)

```python
results = collection.query.hybrid(
    query="quarterly revenue",   # used for BOTH BM25 and vector search
    vector=embed("quarterly revenue"),
    alpha=0.5,                    # 0 = pure keyword, 1 = pure vector
    limit=5,
)
```

See [Weaviate](vector-stores/weaviate.md) for the full client example this is drawn from.

## Example (PostgreSQL: pgvector + full-text search)

Postgres has no single built-in "hybrid" call, but the same pattern is built manually by running a `tsvector` full-text query and a `pgvector` similarity query, then merging (often with [RRF](reciprocal-rank-fusion.md)) in application code or a combined [SQL](../../databases/relational/sql.md) query with `UNION`/`CTE`s:

```sql
-- Keyword side: PostgreSQL full-text search
SELECT id, ts_rank(to_tsvector('english', content), query) AS score
FROM documents, plainto_tsquery('english', 'quarterly revenue') query
WHERE to_tsvector('english', content) @@ query
ORDER BY score DESC LIMIT 20;

-- Vector side: pgvector cosine distance
SELECT id, embedding <=> '[0.1, 0.2, ...]' AS distance
FROM documents
ORDER BY distance LIMIT 20;

-- Merge both result sets (e.g. via RRF) in application code
```

See the [pgvector section of PostgreSQL](../../databases/relational/postgresql.md#pgvector-vector-search) for the vector-search half of this.

## Other Real Implementations

Several engines in this handbook support hybrid search natively rather than requiring manual merge code like the pgvector example above:

- **[Azure AI Search](../../cloud/azure/azure-ai-search.md)** — one query request with both a `search` ([BM25](bm25.md)) parameter and `vectorQueries`, merged via [RRF](reciprocal-rank-fusion.md), with an optional [cross-encoder semantic re-ranker](cross-encoder-reranking.md) pass on top.
- **[Elasticsearch](../../databases/search/elasticsearch.md)** — combine a regular `query` clause with a `knn` clause in the same search request.
- **[OpenSearch](../../databases/search/opensearch.md)** — a dedicated `hybrid` query type, with a search-pipeline stage to normalize the two score scales before combining them.

## When to use hybrid search

| Good fit | Skip it |
|---|---|
| Corpus contains identifiers, codes, names, or jargon that [embeddings](../ingestion/embeddings.md) handle poorly | Very small corpora where either search alone already performs well |
| Users search with a mix of natural-language questions and exact terms | Latency-critical paths where running two searches + merge isn't affordable |
| Domains with lots of acronyms/abbreviations (legal, medical, technical support) | Prototypes where simplicity matters more than recall (start vector-only, add hybrid later if recall is a measured problem) |

## Related

- [Retrieval-Augmented Generation (RAG)](../rag/rag.md) — the system hybrid search typically feeds into
- [BM25](bm25.md) — the lexical scoring algorithm behind the keyword half
- [TF-IDF](tf-idf.md) — the older statistic [BM25](bm25.md) improves on
- [Reciprocal Rank Fusion (RRF)](reciprocal-rank-fusion.md) — the standard merge strategy for the two result lists
- [Cross-Encoder Re-Ranking](cross-encoder-reranking.md) — the more expensive, more accurate second-pass alternative
- [MMR](mmr.md) — a diversity-focused second pass, often layered on the merged result set alongside or instead of re-ranking
- [BM25 vs. Hybrid Search vs. RRF](../../../overviews/ai/bm25-vs-hybrid-search-vs-rrf.md) — how these three relate, with a worked merge example
- [Inverted Index](inverted-index.md) — the data structure [BM25](bm25.md) scores against
- [Text Analysis: Tokenization, Normalization, Stemming & Lemmatization](text-analysis.md) — the pipeline that turns raw text into the terms the keyword half actually searches
- [Approximate Nearest Neighbor Search (ANN)](approximate-nearest-neighbor.md) / [HNSW](hnsw.md) — how the vector half actually executes at scale
- [Vector Databases](vector-database.md) — the semantic half of a hybrid search setup
- [Weaviate](vector-stores/weaviate.md) — a [vector database](vector-database.md) with hybrid search ([BM25](bm25.md) + vector) built in
- [Azure AI Search](../../cloud/azure/azure-ai-search.md) — managed hybrid search with built-in semantic re-ranking
- [Elasticsearch](../../databases/search/elasticsearch.md) and [OpenSearch](../../databases/search/opensearch.md) — combine `knn`/`hybrid` query clauses with BM25 natively
- [PostgreSQL](../../databases/relational/postgresql.md) — `pgvector` (vector) + `tsvector` (full-text) can be combined manually for the same effect
- [Agentic RAG](../rag/agentic-rag.md) — an agent can choose to run a hybrid search tool, or fall back to pure keyword search, based on the query
- [Embeddings](../ingestion/embeddings.md) — what powers the vector half of hybrid search
