# Pinecone

Pinecone is a fully managed, cloud-native [vector database](../vector-database.md) built specifically for production AI applications. Unlike self-hosted options, Pinecone handles all infrastructure — replication, scaling, indexing — so you interact with it entirely through an API. It is the most common choice when you need production-grade vector search without managing servers.

## When to Use Pinecone

| Good fit | Poor fit |
|---|---|
| Production [RAG](../../rag/rag.md) / semantic search | Local development (use [ChromaDB](chromadb.md) instead) |
| Millions to billions of vectors | Strict data residency / air-gapped environments |
| Teams without infra capacity | Budget-sensitive projects (managed = paid) |
| Low-latency similarity search at scale | Full control over the index internals |

## Core Concepts

| Term | Meaning |
|---|---|
| **Index** | A named collection of vectors (like a table) |
| **Namespace** | Logical partition within an index (like a folder) |
| **Vector** | A float array representing an embedding |
| **Metadata** | Key-value pairs attached to each vector for filtering |
| **Upsert** | Insert or update vectors by ID |
| **Pod-based index** | Dedicated compute pods (legacy, pay-per-pod) |
| **Serverless index** | Pay-per-request, auto-scales (recommended for new projects) |

## Installation

```bash
pip install pinecone
```

## Quick Start

```python
from pinecone import Pinecone, ServerlessSpec
import os
from dotenv import load_dotenv

load_dotenv()

pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))

# Create a serverless index (once)
pc.create_index(
    name="my-index",
    dimension=1536,          # must match your embedding model output size
    metric="cosine",         # cosine | euclidean | dotproduct
    spec=ServerlessSpec(
        cloud="aws",         # aws | gcp | azure
        region="us-east-1",
    ),
)

index = pc.Index("my-index")
```

## Upsert Vectors

```python
# Upsert a batch of vectors
index.upsert(
    vectors=[
        {
            "id": "doc-001",
            "values": [0.1, 0.2, ...],   # embedding vector (1536 floats)
            "metadata": {"source": "finance", "author": "alice"},
        },
        {
            "id": "doc-002",
            "values": [0.3, 0.4, ...],
            "metadata": {"source": "engineering", "author": "bob"},
        },
    ],
    namespace="reports",     # optional — default namespace if omitted
)
```

Upsert in batches of up to 100 vectors per request. For large ingestion, batch and parallelize:

```python
from itertools import islice

def batched(iterable, n):
    it = iter(iterable)
    while batch := list(islice(it, n)):
        yield batch

for batch in batched(all_vectors, 100):
    index.upsert(vectors=batch, namespace="reports")
```

## Query (Similarity Search)

```python
results = index.query(
    vector=[0.1, 0.2, ...],      # query embedding
    top_k=5,                      # number of results
    namespace="reports",
    include_metadata=True,
    include_values=False,         # set True if you need the raw vectors back
)

for match in results["matches"]:
    print(match["id"], match["score"], match["metadata"])
```

## Metadata Filtering

```python
results = index.query(
    vector=query_embedding,
    top_k=5,
    filter={
        "source": {"$eq": "finance"},
        "year": {"$gte": 2023},
    },
    include_metadata=True,
)
```

Supported operators: `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$in`, `$nin`, `$and`, `$or`.

## Fetch, Update, Delete

```python
# Fetch vectors by ID
resp = index.fetch(ids=["doc-001", "doc-002"], namespace="reports")

# Update metadata (keep the same vector)
index.update(id="doc-001", set_metadata={"reviewed": True}, namespace="reports")

# Delete by ID
index.delete(ids=["doc-001"], namespace="reports")

# Delete all vectors in a namespace
index.delete(delete_all=True, namespace="reports")

# Index stats
print(index.describe_index_stats())
```

## RAG Pattern with Pinecone

```python
import os
from pinecone import Pinecone
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
index = pc.Index("knowledge-base")
openai = OpenAI()

def embed(text: str) -> list[float]:
    resp = openai.embeddings.create(model="text-embedding-3-small", input=text)
    return resp.data[0].embedding

def ingest(doc_id: str, text: str, metadata: dict):
    index.upsert(vectors=[{"id": doc_id, "values": embed(text), "metadata": metadata}])

def retrieve(query: str, k: int = 4, filter: dict = None) -> list[str]:
    results = index.query(
        vector=embed(query),
        top_k=k,
        filter=filter,
        include_metadata=True,
    )
    return [m["metadata"].get("text", m["id"]) for m in results["matches"]]

def answer(question: str, filter: dict = None) -> str:
    context = "\n\n".join(retrieve(question, filter=filter))
    resp = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": f"Answer using this context:\n{context}"},
            {"role": "user", "content": question},
        ],
    )
    return resp.choices[0].message.content
```

## Namespaces (Multi-tenant Isolation)

Use namespaces to isolate data per user, team, or document group within one index:

```python
# Ingest per tenant
index.upsert(vectors=vectors, namespace=f"tenant-{tenant_id}")

# Query per tenant
index.query(vector=query_vec, top_k=5, namespace=f"tenant-{tenant_id}")

# Delete all data for a tenant
index.delete(delete_all=True, namespace=f"tenant-{tenant_id}")
```

## Index Management

```python
# List indexes
print(pc.list_indexes())

# Describe an index
print(pc.describe_index("my-index"))

# Delete an index (irreversible)
pc.delete_index("my-index")
```

## Environment Variables

```bash
# .env
PINECONE_API_KEY=pcsk_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
PINECONE_INDEX=my-index
PINECONE_NAMESPACE=default
```

## Dimension Reference (Common Embedding Models)

| Model | Dimension |
|---|---|
| `text-embedding-3-small` (OpenAI) | 1536 |
| `text-embedding-3-large` (OpenAI) | 3072 |
| `text-embedding-ada-002` (OpenAI, legacy) | 1536 |
| `all-MiniLM-L6-v2` (HuggingFace) | 384 |
| `all-mpnet-base-v2` (HuggingFace) | 768 |
| `nomic-embed-text` (Ollama) | 768 |

The index dimension must match exactly — cannot be changed after creation.

## Pinecone vs Alternatives

| | Pinecone | [ChromaDB](chromadb.md) | [Weaviate](weaviate.md) | pgvector |
|---|---|---|---|---|
| Hosting | Fully managed SaaS | Self-hosted / local | Self-hosted / managed | [PostgreSQL](../../../databases/relational/postgresql.md) extension |
| Scale | Billions of vectors | Thousands–low millions | Millions+ | Millions (with [PostgreSQL](../../../databases/relational/postgresql.md)) |
| Setup | [API key](../../../security/auth/api-key.md) only | Zero (embedded) | [Docker](../../../containers/docker.md) / cloud | [PostgreSQL](../../../databases/relational/postgresql.md) extension |
| Cost | Pay-per-use | Free (self-hosted) | Free (self-hosted) | Free ([PostgreSQL](../../../databases/relational/postgresql.md) cost) |
| Best for | Production, no-infra | Prototypes, local [RAG](../../rag/rag.md) | Production, self-hosted | Already using [PostgreSQL](../../../databases/relational/postgresql.md) |

## Related Concepts

- [ChromaDB](./chromadb.md) — local/self-hosted alternative, ideal for prototyping
- [Weaviate](./weaviate.md) — self-hosted production [vector database](../vector-database.md)
- [Vector Databases](../vector-database.md) — overview and comparison of all options
- [python-dotenv](../../../../installation/linux/python.md) — manage API keys securely
