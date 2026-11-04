# FAISS

FAISS (Facebook AI Similarity Search) is an open-source library — not a server — for fast similarity search over dense vectors, built by Meta. It runs embedded directly in your application process (no separate database to run), making it a common choice for local/prototype [vector search](../vector-database.md) when a full client-server [vector database](../vector-database.md) is unnecessary overhead.

## Core Concepts

| Term | Meaning |
|---|---|
| **Index** | An in-memory data structure holding vectors and supporting nearest-neighbor search — the core FAISS object, not a server-side concept |
| **`IndexFlatL2` / `IndexFlatIP`** | The simplest index types — exact search via brute-force distance/inner-product computation; correct but scales linearly with vector count |
| **[Approximate indexes](../approximate-nearest-neighbor.md) (`IndexIVFFlat`, `IndexHNSWFlat` — [HNSW](../hnsw.md))** | Trade a small amount of search accuracy for much faster search at large scale, by not comparing against every single vector |
| **Training** | Some index types (IVF-based) need to be "trained" on representative vectors first, to build internal clustering structures, before vectors can be added |
| **No built-in persistence server** | FAISS indexes live in memory; saving/loading to disk is an explicit step you manage yourself (`faiss.write_index` / `faiss.read_index`), unlike a server-based store that persists automatically |

## Installation

```bash
pip install faiss-cpu   # or faiss-gpu for CUDA-accelerated search
```

## Building and Searching a Flat (Exact) Index

```python
import faiss
import numpy as np

dimension = 1536  # must match your embedding model's output size
index = faiss.IndexFlatL2(dimension)  # exact search, L2 distance

vectors = np.random.random((1000, dimension)).astype('float32')
index.add(vectors)

query = np.random.random((1, dimension)).astype('float32')
distances, indices = index.search(query, k=5)   # 5 nearest neighbors
print(indices, distances)
```

FAISS itself only returns index positions and distances — it doesn't store metadata (text, filenames) alongside vectors the way [ChromaDB](chromadb.md)/[Pinecone](pinecone.md)/[Qdrant](qdrant.md) do, so applications typically keep a separate parallel array/dict mapping index position back to the original document.

## An Approximate Index for Larger Scale

```python
nlist = 100  # number of clusters
quantizer = faiss.IndexFlatL2(dimension)
index = faiss.IndexIVFFlat(quantizer, dimension, nlist)

index.train(vectors)   # required before adding vectors, unlike IndexFlatL2
index.add(vectors)

index.nprobe = 10       # how many clusters to search — higher = more accurate, slower
distances, indices = index.search(query, k=5)
```

## Persisting an Index

```python
faiss.write_index(index, "my_index.faiss")
index = faiss.read_index("my_index.faiss")
```

## Common Questions

**When is FAISS the wrong choice compared to [Qdrant](qdrant.md), [ChromaDB](chromadb.md), or [Pinecone](pinecone.md)?**
> When you need metadata filtering combined with vector search (e.g. "similar documents, but only from Finance"), multi-tenant isolation, or a separate server that multiple application processes can query concurrently — FAISS is a library embedded in one process with no metadata model or client-server access built in. [Qdrant](qdrant.md) and [ChromaDB](chromadb.md) exist specifically to add those capabilities on top of a similar underlying search problem.

**Is FAISS still relevant given full [vector databases](../vector-database.md) now exist?**
> Yes, particularly as the underlying search algorithm inside other tools (several [vector databases](../vector-database.md) use FAISS or FAISS-derived techniques internally), and directly, for use cases genuinely needing raw, embedded, no-server-overhead vector search — a single-machine batch job or a research prototype, for instance.

## Related

- [Vector Databases](../vector-database.md)
- [Qdrant](qdrant.md)
- [ChromaDB](chromadb.md)
- [Approximate Nearest Neighbor Search (ANN)](../approximate-nearest-neighbor.md) / [HNSW](../hnsw.md)
- [Embeddings](../../ingestion/embeddings.md)
