# Weaviate

Weaviate is an open-source, production-grade [vector database](../vector-database.md) that combines vector similarity search with structured data filtering in a single engine. It is schema-based (unlike [ChromaDB](chromadb.md)), supports multiple vector spaces per object, and can auto-vectorize data using built-in model integrations — meaning you can push raw text and Weaviate calls the embedding model for you.

## When to Use Weaviate

| Good fit | Poor fit |
|---|---|
| Production self-hosted vector search | Quick local prototypes (use [ChromaDB](chromadb.md)) |
| Complex object schemas with typed properties | Teams without [Docker](../../../containers/docker.md)/infra capacity |
| [Hybrid search](../hybrid-search.md) (vector + keyword [BM25](../bm25.md)) | Fully managed with no ops (use [Pinecone](pinecone.md)) |
| Multi-tenancy (namespace per tenant) | Simple single-collection use cases |
| Auto-vectorization without separate embed step | |

## Core Concepts

| Term | Meaning |
|---|---|
| **Collection** (formerly Class) | A typed schema for a group of objects |
| **Object** | A record with properties + an embedding vector |
| **Property** | A typed field on an object (text, int, bool, etc.) |
| **Vectorizer** | Module that auto-generates [embeddings](../../ingestion/embeddings.md) (e.g. `text2vec-openai`) |
| **Tenant** | Isolated data partition within a collection (multi-tenancy) |
| **[Hybrid Search](../hybrid-search.md)** | Combines vector similarity + [BM25](../bm25.md) keyword search |
| **Generative Search** | [RAG](../../rag/rag.md) built in — retrieve + generate in one query |

## Installation (Docker)

```yaml
# docker-compose.yml
services:
  weaviate:
    image: cr.weaviate.io/semitechnologies/weaviate:1.25.0
    ports:
      - "8080:8080"
      - "50051:50051"    # gRPC (used by v4 client)
    volumes:
      - weaviate_data:/var/lib/weaviate
    environment:
      QUERY_DEFAULTS_LIMIT: "25"
      AUTHENTICATION_ANONYMOUS_ACCESS_ENABLED: "true"
      PERSISTENCE_DATA_PATH: "/var/lib/weaviate"
      DEFAULT_VECTORIZER_MODULE: "none"          # set to text2vec-openai to auto-vectorize
      ENABLE_MODULES: ""                         # add modules: text2vec-openai,generative-openai
      CLUSTER_HOSTNAME: "node1"

volumes:
  weaviate_data:
```

```bash
docker compose up -d
```

## Python Client (v4)

```bash
pip install weaviate-client
```

```python
import weaviate
import os
from dotenv import load_dotenv

load_dotenv()

# Connect to local instance
client = weaviate.connect_to_local()  # localhost:8080

# Connect to Weaviate Cloud (managed)
client = weaviate.connect_to_weaviate_cloud(
    cluster_url=os.getenv("WEAVIATE_URL"),
    auth_credentials=weaviate.auth.AuthApiKey(os.getenv("WEAVIATE_API_KEY")),
)

# Always close the client when done
client.close()

# Or use as context manager
with weaviate.connect_to_local() as client:
    pass
```

## Define a Collection (Schema)

```python
import weaviate.classes as wvc

with weaviate.connect_to_local() as client:
    client.collections.create(
        name="Document",
        vectorizer_config=wvc.config.Configure.Vectorizer.none(),  # we supply our own vectors
        properties=[
            wvc.config.Property(name="title", data_type=wvc.config.DataType.TEXT),
            wvc.config.Property(name="content", data_type=wvc.config.DataType.TEXT),
            wvc.config.Property(name="source", data_type=wvc.config.DataType.TEXT),
            wvc.config.Property(name="created_at", data_type=wvc.config.DataType.DATE),
        ],
    )
```

## Insert Objects

```python
from datetime import datetime, timezone

with weaviate.connect_to_local() as client:
    collection = client.collections.get("Document")

    # Single insert
    uuid = collection.data.insert(
        properties={
            "title": "Q3 Financial Report",
            "content": "Revenue grew by 12% in Q3...",
            "source": "finance",
            "created_at": datetime(2024, 9, 1, tzinfo=timezone.utc).isoformat(),
        },
        vector=[0.1, 0.2, ...],   # your embedding
    )

    # Batch insert (recommended for large ingestion)
    with collection.batch.dynamic() as batch:
        for doc in documents:
            batch.add_object(
                properties={"title": doc["title"], "content": doc["content"]},
                vector=embed(doc["content"]),
            )
```

## Vector Search (Similarity)

```python
with weaviate.connect_to_local() as client:
    collection = client.collections.get("Document")

    results = collection.query.near_vector(
        near_vector=embed("quarterly revenue results"),
        limit=5,
        return_metadata=wvc.query.MetadataQuery(distance=True),
    )

    for obj in results.objects:
        print(obj.properties["title"], obj.metadata.distance)
```

## Hybrid Search (Vector + BM25 Keyword)

```python
results = collection.query.hybrid(
    query="quarterly revenue",        # used for both BM25 and vector
    vector=embed("quarterly revenue"),
    alpha=0.5,                        # 0 = pure BM25, 1 = pure vector
    limit=5,
)
```

## Filtered Search

```python
import weaviate.classes as wvc

results = collection.query.near_vector(
    near_vector=query_vector,
    limit=5,
    filters=wvc.query.Filter.by_property("source").equal("finance"),
)

# Compound filters
filters = (
    wvc.query.Filter.by_property("source").equal("finance") &
    wvc.query.Filter.by_property("created_at").greater_than("2024-01-01T00:00:00Z")
)
```

## Fetch, Update, Delete

```python
# Fetch by UUID
obj = collection.query.fetch_object_by_id(uuid)

# Fetch by property filter
results = collection.query.fetch_objects(
    filters=wvc.query.Filter.by_property("source").equal("finance"),
    limit=10,
)

# Update an object
collection.data.update(uuid=uuid, properties={"title": "Updated Title"})

# Replace entire object
collection.data.replace(uuid=uuid, properties={...}, vector=[...])

# Delete by UUID
collection.data.delete_by_id(uuid)

# Delete by filter
collection.data.delete_many(
    where=wvc.query.Filter.by_property("source").equal("old-source")
)
```

## Auto-Vectorization (text2vec-openai module)

With the OpenAI module enabled, Weaviate calls the embedding API automatically on insert:

```yaml
# docker-compose.yml environment:
DEFAULT_VECTORIZER_MODULE: "text2vec-openai"
ENABLE_MODULES: "text2vec-openai,generative-openai"
OPENAI_APIKEY: "${OPENAI_API_KEY}"
```

```python
client.collections.create(
    name="Document",
    vectorizer_config=wvc.config.Configure.Vectorizer.text2vec_openai(
        model="text-embedding-3-small",
    ),
    properties=[
        wvc.config.Property(name="content", data_type=wvc.config.DataType.TEXT),
    ],
)

# Insert without providing a vector — Weaviate embeds automatically
collection.data.insert(properties={"content": "Revenue grew by 12%..."})
```

## Generative Search (Built-in RAG)

```python
client.collections.create(
    name="Document",
    generative_config=wvc.config.Configure.Generative.openai(model="gpt-4o-mini"),
    # ...
)

results = collection.generate.near_vector(
    near_vector=query_vector,
    limit=4,
    single_prompt="Summarize this document: {content}",
    # grouped_task="Summarize all retrieved documents into one answer",
)

for obj in results.objects:
    print(obj.generated)
```

## Multi-Tenancy

```python
# Enable multi-tenancy on collection
client.collections.create(
    name="Document",
    multi_tenancy_config=wvc.config.Configure.multi_tenancy(enabled=True),
)

collection = client.collections.get("Document")

# Create tenants
collection.tenants.create([
    wvc.tenants.Tenant(name="tenant-alice"),
    wvc.tenants.Tenant(name="tenant-bob"),
])

# Scope all operations to a tenant
tenant_collection = collection.with_tenant("tenant-alice")
tenant_collection.data.insert(properties={...}, vector=[...])
results = tenant_collection.query.near_vector(near_vector=[...], limit=5)
```

## Environment Variables

```bash
# .env
WEAVIATE_URL=https://my-cluster.weaviate.network    # Weaviate Cloud
WEAVIATE_API_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
OPENAI_API_KEY=sk-...     # if using text2vec-openai or generative-openai
```

## Weaviate vs Alternatives

| | Weaviate | [ChromaDB](chromadb.md) | [Pinecone](pinecone.md) | pgvector |
|---|---|---|---|---|
| Hosting | Self-hosted / managed cloud | Self-hosted / local | Fully managed SaaS | [PostgreSQL](../../../databases/relational/postgresql.md) extension |
| Schema | Typed (required) | Flexible | Schema-less | [PostgreSQL](../../../databases/relational/postgresql.md) columns |
| [Hybrid search](../hybrid-search.md) | Yes ([BM25](../bm25.md) + vector) | No | No (vector only) | With pg_bm25 extension |
| Auto-vectorize | Yes (modules) | Yes (built-in) | No | No |
| Generative search | Yes (built-in) | No | No | No |
| Multi-tenancy | Yes (native) | No | Yes (namespaces) | Manual (row-level) |
| Best for | Production self-hosted, complex queries | Local prototypes | Managed, no-ops | Already on [PostgreSQL](../../../databases/relational/postgresql.md) |

## Related Concepts

- [ChromaDB](./chromadb.md) — simpler self-hosted option for prototyping
- [Pinecone](./pinecone.md) — fully managed alternative (no infra)
- [Vector Databases](../vector-database.md) — overview and comparison
- [python-dotenv](../../../../installation/linux/python.md) — manage secrets securely
