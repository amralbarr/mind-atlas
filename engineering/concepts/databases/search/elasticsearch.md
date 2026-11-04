# Elasticsearch

Elasticsearch is a distributed document store and search engine built on [Apache Lucene](lucene.md) — it stores [JSON](../../programming/fundamentals/json.md) documents, indexes every field automatically, and exposes search, aggregation, and analytics through a [REST](../../backend/api/rest.md) API. Its original and still-dominant identity is full-text search: every text field is backed by an [inverted index](../../ai/retrieval/inverted-index.md), scored with [BM25](../../ai/retrieval/bm25.md) by default. Since version 8.0 it also supports storing and searching embedding vectors natively, making it one of the "vector search added to a general-purpose [database](../../ai/retrieval/vector-database.md)" options rather than a purpose-built vector store.

## Core Concepts

| Term | Meaning |
|---|---|
| **Document** | A single [JSON](../../programming/fundamentals/json.md) record — the unit of storage and retrieval |
| **Index** | A named collection of documents with a shared mapping — roughly analogous to a [SQL](../relational/sql.md) table |
| **Mapping** | The schema for an index: field names, types (`text`, `keyword`, `dense_vector`, etc.) and how each is indexed |
| **Shard** | A horizontal partition of an index's data — [Lucene](lucene.md) index under the hood — spread across nodes for scale |
| **Replica** | A copy of a shard on a different node, for both high availability and read throughput |
| **Cluster** | A set of nodes working together, coordinated by an elected master node |
| **Node** | A single running Elasticsearch instance, with a role (data, master-eligible, ingest, etc.) |

## Installation

```bash
# Docker (single node, dev)
docker run -d --name elasticsearch \
  -p 9200:9200 -p 9300:9300 \
  -e "discovery.type=single-node" \
  -e "xpack.security.enabled=false" \
  docker.elastic.co/elasticsearch/elasticsearch:8.15.0
```

## REST API

Every operation — indexing, searching, cluster administration — is an [HTTP](../../networking/http.md) call against the node:

```bash
# Create an index with an explicit mapping
curl -X PUT "localhost:9200/products" -H 'Content-Type: application/json' -d '{
  "mappings": {
    "properties": {
      "name":        { "type": "text" },
      "category":    { "type": "keyword" },
      "price":       { "type": "float" }
    }
  }
}'

# Index a document
curl -X POST "localhost:9200/products/_doc/1" -H 'Content-Type: application/json' -d '{
  "name": "Wireless mouse",
  "category": "electronics",
  "price": 19.99
}'

# Full-text search (Query DSL)
curl -X GET "localhost:9200/products/_search" -H 'Content-Type: application/json' -d '{
  "query": { "match": { "name": "wireless mouse" } }
}'
```

`keyword` fields are matched exactly (used for filtering, aggregation, sorting); `text` fields are run through an [analyzer](../../ai/retrieval/text-analysis.md) (tokenized, lowercased, stemmed) and matched via [BM25](../../ai/retrieval/bm25.md) relevance scoring through the [inverted index](../../ai/retrieval/inverted-index.md) Elasticsearch builds automatically for them — this is what makes `match` queries find "wireless mice" when the document says "mouse" (via [stemming](../../ai/retrieval/analyzer-pipeline/stemming.md)), without needing exact string equality. Elasticsearch ships built-in language analyzers for this, including an `arabic` analyzer (Arabic-specific normalization — letter-variant folding, diacritic stripping — plus Arabic [stemming](../../ai/retrieval/analyzer-pipeline/stemming.md)) rather than falling back to the generic English-tuned default.

## Vector Search (`dense_vector` + kNN)

Elasticsearch stores embedding vectors in a `dense_vector` field and searches them with [approximate kNN](../../ai/retrieval/approximate-nearest-neighbor.md) backed by [HNSW](../../ai/retrieval/hnsw.md):

```bash
# Mapping: add a dense_vector field
curl -X PUT "localhost:9200/articles" -H 'Content-Type: application/json' -d '{
  "mappings": {
    "properties": {
      "content":   { "type": "text" },
      "embedding": {
        "type": "dense_vector",
        "dims": 1536,
        "index": true,
        "similarity": "cosine"
      }
    }
  }
}'

# Approximate kNN search
curl -X GET "localhost:9200/articles/_search" -H 'Content-Type: application/json' -d '{
  "knn": {
    "field": "embedding",
    "query_vector": [0.12, -0.34, 0.87, ...],
    "k": 5,
    "num_candidates": 100
  }
}'
```

| Parameter | Meaning |
|---|---|
| `dims` | Vector dimensionality — must match the embedding model's output size |
| `similarity` | Distance metric: `cosine` (default), `dot_product`, `l2_norm` |
| `index_options` | [HNSW](../../ai/retrieval/hnsw.md) tuning — `m` (graph connections per node) and `ef_construction` (build-time search width), the same parameters described in [HNSW](../../ai/retrieval/hnsw.md) |
| `k` | How many nearest neighbors to return |
| `num_candidates` | How many candidates each shard considers before the final top-`k` is picked — the `ef_search`-equivalent recall/speed knob |

Recent Elasticsearch versions quantize float vectors automatically (`int8_hnsw`, and `bbq`-based quantization for larger models) to cut the memory footprint of the [HNSW](../../ai/retrieval/hnsw.md) graph, trading a small amount of recall for significantly less RAM per vector.

### Hybrid search

The `knn` top-level search parameter runs alongside a regular `query` clause in the same request — Elasticsearch merges the lexical ([BM25](../../ai/retrieval/bm25.md)) matches and the vector matches into one ranked response, which is the [hybrid search](../../ai/retrieval/hybrid-search.md) pattern applied natively inside a single engine rather than merged in application code:

```bash
curl -X GET "localhost:9200/articles/_search" -H 'Content-Type: application/json' -d '{
  "query": {
    "match": { "content": "quarterly revenue" }
  },
  "knn": {
    "field": "embedding",
    "query_vector": [0.12, -0.34, 0.87, ...],
    "k": 5,
    "num_candidates": 100
  },
  "size": 5
}'
```

A `knn` clause can also be nested inside a `bool` query alongside `filter`/`must` clauses, so metadata filtering and vector search apply together in a single request.

## Elasticsearch vs OpenSearch

[OpenSearch](opensearch.md) is a 2021 fork of Elasticsearch 7.10.2, created after Elastic relicensed Elasticsearch away from Apache 2.0. The two share the same [Lucene](lucene.md)-based core, [REST](../../backend/api/rest.md) API shape, and cluster/shard/replica model, but have drifted since the fork — see [OpenSearch](opensearch.md#elasticsearch-vs-opensearch) for the licensing history and the concrete API/feature differences that have accumulated (notably: Elasticsearch's `knn`/`dense_vector` API described above vs. [OpenSearch](opensearch.md)'s separate k-NN plugin with its own `knn_vector` field type and engine choice). [Apache Solr](solr.md) is the third major [Lucene](lucene.md)-based engine in this space — older than both, and the one Elasticsearch itself displaced as the default open-source choice for most new projects after 2010; see [Solr's comparison table](solr.md#comparison-solr-vs-elasticsearch-vs-opensearch) for the full three-way breakdown.

## Related

- [OpenSearch](opensearch.md) — the Apache-2.0-licensed fork, near-identical core with its own k-NN plugin
- [Apache Solr](solr.md) — the older [Lucene](lucene.md)-based engine Elasticsearch displaced as the default open-source choice for most new projects after 2010
- [Lucene](lucene.md) — the library Elasticsearch actually embeds as its core engine
- [BM25](../../ai/retrieval/bm25.md) — the lexical scoring algorithm behind Elasticsearch's default text relevance
- [Text Analysis: Tokenization, Normalization, Stemming & Lemmatization](../../ai/retrieval/text-analysis.md) — the analyzer pipeline, including the built-in `arabic` analyzer
- [Inverted Index](../../ai/retrieval/inverted-index.md) — the structure behind Elasticsearch's full-text search
- [Approximate Nearest Neighbor Search (ANN)](../../ai/retrieval/approximate-nearest-neighbor.md) / [HNSW](../../ai/retrieval/hnsw.md) — the algorithm behind Elasticsearch's `knn` search
- [Hybrid Search](../../ai/retrieval/hybrid-search.md) — combining `knn` with regular query clauses
- [Vector Databases](../../ai/retrieval/vector-database.md) — where Elasticsearch fits among vector store options
- [PostgreSQL (`pgvector`)](../relational/postgresql.md#pgvector-vector-search) — the equivalent "vector search bolted onto a general-purpose database" pattern in the relational world
