# OpenSearch

OpenSearch is a distributed document store and search engine forked from [Elasticsearch](elasticsearch.md) 7.10.2 in 2021. It shares [Elasticsearch](elasticsearch.md)'s [Lucene](lucene.md)-based core, [REST](../../backend/api/rest.md) API shape, and cluster/shard/replica model almost exactly — most [Elasticsearch](elasticsearch.md) 7.10-era API calls work against OpenSearch unchanged — but the two have diverged since the fork, most visibly in how each handles vector search.

## Why it exists

In January 2021, Elastic (the company behind [Elasticsearch](elasticsearch.md)) relicensed [Elasticsearch](elasticsearch.md) and Kibana away from Apache 2.0 to a dual Server Side Public License (SSPL) / Elastic License model, citing [cloud providers](../../../overviews/cloud/cloud-providers.md) — specifically [AWS](../../cloud/infrastructure/aws.md) — offering [Elasticsearch](elasticsearch.md) as a managed service without contributing back. [AWS](../../cloud/infrastructure/aws.md) responded by forking the last Apache-2.0 release (7.10.2) into OpenSearch, shipping 1.0 in mid-2021 and keeping it permissively licensed (Apache 2.0) under the Linux Foundation-governed OpenSearch Project. Elastic later (2024) added the AGPLv3 as a third licensing option alongside SSPL and the Elastic License, but Elasticsearch itself remains differently licensed from OpenSearch's unconditional Apache 2.0.

## Core Concepts

Identical in name and role to Elasticsearch, inherited directly from the shared 7.10.2 ancestor:

| Term | Meaning |
|---|---|
| **Document** | A single [JSON](../../programming/fundamentals/json.md) record |
| **Index** | A named collection of documents with a shared mapping |
| **Shard** | A horizontal partition of an index, backed by a [Lucene](lucene.md) index |
| **Replica** | A copy of a shard on another node, for availability and read scale |
| **Cluster / Node** | The set of coordinated instances, and a single running instance within it |

```bash
# Docker (single node, dev)
docker run -d --name opensearch \
  -p 9200:9200 -p 9600:9600 \
  -e "discovery.type=single-node" \
  opensearchproject/opensearch:2.17.0

# REST API — near-identical to Elasticsearch's
curl -X POST "localhost:9200/products/_doc/1" -H 'Content-Type: application/json' -d '{
  "name": "Wireless mouse", "category": "electronics", "price": 19.99
}'
```

Full-text search works the same way as Elasticsearch: `text` fields are run through an [analyzer](../../ai/retrieval/text-analysis.md) and matched via [BM25](../../ai/retrieval/bm25.md) through an [inverted index](../../ai/retrieval/inverted-index.md) built automatically per index — including the same built-in language-specific analyzers (e.g. `arabic`), inherited from the shared [Lucene](lucene.md) analysis components both engines build on.

## k-NN Plugin

Unlike Elasticsearch, where vector search is a built-in `dense_vector` field type, OpenSearch's vector support ships as a separate **k-NN plugin** (bundled by default in the standard distribution) with its own field type, `knn_vector`:

```bash
# Mapping: knn_vector field with an explicit method
curl -X PUT "localhost:9200/articles" -H 'Content-Type: application/json' -d '{
  "settings": { "index.knn": true },
  "mappings": {
    "properties": {
      "content": { "type": "text" },
      "embedding": {
        "type": "knn_vector",
        "dimension": 1536,
        "method": {
          "name": "hnsw",
          "space_type": "cosinesimil",
          "engine": "faiss",
          "parameters": { "ef_construction": 128, "m": 16 }
        }
      }
    }
  }
}'

# Approximate k-NN search
curl -X GET "localhost:9200/articles/_search" -H 'Content-Type: application/json' -d '{
  "size": 5,
  "query": {
    "knn": { "embedding": { "vector": [0.12, -0.34, 0.87, ...], "k": 5 } }
  }
}'
```

### Engine choices

The `method.engine` setting picks which underlying library builds and searches the vector index — this is OpenSearch-specific; Elasticsearch has no equivalent choice:

| Engine | What it is | Notes |
|---|---|---|
| **`faiss`** | Meta's [FAISS](../../ai/retrieval/vector-stores/faiss.md) library | Default and recommended for most and especially large-scale deployments; supports both [HNSW](../../ai/retrieval/hnsw.md) and IVF methods, plus quantization (PQ) to shrink memory footprint |
| **`lucene`** | OpenSearch's underlying [Lucene](lucene.md) engine's native vector support | Good for smaller deployments; integrates tightly with [Lucene](lucene.md)'s own query execution, which enables "smart" automatic filtering strategy selection (pre-filter, post-filter, or exact k-NN, chosen per query) |
| **`nmslib`** (legacy) | The original engine OpenSearch's k-NN plugin shipped with | Deprecated in OpenSearch 2.16, removed entirely in 3.0 — new mappings should use `faiss` or `lucene` |

### Methods and approximate vs. exact k-NN

| Method | Idea | Needs training? |
|---|---|---|
| **[HNSW](../../ai/retrieval/hnsw.md)** | Graph-based [ANN](../../ai/retrieval/approximate-nearest-neighbor.md), same algorithm underlying Elasticsearch's and most other [vector databases](../../ai/retrieval/vector-database.md)' default index | No — built incrementally |
| **IVF** | Clusters vectors first (k-means), then searches only the nearest clusters | Yes — requires a training step on a representative sample before vectors can be added ([FAISS](../../ai/retrieval/vector-stores/faiss.md) engine only) |

Both are **approximate** k-NN — fast, [HNSW](../../ai/retrieval/hnsw.md)/IVF-indexed, and the default for any real-scale deployment. OpenSearch also supports **exact k-NN** (brute-force, no index, compares the query against every vector) for small datasets or as a recall baseline to benchmark approximate results against, mirroring the exact-vs-approximate trade-off described in [ANN](../../ai/retrieval/approximate-nearest-neighbor.md) / [HNSW](../../ai/retrieval/hnsw.md).

`space_type` picks the distance metric (`l2`, `cosinesimil`, `innerproduct`, etc.) — the OpenSearch-specific naming for what Elasticsearch calls `similarity`.

### Hybrid search

OpenSearch combines lexical and vector search via a dedicated **`hybrid` query type**, run through a **search pipeline** that normalizes and combines the two score sets (since raw [BM25](../../ai/retrieval/bm25.md) scores and raw vector-similarity scores aren't on comparable scales — the same normalization problem [Hybrid Search](../../ai/retrieval/hybrid-search.md) describes generally):

```bash
curl -X GET "localhost:9200/articles/_search?search_pipeline=hybrid-search-pipeline" -H 'Content-Type: application/json' -d '{
  "query": {
    "hybrid": {
      "queries": [
        { "match": { "content": "quarterly revenue" } },
        { "knn": { "embedding": { "vector": [0.12, -0.34, 0.87, ...], "k": 5 } } }
      ]
    }
  }
}'
```

The `search_pipeline` applies a normalization processor (e.g. min-max or z-score normalization) to both result sets before combining them — functionally the same goal as the weighted-sum/[RRF](../../ai/retrieval/reciprocal-rank-fusion.md) merge strategies in [Hybrid Search](../../ai/retrieval/hybrid-search.md), implemented as a server-side pipeline stage rather than application code.

## Elasticsearch vs OpenSearch

| | Elasticsearch | OpenSearch |
|---|---|---|
| License | Triple-licensed: AGPLv3 / SSPL / Elastic License 2.0 | Apache 2.0 |
| Governance | Elastic (company) | OpenSearch Project (Linux Foundation) |
| Vector field | Built-in `dense_vector` type, native `knn` search option | Separate k-NN plugin, `knn_vector` type |
| Vector engine choice | None exposed — Elasticsearch manages [HNSW](../../ai/retrieval/hnsw.md) internally | Explicit `engine` choice: `faiss` (default), `lucene`, or legacy `nmslib` (removed in 3.0) |
| [Hybrid search](../../ai/retrieval/hybrid-search.md) | `knn` + `query` combined in one request body | Dedicated `hybrid` query type + search pipeline normalization |
| [AWS](../../cloud/infrastructure/aws.md) managed offering | "Amazon Elasticsearch Service" was rebranded away; [AWS](../../cloud/infrastructure/aws.md) now offers Elasticsearch separately under Elastic's licensing terms | **Amazon OpenSearch Service** — [AWS](../../cloud/infrastructure/aws.md)'s own managed offering, unsurprisingly, given OpenSearch is an AWS-originated fork |
| Common cloud default | Elastic Cloud (Elastic's own managed service) | Amazon OpenSearch Service; also used internally by some other providers' "Elasticsearch-compatible" offerings |

Both remain close enough at the [REST](../../backend/api/rest.md)/query-DSL level that most non-vector workloads port between them with minimal changes — the real decision point in practice is licensing posture and which vector/k-NN API shape a team is already invested in. [Apache Solr](solr.md#comparison-solr-vs-elasticsearch-vs-opensearch) is the third [Lucene](lucene.md)-based option in this space — older than both, Apache-2.0-licensed like OpenSearch, but with the newest and least turnkey vector/[hybrid search](../../ai/retrieval/hybrid-search.md) of the three; see its comparison table for the full three-way breakdown.

## Related

- [Elasticsearch](elasticsearch.md) — the project OpenSearch forked from, with native `dense_vector`/`knn` instead of a separate plugin
- [Apache Solr](solr.md) — the older Lucene-based, Apache-2.0-licensed search engine; shares OpenSearch's permissive licensing but with a smaller, newer vector-search feature set
- [Lucene](lucene.md) — the library OpenSearch's `lucene` k-NN engine option and full-text search both build on
- [BM25](../../ai/retrieval/bm25.md) — the lexical scoring algorithm behind OpenSearch's default text relevance
- [Text Analysis: Tokenization, Normalization, Stemming & Lemmatization](../../ai/retrieval/text-analysis.md) — the analyzer pipeline, inherited from the shared Lucene lineage
- [Inverted Index](../../ai/retrieval/inverted-index.md) — the structure behind OpenSearch's full-text search
- [Approximate Nearest Neighbor Search (ANN)](../../ai/retrieval/approximate-nearest-neighbor.md) / [HNSW](../../ai/retrieval/hnsw.md) — the algorithm behind the k-NN plugin's `hnsw` method
- [Hybrid Search](../../ai/retrieval/hybrid-search.md) — the general pattern OpenSearch's `hybrid` query type implements natively
- [Vector Databases](../../ai/retrieval/vector-database.md) — where OpenSearch fits among vector store options
- [PostgreSQL (`pgvector`)](../relational/postgresql.md#pgvector-vector-search) — the equivalent "vector search bolted onto a general-purpose database" pattern in the relational world
