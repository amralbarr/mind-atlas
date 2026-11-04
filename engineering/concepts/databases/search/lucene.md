# Apache Lucene

Lucene is the open-source Java library that actually does full-text search — not a server, not a database, not something you query over a network. [Elasticsearch](elasticsearch.md), [OpenSearch](opensearch.md), and [Apache Solr](solr.md) are not three competing search engines in the sense of having three independent implementations: all three **embed the same Lucene library** as their core engine, then wrap it with a distributed server, a [REST](../../backend/api/rest.md) API, clustering, and schema management. When any of those three files in this handbook says "Lucene's `X` filter" or "Lucene-based," this is the library they're referring to.

## What Lucene actually provides

| Component | What it does |
|---|---|
| **`IndexWriter` / `IndexReader`** | The core Java API for writing documents into an index and reading/searching it back |
| **Segments** | A Lucene index is physically made of immutable segments — each write creates a new small segment, and segments are periodically merged in the background. This segment-based design is *why* a Lucene-based index can keep serving reads while being written to |
| **Analyzers (Tokenizers + TokenFilters)** | The actual implementations behind every "Lucene `X` filter/tokenizer" reference across this handbook's [text analysis pipeline](../../ai/retrieval/text-analysis.md) — `StandardTokenizer`, `LowerCaseFilter`, `ASCIIFoldingFilter`, `ArabicNormalizationFilter`/`ArabicStemFilter`, `StopFilter`, `ICUNormalizer2Filter`, and the rest are all Lucene classes, not something [Elasticsearch](elasticsearch.md)/[OpenSearch](opensearch.md)/Solr independently reimplemented |
| **`Similarity`** | Lucene's pluggable scoring framework. `BM25Similarity` has been Lucene's default since version 6 — this is the actual implementation behind every "uses [BM25](../../ai/retrieval/bm25.md)" claim made about [Elasticsearch](elasticsearch.md), [OpenSearch](opensearch.md), or Solr in this handbook; see [BM25](../../ai/retrieval/bm25.md) |
| **Query objects** | `TermQuery`, `BooleanQuery`, `PhraseQuery`, and others — the building blocks that a higher-level query language ([Elasticsearch](elasticsearch.md)'s Query DSL, Solr's query parsers) ultimately compiles down to |
| **Vector field support** | Since Lucene 9.x, native k-NN vector search ([HNSW](../../ai/retrieval/approximate-nearest-neighbor.md)-based) — the implementation [Elasticsearch](elasticsearch.md)'s `dense_vector` field and [OpenSearch](opensearch.md)'s `lucene` k-NN engine choice both build directly on |

## Why this explains why the three engines behave so similarly

[Elasticsearch](elasticsearch.md), [OpenSearch](opensearch.md), and [Solr](solr.md) share the same [inverted index](../../ai/retrieval/inverted-index.md) format, the same default [BM25](../../ai/retrieval/bm25.md) scoring, and largely the same analyzer behavior (same tokenizers, same stemmers, same `arabic` language analyzer) precisely because none of them reimplemented any of that — they all call into the same underlying Lucene classes. What actually differs between the three is everything *around* Lucene: how the index is distributed across a cluster, what the query API looks like, how schema is managed, and — most visibly in this handbook's coverage — how each one bolts on vector search ([Elasticsearch](elasticsearch.md)'s built-in `dense_vector` field vs. [OpenSearch](opensearch.md)'s separate k-NN plugin with its `faiss`/`lucene` engine choice vs. Solr's `DenseVectorField`).

## Can you use Lucene directly?

Yes — the same embedded-library-vs-full-server [positioning](../../../../marketing/concepts/fundamentals/positioning.md) as [FAISS](../../ai/retrieval/vector-stores/faiss.md) relative to a full [vector database](../../ai/retrieval/vector-database.md). Lucene runs inside your own JVM process with no separate server, [REST](../../backend/api/rest.md) API, or clustering — which is exactly the trade-off: no network hop and no infrastructure to operate, but no distribution across machines and no [HTTP](../../networking/http.md) interface either, unlike [Elasticsearch](elasticsearch.md)/[OpenSearch](opensearch.md)/Solr. It's the right choice for a single-process Java application that needs embedded search and doesn't need a multi-node cluster — the same niche [FAISS](../../ai/retrieval/vector-stores/faiss.md) or embedded [ChromaDB](../../ai/retrieval/vector-stores/chromadb.md) occupy for vector search specifically.

## Related

- [Elasticsearch](elasticsearch.md), [OpenSearch](opensearch.md), [Apache Solr](solr.md) — all three embed Lucene as their core engine
- [BM25](../../ai/retrieval/bm25.md) — Lucene's default `Similarity` implementation since version 6
- [Inverted Index](../../ai/retrieval/inverted-index.md) — the structure Lucene's segments implement
- [Text Analysis Pipeline](../../ai/retrieval/text-analysis.md) — tokenization/normalization/[stemming](../../ai/retrieval/analyzer-pipeline/stemming.md), all implemented as Lucene Analyzer components
- [Approximate Nearest Neighbor Search (ANN) & HNSW](../../ai/retrieval/approximate-nearest-neighbor.md) — Lucene's own native [HNSW](../../ai/retrieval/hnsw.md) vector support since version 9.x
- [FAISS](../../ai/retrieval/vector-stores/faiss.md) — the equivalent embedded-library [positioning](../../../../marketing/concepts/fundamentals/positioning.md) on the vector-search side
