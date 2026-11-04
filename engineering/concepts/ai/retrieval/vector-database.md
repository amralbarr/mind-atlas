# Vector Databases

## What is it?

A vector database (also called a **vector store**) is a specialized database designed to store, index, and search **embedding vectors** — lists of numbers that represent the meaning of text. Unlike a traditional database that searches by exact keyword match, a vector database finds results by **semantic similarity**: it returns vectors that are mathematically close to the query vector, which corresponds to content that means something similar to the query.

## Why a vector database?

Traditional database search:
```sql
SELECT * FROM documents WHERE content LIKE '%budget%'
```
Finds only documents that contain the exact word "budget". Misses "spending plan", "financial allocation", "cost breakdown".

Vector database search:
```
search(embed("what is the spending plan?"), top_k=5)
```
Finds documents about budgets, financial plans, cost allocations — even if they don't contain the word "budget" — because the [embeddings](../ingestion/embeddings.md) are semantically similar.

## How it works

```
Store phase:
Text chunk → Embedding Model → [0.12, -0.34, 0.87, ...]
                                         ↓
                              Stored in vector index with metadata

Search phase:
Query text → Embedding Model → [0.11, -0.31, 0.85, ...]
                                         ↓
                              Find nearest vectors (cosine similarity)
                                         ↓
                              Return top-N most similar chunks
```

## Similarity search

The most common similarity measure is **cosine similarity**: it measures the angle between two vectors. A score of 1.0 means identical meaning; 0.0 means unrelated. See [Embeddings](../ingestion/embeddings.md) for the full mechanics of how vectors are produced and compared.

## Types of Vector Databases

Every tool in the options table below falls into one of four categories — knowing which one you're picking determines what you're actually signing up to operate:

| Category | What it means | Examples |
|---|---|---|
| **Embedded / in-process library** | Runs inside your own application process — no separate server to deploy, no network hop. Simplest to start with; typically limited to a single machine's memory and doesn't scale to a distributed, multi-writer setup | [FAISS](vector-stores/faiss.md), [ChromaDB](vector-stores/chromadb.md) in its default local mode |
| **Purpose-built vector database server** | A standalone product built specifically for vector search, run self-hosted ([Docker](../../containers/docker.md)/[Kubernetes](../../distributed-systems/kubernetes/ingress.md)) or as a managed cloud service. Strongest metadata filtering, scaling, and [ANN-tuning](approximate-nearest-neighbor.md) options because vectors are the only thing it does | [Qdrant](vector-stores/qdrant.md), [Weaviate](vector-stores/weaviate.md), [Pinecone](vector-stores/pinecone.md), Milvus |
| **Vector search added to a general-purpose database** | A feature or extension bolted onto a database you likely already operate for other data. Avoids standing up new infrastructure and keeps vectors next to relational/document data in one system, at the cost of typically being less specialized than a purpose-built engine at very large vector scale | `pgvector` on [PostgreSQL](../../databases/relational/postgresql.md), [Elasticsearch](../../databases/search/elasticsearch.md)/[OpenSearch](../../databases/search/opensearch.md) (k-NN plugin)/[Solr](../../databases/search/solr.md) (`DenseVectorField`, since 9.0), Redis (vector search module), [MongoDB](../../databases/nosql/mongodb.md) Atlas Vector Search |
| **Cloud-native managed AI search service** | A higher-level managed service that bundles vector search with hybrid/keyword search, semantic re-ranking, and enterprise features (access control, scaling, SLAs) under one product | [Azure AI Search](../../cloud/azure/azure-ai-search.md), [AWS](../../cloud/infrastructure/aws.md) [OpenSearch](../../databases/search/opensearch.md) Service, Google Vertex AI Vector Search |

The first two categories are what most [RAG](../rag/rag.md) tutorials show; the last two matter more once "enterprise" requirements (existing data platform, access control, operational ownership) enter the picture — see the [Architecture Design Exercise](../../../interview/interview-01/06-design.md) for how that trade-off plays out in practice.

## Options for this project

Each option below with real production usage has its own dedicated note — this table is a comparison, not a full description of any of them:

| Tool | Type | Complexity | Best for |
|---|---|---|---|
| **[ChromaDB](vector-stores/chromadb.md)** | Embedded / in-process library | Low | Academic projects, prototypes, no server needed |
| **[FAISS](vector-stores/faiss.md)** | Embedded / in-process library | Low-Medium | Fast search, no server, from Meta |
| **[Qdrant](vector-stores/qdrant.md)** | Purpose-built server (self-hosted) | Medium | Metadata filtering support, more production-ready |
| **[Pinecone](vector-stores/pinecone.md)** | Purpose-built server (fully managed SaaS) | Low ([API key](../../security/auth/api-key.md) only) | Production, no infra to operate, huge scale |
| **[Weaviate](vector-stores/weaviate.md)** | Purpose-built server (self-hosted / managed) | Medium | [Hybrid search](hybrid-search.md) ([BM25](bm25.md) + vector) built in |
| **`pgvector`** ([PostgreSQL](../../databases/relational/postgresql.md#pgvector-vector-search)) | Vector search on a general-purpose database | Low-Medium | Already running Postgres; keeping vectors next to relational metadata in one system |
| **[Elasticsearch](../../databases/search/elasticsearch.md)** | Vector search on a general-purpose database (document store) | Medium | Already running [Elasticsearch](../../databases/search/elasticsearch.md) for full-text/logging; native `dense_vector` + `knn`, [hybrid search](hybrid-search.md) in one request |
| **[OpenSearch](../../databases/search/opensearch.md)** | Vector search on a general-purpose database (document store) | Medium | Same as [Elasticsearch](../../databases/search/elasticsearch.md) but Apache-2.0-licensed, or already on Amazon [OpenSearch](../../databases/search/opensearch.md) Service; k-NN plugin with `faiss`/`lucene` engine choice |
| **[Apache Solr](../../databases/search/solr.md)** | Vector search on a general-purpose database (document store) | Medium | Already running Solr/SolrCloud; `DenseVectorField` + `{!knn}` query parser (since 9.0), the newest and least turnkey of the three [Lucene](../../databases/search/lucene.md)-based engines' vector support |
| **[Azure](../../cloud/azure/azure.md) AI Search** ([Azure AI Search](../../cloud/azure/azure-ai-search.md)) | Cloud-native managed AI search service | Medium-High | Native [Azure](../../cloud/azure/azure.md) integration, managed, built-in [hybrid search](hybrid-search.md) + semantic ranking |

For this project, **[ChromaDB](vector-stores/chromadb.md)** or **[FAISS](vector-stores/faiss.md)** is recommended for simplicity. For an enterprise [RAG](../rag/rag.md) system that already runs [PostgreSQL](../../databases/relational/postgresql.md), **`pgvector`** is the common default (see [Hybrid Search](hybrid-search.md) and [Embedding Model Selection](../../../overviews/ai/embedding-model-selection.md) for how it's used elsewhere in this handbook).

## Metadata filtering

This is critical for permission-aware retrieval. The vector store must support filtering results by metadata fields before or during search:

```python
# Only return chunks from departments this user can access
results = collection.query(
    query_embeddings=[query_vector],
    n_results=5,
    where={"allowed_groups": {"$in": ["Finance", "Admin"]}}
)
```

Without metadata filtering, you would retrieve all semantically similar chunks and then filter — which is less efficient and risks returning unauthorized content momentarily. See [Access Control & IAM](../../security/authorization/access-control-iam.md) for the broader [authorization](../../security/authorization/authorization.md) model this depends on.

### The inputs any query call actually takes

The parameter names differ per engine, but every vector store's search call accepts roughly the same set of inputs:

| Input | What it means | Example |
|---|---|---|
| **query** | The query text, or its precomputed embedding vector | `"What is the leave policy?"` |
| **top_k** | How many results to return (named `n_results`, `top_k`, or `limit` depending on the engine) | `5` |
| **filter** | Metadata conditions that narrow the search | `department = "HR"` |
| **score_threshold** | A minimum similarity cutoff (optional — not every engine supports it) | `0.75` |
| **include / with_payload** | Which fields to return: text, metadata, scores | `metadatas, distances` |
| **namespace / collection** | Which dataset/index to search within | `"company_policies"` |

### Metadata moves through two separate phases

1. **Indexing time** — metadata is attached to each chunk when it's written to the store, alongside its vector:

```python
collection.add(
    ids=["doc_42_chunk_3", "doc_42_chunk_4"],
    documents=["Employees are entitled to 30 paid leave days per year...", "Leave requests must be submitted 14 days in advance..."],
    metadatas=[
        {"department": "HR", "doc_type": "policy", "year": 2026, "source": "hr_handbook.pdf", "page": 12},
        {"department": "HR", "doc_type": "policy", "year": 2026, "source": "hr_handbook.pdf", "page": 13},
    ],
)
```

2. **Query time** — that same metadata is used to filter which vectors are even considered, and it's returned alongside each hit so the caller can inspect it (source, page, access level, freshness) without a separate lookup.

The exact filter syntax differs per engine — see [ChromaDB](vector-stores/chromadb.md) (`where`/`where_document`, and note it returns **distance**, not similarity — lower is better; with cosine, `similarity = 1 - distance`), [Pinecone](vector-stores/pinecone.md) (`filter` + `namespace`), and [Qdrant](vector-stores/qdrant.md) (`query_filter` + `score_threshold`, one of the few engines exposing a similarity cutoff directly in the query call).

### Metadata filtering is a double-edged sword

If the metadata is wrong or incomplete — a leave-policy chunk mistakenly tagged `department: "Finance"` — the filter excludes it permanently and Recall@k drops silently, with no error to signal it. Measure Recall@k **both with and without** the filter applied during evaluation to catch this before it reaches production; see [Retrieval Metrics](../evaluation/retrieval-metrics.md) for the worked example.

## What is stored in the vector store

Each entry in the vector store for this project:

| Field | Type | Description |
|---|---|---|
| `chunk_id` | string | Unique identifier for this chunk |
| `document_id` | string | Which document this came from |
| `filename` | string | Original filename |
| `department` | string | Which department folder (Finance, HR, Projects) |
| `allowed_groups` | list | Which Nextcloud groups can access this document |
| `chunk_index` | int | Position of this chunk within the document |
| `content` | string | The actual text of the chunk |
| `embedding` | vector | The numerical representation of the chunk's meaning |

## How it fits in this project

The vector store is set up and managed by Member 1 (Computer Science) as part of the AI indexing pipeline. It is populated by the document ingestion process and queried by the [RAG](../rag/rag.md) retrieval layer when a user asks a question.

## Related

- [ChromaDB](vector-stores/chromadb.md)
- [FAISS](vector-stores/faiss.md)
- [Qdrant](vector-stores/qdrant.md)
- [Pinecone](vector-stores/pinecone.md)
- [Weaviate](vector-stores/weaviate.md)
- [PostgreSQL (`pgvector`)](../../databases/relational/postgresql.md#pgvector-vector-search)
- [Elasticsearch](../../databases/search/elasticsearch.md)
- [OpenSearch](../../databases/search/opensearch.md)
- [Apache Solr](../../databases/search/solr.md)
- [Azure AI Search](../../cloud/azure/azure-ai-search.md)
- [Approximate Nearest Neighbor Search (ANN)](approximate-nearest-neighbor.md)
- [HNSW](hnsw.md) — the dominant [ANN](approximate-nearest-neighbor.md) algorithm
- [Lucene](../../databases/search/lucene.md) — the shared engine behind [Elasticsearch](../../databases/search/elasticsearch.md), [OpenSearch](../../databases/search/opensearch.md), and Solr
- [Inverted Index](inverted-index.md) — the keyword-search counterpart to a vector index
- [MMR](mmr.md) — a diversity-focused re-ranking pass over a vector store's search results, needing each candidate's embedding to compute
- [BM25](bm25.md)
- [Embeddings](../ingestion/embeddings.md)
- [Retrieval-Augmented Generation (RAG)](../rag/rag.md)
- [Document Indexing Pipeline](../ingestion/document-indexing.md)
- [Access Control & IAM](../../security/authorization/access-control-iam.md)
- [Nextcloud RAG Case Study](../../../guides/cloud/nextcloud-rag-case-study/nextcloud.md)
