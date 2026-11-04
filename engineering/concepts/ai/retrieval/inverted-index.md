# Inverted Index

An inverted index is the data structure behind keyword/full-text search — it's what makes "find every document containing this word" fast instead of requiring a linear scan of every document. It's called *inverted* because it flips the natural, "forward" direction of the data: instead of each document listing its own words, each word lists the documents it appears in.

## Forward index vs. inverted index

```
Forward index (how documents are naturally stored):
  doc_1 → ["leave", "policy", "entitles", "employees", "to", "30", "days"]
  doc_2 → ["expense", "report", "submit", "within", "14", "days"]

Inverted index (flipped — word → documents):
  "leave"    → [doc_1]
  "policy"   → [doc_1]
  "days"     → [doc_1, doc_2]
  "expense"  → [doc_2]
  "report"   → [doc_2]
```

A query for "days" becomes a direct lookup — `index["days"] → [doc_1, doc_2]` — instead of scanning every document's text to check whether it contains the word. This is the same algorithmic shift that an index provides in a relational database (`WHERE` on an indexed column vs. a full table scan), applied to text search specifically.

## What's actually stored per term

A real inverted index stores more than just a list of document IDs — it keeps what's needed to *rank* results, not just find them:

| Stored per term | Why |
|---|---|
| **Postings list** | Which documents contain the term |
| **Term frequency** | How many times the term appears in each document — an input to [BM25](bm25.md) scoring |
| **Positions** | Where in the document the term appears — enables phrase queries ("submit expense report" as an exact phrase, not just three separate word matches) |
| **Document frequency** | How many documents in the whole corpus contain the term at all — the other input [BM25](bm25.md) needs, to weight rare terms higher than common ones |

## How it fits into search

Building the index happens once (and incrementally, as documents are added or changed) at ingestion time: text runs through the [tokenization, normalization, and stemming/lemmatization pipeline](text-analysis.md), and the resulting terms are written into the postings lists above. At query time, the query is run through the exact same pipeline, each query term's postings list is looked up, and [BM25](bm25.md) scores the matching documents using the term-frequency and document-frequency data already sitting in the index — no re-scanning of raw text happens at query time.

This is the structure behind the "full-text" side of every engine that offers keyword search: [Elasticsearch](../../databases/search/elasticsearch.md), [OpenSearch](../../databases/search/opensearch.md), Solr, and the inverted index [Azure AI Search](../../cloud/azure/azure-ai-search.md) builds automatically for every text field in an index (see [Azure AI Search](../../cloud/azure/azure-ai-search.md)'s indexing diagram). [PostgreSQL](../../databases/relational/postgresql.md)'s `tsvector`/`GIN` index is the same underlying idea applied inside a relational database.

## Why it matters alongside vector search

An inverted index and a [vector index](approximate-nearest-neighbor.md) solve genuinely different problems and typically coexist side by side in a modern search system rather than one replacing the other — exactly the pattern [hybrid search](hybrid-search.md) runs both in parallel and merges the results. The inverted index answers "which documents contain these exact words," fast and exactly; the vector index answers "which documents are about this general idea," approximately. Neither can substitute for the other.

## Related

- [BM25](bm25.md) — the scoring algorithm that ranks results found via an inverted index
- [Text Analysis: Tokenization, Normalization, Stemming & Lemmatization](text-analysis.md) — the pipeline that turns raw text into the terms this index actually stores
- [Hybrid Search](hybrid-search.md) — combines inverted-index (keyword) search with vector search
- [Approximate Nearest Neighbor Search (ANN)](approximate-nearest-neighbor.md) / [HNSW](hnsw.md) — the vector-side counterpart to this structure
- [Lucene](../../databases/search/lucene.md) — the library whose segments implement this structure inside [Elasticsearch](../../databases/search/elasticsearch.md)/[OpenSearch](../../databases/search/opensearch.md)/Solr
- [Azure AI Search](../../cloud/azure/azure-ai-search.md) — builds an inverted index automatically for every text field
- [Vector Databases](vector-database.md)
