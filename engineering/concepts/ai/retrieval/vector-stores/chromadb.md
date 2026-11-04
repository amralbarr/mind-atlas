# ChromaDB

ChromaDB is an open-source, embedded [vector database](../vector-database.md) designed for AI applications. It stores vector [embeddings](../../ingestion/embeddings.md) alongside metadata and supports semantic similarity search. It runs in-process (no separate server) by default, making it the fastest way to add vector search to a Python project.

## When to Use ChromaDB

| Good fit | Poor fit |
|---|---|
| Local prototypes & [RAG](../../rag/rag.md) demos | Large-scale production (millions of vectors) |
| Single-process Python apps | Multi-node distributed setups |
| Fast iteration / no infra overhead | Strict persistence SLAs without tuning |
| Learning vector search concepts | Teams already running [Qdrant](qdrant.md) / [Weaviate](weaviate.md) |

## Installation

```bash
pip install chromadb
```

## Core Concepts

| Term | Meaning |
|---|---|
| **Collection** | A named group of [embeddings](../../ingestion/embeddings.md) (like a table) |
| **Document** | The raw text stored alongside each embedding |
| **Embedding** | The vector representation of a document |
| **Metadata** | Arbitrary key-value pairs for filtering |
| **ID** | Unique string identifier per record |

## Quick Start (In-Memory)

```python
import chromadb

client = chromadb.Client()  # ephemeral, no disk persistence

collection = client.create_collection("docs")

collection.add(
    documents=["FastAPI is a modern Python web framework", "PostgreSQL is a relational database"],
    metadatas=[{"source": "web"}, {"source": "db-docs"}],
    ids=["doc1", "doc2"],
)

results = collection.query(
    query_texts=["what is a web framework?"],
    n_results=1,
)
print(results["documents"])
```

## Persistent Storage (Disk)

```python
import chromadb

client = chromadb.PersistentClient(path="./chroma_db")  # saved to disk

collection = client.get_or_create_collection("docs")
```

## Client-Server Mode

Run ChromaDB as a standalone [HTTP](../../../networking/http.md) server (useful for multi-process or [Docker](../../../containers/docker.md) setups):

```bash
chroma run --path ./chroma_db --port 8000
```

```python
import chromadb

client = chromadb.HttpClient(host="localhost", port=8000)
collection = client.get_or_create_collection("docs")
```

## Using Custom Embeddings

By default ChromaDB uses its built-in `all-MiniLM-L6-v2` model. Pass your own [embeddings](../../ingestion/embeddings.md) for full control:

```python
import chromadb
from chromadb import Documents, EmbeddingFunction, Embeddings
from openai import OpenAI

class OpenAIEmbedder(EmbeddingFunction):
    def __call__(self, input: Documents) -> Embeddings:
        client = OpenAI()
        response = client.embeddings.create(model="text-embedding-3-small", input=input)
        return [r.embedding for r in response.data]

collection = client.get_or_create_collection(
    "docs",
    embedding_function=OpenAIEmbedder(),
)
```

## Metadata Filtering

```python
results = collection.query(
    query_texts=["database performance"],
    n_results=5,
    where={"source": "db-docs"},           # exact match
    where_document={"$contains": "index"},  # full-text filter on document
)
```

Supported operators: `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$in`, `$nin`, `$and`, `$or`.

## RAG Pattern with ChromaDB

```python
import chromadb
import os
from openai import OpenAI

chroma = chromadb.PersistentClient(path="./chroma_db")
collection = chroma.get_or_create_collection("knowledge_base")
openai = OpenAI()

def ingest(texts: list[str], source: str):
    collection.add(
        documents=texts,
        metadatas=[{"source": source}] * len(texts),
        ids=[f"{source}_{i}" for i in range(len(texts))],
    )

def retrieve(query: str, k: int = 4) -> list[str]:
    results = collection.query(query_texts=[query], n_results=k)
    return results["documents"][0]

def answer(question: str) -> str:
    context = "\n\n".join(retrieve(question))
    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": f"Answer using this context:\n{context}"},
            {"role": "user", "content": question},
        ],
    )
    return response.choices[0].message.content
```

## Docker (Client-Server)

```yaml
# docker-compose.yml
services:
  chroma:
    image: chromadb/chroma:latest
    ports:
      - "8000:8000"
    volumes:
      - chroma_data:/chroma/chroma
    environment:
      - IS_PERSISTENT=TRUE

volumes:
  chroma_data:
```

```python
client = chromadb.HttpClient(host="localhost", port=8000)
```

## Environment Variables

```bash
# .env
CHROMA_HOST=localhost
CHROMA_PORT=8000
```

```python
from dotenv import load_dotenv
load_dotenv()

client = chromadb.HttpClient(
    host=os.getenv("CHROMA_HOST", "localhost"),
    port=int(os.getenv("CHROMA_PORT", 8000)),
)
```

## ChromaDB vs Alternatives

| | ChromaDB | pgvector | [Qdrant](qdrant.md) | [Weaviate](weaviate.md) |
|---|---|---|---|---|
| Setup | Zero (embedded) | [PostgreSQL](../../../databases/relational/postgresql.md) extension | [Docker](../../../containers/docker.md) / cloud | [Docker](../../../containers/docker.md) / cloud |
| Scale | Thousands–low millions | Millions (with [PostgreSQL](../../../databases/relational/postgresql.md)) | Millions+ | Millions+ |
| Filtering | Metadata + doc | Full [SQL](../../../databases/relational/sql.md) | Rich payload filters | [GraphQL](../../../backend/api/graphql.md) |
| Best for | Prototypes, local [RAG](../../rag/rag.md) | Already using [PostgreSQL](../../../databases/relational/postgresql.md) | Production vector search | Complex semantic apps |

## Related Concepts

- [Vector Databases](../vector-database.md) — comparison of all vector store options
- [FastAPI](../../../backend/architecture/asgi.md) — serve a retrieval endpoint over ChromaDB
- [Streamlit](../../../frontend/streamlit.md) — build a [RAG](../../rag/rag.md) UI on top of ChromaDB
- [python-dotenv](../../../../installation/linux/python.md) — manage secrets and config
