# Azure AI Search

Azure AI Search (formerly **[Azure](azure.md) Cognitive Search**) is Microsoft's fully managed search-as-a-service — it indexes content and serves full-text ([BM25](../../ai/retrieval/bm25.md)), vector, and hybrid queries with built-in semantic re-ranking. It is the standard managed retrieval layer for enterprise [RAG](../../ai/rag/rag.md) on [Azure](azure.md), and the closest managed equivalent to a self-hosted pgvector + hybrid-search setup. It is part of the broader [Azure AI services](azure-ai-services.md) family and can be consumed directly via its own [REST](../../backend/api/rest.md) API/SDK, or through [Azure AI Foundry](azure-ai-foundry.md), which bundles it as the retrieval component behind [RAG](../../ai/rag/rag.md)-pattern apps built in the Foundry portal.

## What It Is

An Azure AI Search **index** is a schema of fields (text, numeric, geo, and vector fields) plus the documents stored against that schema:

```
Documents (JSON) → Indexer / push API → Search Index
                                              ├── Inverted index (BM25 full-text)
                                              ├── Vector index (HNSW / exhaustive kNN)
                                              └── Filterable / facetable metadata fields
```

- **[Inverted index](../../ai/retrieval/inverted-index.md)** — the data structure behind the [BM25](../../ai/retrieval/bm25.md) full-text side: term → list of documents, built once at indexing time.
- **[HNSW](../../ai/retrieval/hnsw.md) / exhaustive kNN** — [HNSW](../../ai/retrieval/hnsw.md) is the [approximate](../../ai/retrieval/approximate-nearest-neighbor.md) (fast, large-scale) vector index option; exhaustive kNN is exact brute-force search, usable when the field is small enough that approximation isn't needed.
- **Filterable / facetable metadata fields** — see [Vector Databases — Metadata filtering](../../ai/retrieval/vector-database.md#metadata-filtering) for how this same mechanism underpins permission-aware retrieval.

A single query request can run a full-text query, a vector query, or both at once (hybrid), optionally followed by semantic re-ranking — all against the same index.

## Hybrid Search Mechanics

[Hybrid search](../../ai/retrieval/hybrid-search.md) issues one query request containing both a `search` (keyword) parameter and one or more `vectorQueries`, which execute **in parallel** against the same index:

```
Query
  ├── Full-text search   → BM25 over the inverted index         → ranked list A
  └── Vector search       → HNSW / exhaustive kNN over embeddings → ranked list B
                                      ↓
                 Reciprocal Rank Fusion (RRF) merges A and B
                                      ↓
                    (optional) Semantic re-ranker re-scores top results
                                      ↓
                         Final ranked result set returned
```

- **[BM25](../../ai/retrieval/bm25.md)** over the **[inverted index](../../ai/retrieval/inverted-index.md)** handles exact terms — product codes, IDs, names, jargon — that [embeddings](../../ai/ingestion/embeddings.md) tend to blur.
- **Vector search** ([HNSW](../../ai/retrieval/hnsw.md) for approximate, exhaustive kNN for brute-force) handles conceptual/semantic matches regardless of exact wording.
- **[Reciprocal Rank Fusion (RRF)](../../ai/retrieval/reciprocal-rank-fusion.md)** merges the two ranked lists into one unified ranking without needing to normalize the two different scoring scales directly against each other.

Example hybrid query (abbreviated):

```json
POST /indexes/my-index/docs/search?api-version=2026-04-01
{
  "search": "historic hotel walk to restaurants",
  "vectorQueries": [
    { "kind": "vector", "vector": [ ... ], "k": 50, "fields": "DescriptionVector" }
  ],
  "filter": "department eq 'finance' and access_level le 2",
  "queryType": "semantic",
  "semanticConfiguration": "my-semantic-config"
}
```

## Semantic Ranking

Semantic ranking (`queryType=semantic`) is an optional second pass that applies a Microsoft-managed [cross-encoder](../../ai/retrieval/cross-encoder-reranking.md)/machine-reading-comprehension model to re-score the top candidates ([BM25](../../ai/retrieval/bm25.md), vector, or hybrid) using deeper language understanding than vector similarity or term frequency alone. Best practice: set vector `k=50` when combining with semantic ranking so the [re-ranker](../../ai/retrieval/cross-encoder-reranking.md) has enough candidates to work with — too aggressive a pre-filter starves it of input.

## Document-Level Access Control

Azure AI Search enforces nothing about user identity on its own — it answers whatever query it's given. Document-level permission enforcement is done by the calling application via **filterable metadata fields** on the index, most commonly `access_level` and `department`:

```json
"filter": "access_level le 2 and department eq 'engineering'"
```

The application is responsible for resolving the requesting user's permissions (e.g. via [Microsoft Entra ID](microsoft-entra-id.md) group membership) and injecting the correct `filter` clause into every query. A missing or wrong filter is a direct cross-department/cross-tenant data leak — this is the same gap called out in [Azure AI Foundry](azure-ai-foundry.md#what-azure-ai-foundry-does-not-do-automatically): identity and retrieval-time [authorization](../../security/authorization/authorization.md) are two separate concerns, and only the application connects them.

## Index Management

- **Indexers** can pull content automatically from supported sources (Blob Storage, [ADLS](adls.md) Gen2, [Azure](azure.md) [SQL](../../databases/relational/sql.md), Cosmos DB) on a schedule, re-indexing changed documents incrementally.
- Documents can also be **pushed** directly via the [REST](../../backend/api/rest.md) API/SDK for sources an indexer doesn't support.
- Index schema (fields, vector dimensions, semantic configuration) is defined up front; changing a vector field's dimensionality requires rebuilding the index.

## Pricing Tiers

| Tier | Storage per partition | Typical use |
|---|---|---|
| **Free** | 50 MB, 3 indexes | Tutorials, small demos — shared resources, no scaling |
| **Basic** | 15 GB/partition (45 GB max) | Small production workloads, up to 3 replicas for SLA |
| **Standard (S1/S2/S3)** | 160 GB / 512 GB / 1 TB per partition | Default production tier — scale partitions and replicas independently |
| **Storage Optimized (L1/L2)** | 2 TB / 4 TB per partition | Very large, infrequently-changing indexes; lower cost per TB, higher query latency |

## Azure AI Search vs pgvector

| | Azure AI Search | pgvector |
|---|---|---|
| Hosting | Fully managed SaaS | [PostgreSQL](../../databases/relational/postgresql.md) extension (self-managed or managed Postgres) |
| [Hybrid search](../../ai/retrieval/hybrid-search.md) | Built-in ([BM25](../../ai/retrieval/bm25.md) + vector + [RRF](../../ai/retrieval/reciprocal-rank-fusion.md)) | Manual (combine `tsvector` + vector similarity yourself) |
| Semantic re-ranking | Built-in managed [cross-encoder](../../ai/retrieval/cross-encoder-reranking.md) | Bring your own (e.g. a separate [re-ranker](../../ai/retrieval/cross-encoder-reranking.md) model/service) |
| Scale | Enterprise-scale, purpose-built for search | Good for small/moderate workloads; more manual tuning at scale |
| Best for | Enterprise [Azure](azure.md)-native [RAG](../../ai/rag/rag.md) with minimal ops | Projects already standardized on [PostgreSQL](../../databases/relational/postgresql.md) |

## Related

- [Azure AI Foundry](azure-ai-foundry.md) — the unified platform that bundles Azure AI Search as its [RAG](../../ai/rag/rag.md) retrieval layer; Azure AI Search can be consumed directly or through Foundry
- [Azure AI services](azure-ai-services.md) — the broader family of pre-built AI APIs that Azure AI Search sits alongside
- [Hybrid Search](../../ai/retrieval/hybrid-search.md) — the general hybrid-search concept this service implements
- [BM25](../../ai/retrieval/bm25.md) — the lexical scoring algorithm behind its full-text search side
- [Inverted Index](../../ai/retrieval/inverted-index.md) — the data structure [BM25](../../ai/retrieval/bm25.md) scores against
- [Reciprocal Rank Fusion (RRF)](../../ai/retrieval/reciprocal-rank-fusion.md) — the algorithm behind its hybrid-search merge step
- [Cross-Encoder Re-Ranking](../../ai/retrieval/cross-encoder-reranking.md) — the mechanism behind its semantic ranking feature
- [Text Analysis: Tokenization, Normalization, Stemming & Lemmatization](../../ai/retrieval/text-analysis.md) — the analyzer pipeline, including its `ar.microsoft`/`ar.lucene` Arabic-specific analyzers
- [Approximate Nearest Neighbor Search (ANN)](../../ai/retrieval/approximate-nearest-neighbor.md) / [HNSW](../../ai/retrieval/hnsw.md) — the vector-index algorithm behind its [HNSW](../../ai/retrieval/hnsw.md) option
- [Lucene](../../databases/search/lucene.md) — the shared engine behind [Elasticsearch](../../databases/search/elasticsearch.md)/[OpenSearch](../../databases/search/opensearch.md)/Solr, the comparable self-hosted alternatives to this managed service
- [Vector Database](../../ai/retrieval/vector-database.md)
- [RAG](../../ai/rag/rag.md)
- [Microsoft Entra ID](microsoft-entra-id.md) — identity layer that `access_level`/`department` filters enforce against
- [ADLS](adls.md) — common source an Azure AI Search indexer pulls documents from
- [Databricks](../data/databricks.md) — upstream pipeline that curates and chunks documents before they reach the index
