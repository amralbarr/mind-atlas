# Approximate Nearest Neighbor Search (ANN)

Approximate Nearest Neighbor search (**ANN**) is the family of techniques [vector databases](vector-database.md) use to find the closest vectors to a query without comparing against every single vector in the index. It's "approximate" because it deliberately trades a small amount of search accuracy for a large speed and memory improvement — and in practice, almost every [vector database](vector-database.md) you'd use at any real scale is running an ANN index, not exact search, by default.

## Why exact search doesn't scale

The naive approach — **exact nearest neighbor (kNN) / brute-force search** — computes the distance between the query vector and every indexed vector, then returns the top-k closest:

```
Exact search cost: O(N) per query, where N = total vectors in the index
```

That's fine at a few thousand vectors. At tens of millions, every single query touches every single vector — latency and compute cost scale linearly with corpus size. ANN indexes trade exactness for sublinear (often close to logarithmic) query cost by organizing vectors into a structure that lets search skip most of them.

## ANN algorithms

| Approach | Idea | Where you'll see it |
|---|---|---|
| **[HNSW](hnsw.md)** | Graph-based — see [HNSW](hnsw.md) for the full mechanics (layer structure, the query walk, tuning parameters) | The default or primary index type in [FAISS](vector-stores/faiss.md), [Qdrant](vector-stores/qdrant.md), [Weaviate](vector-stores/weaviate.md), `pgvector`, [Azure AI Search](../../cloud/azure/azure-ai-search.md), and [Lucene](../../databases/search/lucene.md) — the most widely used ANN algorithm today |
| **IVF (Inverted File Index)** | Clusters vectors ahead of time (e.g. via k-means); a query only searches the clusters nearest to it, not the whole index | `IndexIVFFlat` in [FAISS](vector-stores/faiss.md) |
| **Product Quantization (PQ)** | Compresses vectors into compact codes to shrink memory footprint, often combined with IVF (`IndexIVFPQ`) | [FAISS](vector-stores/faiss.md), large-scale deployments where memory is the bottleneck |

IVF-based indexes additionally need a **training** step — they're built by clustering a representative sample of vectors first, before any vectors can be added — unlike [HNSW](hnsw.md), which is built incrementally as vectors are inserted; see [HNSW](hnsw.md) for why that matters.

## The trade-off that actually matters: recall vs. speed

Every ANN parameter above is a dial between **recall** (did we actually find the true nearest neighbors?) and **speed/memory**. This is a distinct kind of recall from [Recall@k](../evaluation/retrieval-metrics.md) as a [RAG](../rag/rag.md) metric — ANN recall asks "did the index return the vectors that are mathematically closest to the query," while [RAG](../rag/rag.md)'s Recall@k asks "did retrieval return the chunks that actually answer the question." A perfect ANN index (100% ANN recall) still has a [RAG](../rag/rag.md) Recall@k ceiling set by whether the *correct* chunk's vector is even close to the query vector in the first place — ANN tuning cannot fix a bad embedding or a bad chunk.

**In practice:** benchmark ANN parameters against exact search on a representative, authorized subset of your real data, not a synthetic benchmark — tune [HNSW's `M`/`ef_construction`/`ef_search`](hnsw.md#tuning-parameters) (or your engine's equivalent) against measured latency, memory, index build time, and recall, and re-validate whenever a metadata filter changes the shape of what's actually being searched (a highly selective filter narrows the candidate pool, and filtered-ANN behavior varies meaningfully by engine).

## Related

- [HNSW](hnsw.md) — the dominant ANN algorithm, full mechanics
- [Lucene](../../databases/search/lucene.md) — has native [HNSW](hnsw.md)-based vector support since version 9.x
- [Vector Databases](vector-database.md)
- [FAISS](vector-stores/faiss.md) — exposes both exact (`IndexFlatL2`) and approximate (`IndexIVFFlat`, `IndexHNSWFlat`) index types directly
- [Qdrant](vector-stores/qdrant.md) — uses [HNSW](hnsw.md) internally as its default index
- [Azure AI Search](../../cloud/azure/azure-ai-search.md) — offers both [HNSW](hnsw.md) (approximate) and exhaustive kNN (exact) per vector field
- [Retrieval Metrics](../evaluation/retrieval-metrics.md) — where ANN recall and [RAG](../rag/rag.md) Recall@k are distinct, related measurements
- [Cross-Encoder Re-Ranking](cross-encoder-reranking.md) — the second-stage model this candidate pool feeds
- [Hybrid Search](hybrid-search.md)
