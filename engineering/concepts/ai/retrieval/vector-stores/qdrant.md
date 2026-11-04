# Qdrant

Qdrant is an open-source [vector database](../vector-database.md) that runs as a server (self-hosted via [Docker](../../../containers/docker.md), or as a managed cloud offering) — positioned as a more production-ready middle ground between an embedded library like [FAISS](faiss.md) and a fully managed SaaS like [Pinecone](pinecone.md), with strong built-in support for filtering search results by metadata.

## Core Concepts

| Term | Meaning |
|---|---|
| **Collection** | A named set of vectors plus their payloads — Qdrant's equivalent of a table |
| **Point** | A single record: an ID, a vector, and an optional **payload** (arbitrary [JSON](../../../programming/fundamentals/json.md) metadata) |
| **Payload** | The metadata attached to a point — Qdrant indexes payload fields separately from vectors, enabling fast filtered search |
| **Distance metric** | Configured per collection at creation time — Cosine, Euclidean, or Dot product |
| **[HNSW](../hnsw.md) index** | The [approximate-nearest-neighbor](../approximate-nearest-neighbor.md) algorithm Qdrant uses internally for fast search at scale |

## Running It (Docker)

```bash
docker run -d --name qdrant -p 6333:6333 -p 6334:6334 qdrant/qdrant
```

`6333` serves the [REST](../../../backend/api/rest.md) API; `6334` serves [gRPC](../../../backend/api/grpc.md). Data persists to a [Docker](../../../containers/docker.md) volume by default configuration.

## Installation (Python Client)

```bash
pip install qdrant-client
```

## Creating a Collection and Upserting Points

```python
from qdrant_client import QdrantClient
from qdrant_client.http.models import VectorParams, Distance, PointStruct

client = QdrantClient(url="http://localhost:6333")

client.create_collection(
    collection_name="documents",
    vectors_config=VectorParams(size=1536, distance=Distance.COSINE),
)

client.upsert(
    collection_name="documents",
    points=[
        PointStruct(
            id=1,
            vector=[0.12, -0.34, 0.87, ...],
            payload={"department": "Finance", "filename": "Q3_report.txt"},
        ),
    ],
)
```

## Searching with Metadata Filtering

```python
from qdrant_client.http.models import Filter, FieldCondition, MatchValue

results = client.search(
    collection_name="documents",
    query_vector=query_embedding,
    query_filter=Filter(
        must=[FieldCondition(key="department", match=MatchValue(value="Finance"))]
    ),
    limit=5,
    score_threshold=0.75,   # drop any hit below this similarity score — no result below it is ever returned
)

for hit in results:
    print(hit.id, hit.score, hit.payload)
```

Filtering happens as part of the same search call, not as a separate post-search step — this is the capability the [Vector Databases](../vector-database.md) note flags as critical for permission-aware retrieval (e.g. only returning chunks the requesting user's groups can access). `score_threshold` is one of the few cross-engine query inputs Qdrant exposes directly in the search call rather than requiring a manual post-filter — useful for retrieval-level abstention (see [Retrieval Metrics](../../evaluation/retrieval-metrics.md)).

## Common Questions

**Why choose Qdrant over [ChromaDB](chromadb.md) for a project moving past prototyping?**
> [ChromaDB](chromadb.md) is optimized for simplicity — embedded, minimal setup, good for prototypes. Qdrant runs as a proper server with a documented client-server API, stronger metadata-filtering performance, [gRPC](../../../backend/api/grpc.md) support, and clustering options for scaling beyond a single machine — closer to what a production deployment needs without committing to a fully managed SaaS like [Pinecone](pinecone.md).

**Does Qdrant require its own hosted cloud service?**
> No — self-hosting via [Docker](../../../containers/docker.md) (as shown above) is fully supported and common; Qdrant Cloud is an optional managed offering for teams that don't want to operate the server themselves, similar to the self-hosted-vs-managed choice covered for other tools throughout this vault.

## Related

- [Vector Databases](../vector-database.md)
- [FAISS](faiss.md)
- [ChromaDB](chromadb.md)
- [Pinecone](pinecone.md)
- [Approximate Nearest Neighbor Search (ANN)](../approximate-nearest-neighbor.md) / [HNSW](../hnsw.md)
- [Document Indexing Pipeline](../../ingestion/document-indexing.md)
