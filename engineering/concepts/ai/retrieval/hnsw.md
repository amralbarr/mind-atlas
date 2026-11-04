# HNSW (Hierarchical Navigable Small World)

HNSW is the dominant algorithm for [Approximate Nearest Neighbor (ANN) search](approximate-nearest-neighbor.md) today — it's the default or primary vector index type in [FAISS](vector-stores/faiss.md), [Qdrant](vector-stores/qdrant.md), [Weaviate](vector-stores/weaviate.md), `pgvector`, [Azure AI Search](../../cloud/azure/azure-ai-search.md), and [Lucene](../../databases/search/lucene.md) itself (which [Elasticsearch](../../databases/search/elasticsearch.md) and [OpenSearch](../../databases/search/opensearch.md) both build on — see [Lucene](../../databases/search/lucene.md)).

## The structure: a multi-layer graph

HNSW builds a graph where every indexed vector is a node, connected to its approximate nearest neighbors, organized into layers:

```
Layer 2 (sparsest):     A ─────────────── F
                         \               /
Layer 1 (medium):    A ── B ──── D ──── F ── G
                      \    \    /        \
Layer 0 (every node): A─B─C─D─E─F─G─H─I─J─K
```

- **Layer 0** contains *every* vector in the index, densely connected to its nearby neighbors — this is where the actual fine-grained search resolves.
- Each layer above that is a **random subset** of the layer below, with progressively fewer nodes and longer-range connections — functioning like an express lane that lets a search jump across large distances quickly instead of crawling node-by-node.
- A node's top layer is assigned **randomly at insertion time**, with exponentially decreasing probability of reaching each higher layer — most nodes exist only at layer 0, a few reach layer 1, fewer still reach layer 2. This is the same core idea as a skip list, applied to a graph instead of a sorted list.

## How a query actually walks it

1. Start at a fixed entry point in the **top** (sparsest) layer.
2. Greedily move to whichever neighbor is closest to the query vector, repeating until no neighbor is closer.
3. Drop down one layer, using the current position as the new starting point, and repeat the greedy walk there.
4. Keep descending layer by layer until reaching layer 0, where the final (approximate) nearest neighbors are collected.

Because each layer eliminates most of the search space before the next layer even starts, the whole walk touches only a small fraction of the total nodes — this is *why* HNSW search is close to logarithmic in the number of vectors rather than linear like brute-force [exact search](approximate-nearest-neighbor.md).

## Tuning parameters

| Parameter | What it controls | Trade-off |
|---|---|---|
| `M` | How many connections each node keeps per layer | Higher = better recall, more memory, slower index build |
| `ef_construction` | How wide the search is during index building | Higher = better index quality, slower to build |
| `ef_search` (sometimes called `ef` or `k` at query time) | How wide the search is at query time | Higher = better recall, slower query |

[Azure AI Search](../../cloud/azure/azure-ai-search.md)'s own guidance to "set vector `k=50` when combining with semantic re-ranking" is exactly this `ef_search`-style trade-off: a wider candidate pool at query time costs a bit of latency but gives the downstream [cross-encoder re-ranker](cross-encoder-reranking.md) (or, generally, a narrower top-k) better candidates to choose from. Every one of these three parameters is a dial between recall and speed/memory — benchmark them against exact search on a representative sample of real data rather than assuming a library's defaults transfer unchanged to your corpus.

## How HNSW differs from the index's incremental build (vs. IVF)

Unlike [IVF](approximate-nearest-neighbor.md#other-ann-approaches), which needs a **training** step (clustering a representative sample before any vectors can be added), HNSW is built **incrementally** — each vector is inserted into the graph as it arrives, with no separate training pass required. This makes HNSW a more natural fit for indexes that grow continuously (new documents arriving over time) rather than being built once from a fixed snapshot.

## Related

- [Approximate Nearest Neighbor Search (ANN)](approximate-nearest-neighbor.md) — the general concept this is the dominant algorithm for, including the IVF/Product Quantization alternatives
- [Vector Databases](vector-database.md)
- [FAISS](vector-stores/faiss.md) — exposes HNSW directly as `IndexHNSWFlat`
- [Qdrant](vector-stores/qdrant.md) — uses HNSW internally as its default index
- [Lucene](../../databases/search/lucene.md) — has native HNSW-based vector support since version 9.x
- [Azure AI Search](../../cloud/azure/azure-ai-search.md) — offers HNSW (approximate) alongside exhaustive kNN (exact) per vector field
- [Cross-Encoder Re-Ranking](cross-encoder-reranking.md) — the second-stage model an HNSW candidate pool typically feeds
