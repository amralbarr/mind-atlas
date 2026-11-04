# Apache Solr

Apache Solr is a distributed document store and search engine built on [Apache Lucene](lucene.md) — the same indexing library [Elasticsearch](elasticsearch.md) and [OpenSearch](opensearch.md) are also built on. Solr predates both: it's been an Apache top-level project since 2006, roughly five years before [Elasticsearch](elasticsearch.md) existed, and for a long stretch of the 2010s was the default choice for open-source full-text search at scale. Like its younger siblings, every text field is backed by an [inverted index](../../ai/retrieval/inverted-index.md) and scored with [BM25](../../ai/retrieval/bm25.md) by default, and since version 9.0 it also supports native dense-vector/k-NN search, making it a third "vector search added to a general-purpose [database](../../ai/retrieval/vector-database.md)" option alongside [Elasticsearch](elasticsearch.md) and [OpenSearch](opensearch.md).

## Core Concepts

| Term | Meaning |
|---|---|
| **Document** | A single record — the unit of storage and retrieval |
| **Collection** | A named, logical index spread across the cluster — Solr's equivalent of an [Elasticsearch](elasticsearch.md)/[OpenSearch](opensearch.md) "index" |
| **Shard** | A horizontal partition of a collection's data — a [Lucene](lucene.md) index under the hood — spread across nodes for scale |
| **Replica** | A copy of a shard on a different node, for both high availability and read throughput |
| **SolrCloud** | Solr's distributed/clustered operating mode — multiple nodes, sharded and replicated collections, coordinated via Apache ZooKeeper rather than Solr's own elected-master model |
| **Schema** | The field definitions for a collection: field names, types (`text_general`, `string`, `knn_vector`/`DenseVectorField`, etc.) and how each is indexed — either a manually maintained `schema.xml` or, more commonly today, a **managed schema** (`managed-schema.xml`) editable at runtime through the Schema API |

Solr can also run in a legacy **standalone mode** (single node or manually sharded "SolrCore" instances, no ZooKeeper) but SolrCloud is the mode any production or multi-node deployment uses today.

## Installation

```bash
# Docker (single node, dev) — starts Solr and pre-creates a collection
docker run -d --name solr -p 8983:8983 solr:9.6 solr-precreate gettingstarted

# Or via the bundled control script after a local install
bin/solr start -c                          # -c starts in SolrCloud mode
bin/solr create -c products                # create a collection named "products"
```

## REST API

Like [Elasticsearch](elasticsearch.md) and [OpenSearch](opensearch.md), every operation is an [HTTP](../../networking/http.md) call against a node (or, in SolrCloud, any node — requests are routed to the right shard automatically):

```bash
# Index documents (JSON array of docs)
curl http://localhost:8983/solr/products/update?commit=true \
  -H 'Content-Type: application/json' -d '[
    { "id": "1", "name_t": "Wireless mouse", "category_s": "electronics", "price_f": 19.99 }
  ]'

# Full-text search
curl "http://localhost:8983/solr/products/select?q=name_t:wireless+mouse"

# Create a collection via the Collections API
curl "http://localhost:8983/solr/admin/collections?action=CREATE&name=products&numShards=1&replicationFactor=2&collection.configName=_default"
```

Solr's historical convention is to encode the field type in the field name's suffix (`_t` text, `_s` string, `_f` float, `_i` int) via "dynamic fields" in the schema, rather than declaring every field explicitly — a schemaless-friendly pattern that predates [Elasticsearch](elasticsearch.md)'s automatic field mapping and still shows up constantly in Solr examples and existing deployments.

`text_general` (and language-specific variants) fields are run through an **analyzer chain** (tokenized, lowercased, stemmed) and matched via [BM25](../../ai/retrieval/bm25.md) relevance scoring through the [inverted index](../../ai/retrieval/inverted-index.md) Solr builds automatically for them. [BM25](../../ai/retrieval/bm25.md) has been Solr's **default similarity since version 6.0** (2016) — before that, Solr defaulted to the older "classic" [TF-IDF](../../ai/retrieval/tf-idf.md)-based `ClassicSimilarity`. Solr 8.x (via [LUCENE-8563](https://issues.apache.org/jira/browse/LUCENE-8563)) tweaked the underlying [BM25](../../ai/retrieval/bm25.md) formula slightly (dropping a `(k1+1)` factor from the numerator that doesn't affect relative ranking); the pre-8.x exact formula is still available as the deprecated `LegacyBM25SimilarityFactory`. As with Elasticsearch/[OpenSearch](opensearch.md), `k1` (term-frequency saturation, default `1.2`) and `b` (length normalization, default `0.75`) are configurable per field type.

## Vector Search (`DenseVectorField` + k-NN query parser)

Solr added native dense-vector support in **version 9.0** (2022) — notably later than Elasticsearch (8.0) and [OpenSearch](opensearch.md)'s k-NN plugin, which is one of the real reasons teams evaluating vector/[hybrid search](../../ai/retrieval/hybrid-search.md) today default to the other two. Vectors are declared with the `solr.DenseVectorField` field type and queried with a dedicated `{!knn}` query parser, both backed by [Lucene](lucene.md)'s own [HNSW](../../ai/retrieval/hnsw.md) implementation — the same underlying [Lucene](lucene.md) vector support OpenSearch's `lucene` engine option uses:

```xml
<!-- schema: declare a DenseVectorField type and a field using it -->
<fieldType name="knn_vector" class="solr.DenseVectorField"
           vectorDimension="1536"
           similarityFunction="cosine"
           knnAlgorithm="hnsw"
           hnswM="16"
           hnswEfConstruction="100"/>
<field name="embedding" type="knn_vector" indexed="true" stored="true"/>
```

```bash
# k-NN query via the {!knn} query parser, as a filter query combined with topK
curl "http://localhost:8983/solr/articles/select" -d '
  q={!knn f=embedding topK=5}[0.12,-0.34,0.87,...]'
```

| Parameter | Meaning |
|---|---|
| `vectorDimension` | Vector dimensionality — must match the embedding model's output size |
| `similarityFunction` | Distance metric: `euclidean` (default), `dot_product`, or `cosine` |
| `knnAlgorithm` | Indexing algorithm — `hnsw` is the default and only built-in option |
| `hnswM` | Graph connections per node, default `16` — the same `m` parameter described in [HNSW](../../ai/retrieval/hnsw.md) |
| `hnswEfConstruction` | Build-time search width, default `100` |
| `f` | The `DenseVectorField` to search, in the `{!knn}` query |
| `topK` | How many nearest neighbors to return, default `10` |

### Hybrid search

Solr has no single dedicated "hybrid" query type the way OpenSearch does — instead, a `{!knn}` clause is combined with a regular lexical query the same way any two Solr query clauses combine, typically as a boolean/boosted query or by running the k-NN clause as a `fq` (filter query) or re-ranking clause (`rq`) layered on top of a [BM25](../../ai/retrieval/bm25.md) `q`. This is functionally the same [hybrid search](../../ai/retrieval/hybrid-search.md) goal as Elasticsearch's combined `query`+`knn` request body and OpenSearch's `hybrid` query type, but it's assembled from Solr's general-purpose query composition primitives rather than a purpose-built hybrid API — one more place Solr's vector tooling is newer and less turnkey than its two competitors'.

## Why choose Solr vs. Elasticsearch/OpenSearch today

Solr is not the default pick for a new project in 2026 — Elasticsearch and OpenSearch have far larger ecosystems, more mature vector/[hybrid search](../../ai/retrieval/hybrid-search.md), and (for OpenSearch) a permissive license with less licensing churn than Elastic's history. But Solr still shows up for real reasons:

- **Existing large-scale deployments.** Solr has been the backbone of search at a number of very large, long-running platforms (e.g. it has powered search at sites like DuckDuckGo, Instagram in earlier years, and remains common at organizations that built on it before Elasticsearch existed) — migrating off a working, tuned, multi-shard Solr deployment is a significant undertaking most teams don't take on without a forcing reason.
- **SolrCloud + ZooKeeper operational model.** Teams already running ZooKeeper for other coordination needs, or who prefer ZooKeeper's explicit, battle-tested consensus model over Elasticsearch's internal master-election, sometimes prefer Solr's architecture on those grounds alone.
- **Mature non-vector feature set.** Solr's faceting, highlighting, and rich query-parser ecosystem (`edismax`, function queries, learning-to-rank plugin) are deep and well-documented after two decades of production use — for lexical-search-heavy use cases that don't need vectors, the maturity gap with Elasticsearch/OpenSearch is small to nonexistent.
- **Apache governance, Apache 2.0 license.** Like OpenSearch, Solr has never had Elastic's SSPL/Elastic-License relicensing event — it's a straightforward Apache Software Foundation project under Apache 2.0, which matters to the same class of buyer OpenSearch's licensing appeals to.

What it doesn't have going for it: vector search arrived two-plus years after Elasticsearch's, there's no single built-in hybrid-search API, and community/mindshare momentum for *new* projects has clearly shifted to Elasticsearch and OpenSearch — most new tutorials, managed-cloud offerings, and [RAG](../../ai/rag/rag.md)-stack integrations target those two first.

## Comparison: Solr vs Elasticsearch vs OpenSearch

|                        | Solr                                                                                                   | Elasticsearch                                                                  | OpenSearch                                                                 |
| ---------------------- | ------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------ | -------------------------------------------------------------------------- |
| First released         | 2006                                                                                                   | 2010                                                                           | 2021 (fork of ES 7.10.2)                                                   |
| License                | Apache 2.0                                                                                             | Triple-licensed: AGPLv3 / SSPL / Elastic License 2.0                           | Apache 2.0                                                                 |
| Governance             | Apache Software Foundation                                                                             | Elastic (company)                                                              | OpenSearch Project (Linux Foundation)                                      |
| Clustering             | SolrCloud, coordinated via ZooKeeper                                                                   | Internal master-eligible node election                                         | Internal master-eligible node election (inherited from ES)                 |
| Vector field           | `DenseVectorField` (since 9.0, 2022)                                                                   | Built-in `dense_vector` type (since 8.0)                                       | Separate k-NN plugin, `knn_vector` type                                    |
| Vector search maturity | Newest of the three; [Lucene](lucene.md)/[HNSW](../../ai/retrieval/hnsw.md) only, no engine choice                                                | Mature; quantization (`int8_hnsw`, `bbq`) built in                             | Mature; engine choice (`faiss`, `lucene`), IVF + [HNSW](../../ai/retrieval/hnsw.md)                      |
| [Hybrid search](../../ai/retrieval/hybrid-search.md) support  | Assembled from general query composition (`fq`/`rq` + `{!knn}`), no dedicated API                      | Native: `knn` + `query` in one request body                                    | Dedicated `hybrid` query type + search pipeline normalization              |
| Typical use case today | Maintaining/operating an existing large Solr deployment; teams already invested in SolrCloud/ZooKeeper | New projects wanting the most mature vector/[hybrid search](../../ai/retrieval/hybrid-search.md) and widest ecosystem | New projects wanting Apache-2.0 licensing and/or Amazon OpenSearch Service |

## Related

- [Elasticsearch](elasticsearch.md) — the [Lucene](lucene.md)-based engine that displaced Solr as the default open-source choice for most new projects after 2010
- [OpenSearch](opensearch.md) — the Apache-2.0-licensed fork of Elasticsearch 7.10.2
- [Lucene](lucene.md) — the library Solr actually embeds as its core engine
- [BM25](../../ai/retrieval/bm25.md) — the lexical scoring algorithm, Solr's default similarity since version 6.0
- [Inverted Index](../../ai/retrieval/inverted-index.md) — the structure behind Solr's full-text search, built on the shared [Lucene](lucene.md) library
- [Approximate Nearest Neighbor Search (ANN)](../../ai/retrieval/approximate-nearest-neighbor.md) / [HNSW](../../ai/retrieval/hnsw.md) — the algorithm behind Solr's `DenseVectorField`/`{!knn}` search
- [Hybrid Search](../../ai/retrieval/hybrid-search.md) — the general pattern Solr assembles from `fq`/`rq` + `{!knn}` rather than a dedicated query type
- [Vector Databases](../../ai/retrieval/vector-database.md) — where Solr fits among vector store options
- [PostgreSQL (`pgvector`)](../relational/postgresql.md#pgvector-vector-search) — the equivalent "vector search bolted onto a general-purpose database" pattern in the relational world
