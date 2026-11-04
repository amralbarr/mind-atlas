# Embeddings

## What is it?

An embedding is a numerical representation of text (a word, sentence, paragraph, or document) as a list of decimal numbers called a **vector**. The key property of embeddings is that texts with similar meanings have similar vectors — they are "close" to each other in mathematical space.

Embeddings are what make semantic search possible: instead of matching exact words, the system compares the meaning of the question with the meaning of each document chunk.

## Intuition

Imagine a 2D map where every word is placed based on its meaning:

```
         [Technology]
    Azure  Docker  Cloud

[Finance]                    [People]
  Budget  Revenue           HR  Salary  Employee

         [Documents]
    Report  Policy  Plan
```

Words with similar meanings cluster together. Embeddings do this in hundreds of dimensions instead of 2, making the similarity much more accurate.

## How embeddings are created

An **embedding model** is a neural network trained to produce these vector representations. You pass text in, you get a vector out:

```
Input: "The Q3 revenue exceeded the target by 12%"
         ↓
Embedding Model (e.g., text-embedding-3-small)
         ↓
Output: [0.023, -0.412, 0.887, 0.104, -0.231, ...]  (1536 numbers)
```

The same model must be used for both indexing (converting chunks to vectors) and querying (converting the user's question to a vector). Mixing models produces wrong results.

## Embedding models used in this project

| Model | Provider | Dimensions | Notes |
|---|---|---|---|
| `text-embedding-3-small` | OpenAI API | 1536 | Recommended: fast, affordable, accurate |
| `text-embedding-3-large` | OpenAI API | 3072 | More accurate, higher cost |
| `text-embedding-ada-002` | [Azure](../../cloud/azure/azure.md) OpenAI | 1536 | [Azure](../../cloud/azure/azure.md)-hosted version |
| `all-MiniLM-L6-v2` | sentence-transformers | 384 | Local, free, no [API key](../../security/auth/api-key.md) needed |
| `all-mpnet-base-v2` | sentence-transformers | 768 | Local, free, more accurate |

For a student project with API access: `text-embedding-3-small` is recommended.
For a fully local setup: `all-MiniLM-L6-v2` via sentence-transformers.

For a production, multilingual (e.g. Arabic/English) system, the model landscape is much larger — see [Embedding Model Selection: Local vs. API](../../../overviews/ai/embedding-model-selection.md) for a full comparison (BGE-M3, Qwen3-Embedding, EmbeddingGemma 2, OpenAI, Voyage, Cohere) and a decision framework.

## Similarity — how search works

After embedding both the query and all chunks, the system computes **cosine similarity** between the query vector and every chunk vector:

```
Similarity = cos(θ) = (A · B) / (|A| × |B|)

Score of 1.0 = identical meaning
Score of 0.9 = very similar
Score of 0.5 = somewhat related
Score of 0.0 = unrelated
```

The top-N chunks with the highest similarity scores are returned.

## Embedding example

```python
from openai import OpenAI

client = OpenAI(api_key="...")

def embed(text: str) -> list[float]:
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    return response.data[0].embedding

# Index time: embed a chunk and store it
chunk_text = "Q3 revenue reached 2.4M, exceeding the target by 12%."
chunk_vector = embed(chunk_text)
# → store chunk_vector in ChromaDB with metadata

# Query time: embed the question and search
question = "What was the Q3 revenue?"
query_vector = embed(question)
# → search ChromaDB for chunks with similar vectors
```

## Cost consideration

OpenAI charges per token for embedding API calls:
- `text-embedding-3-small`: $0.02 per 1M tokens (very cheap)
- A 400-word chunk ≈ 500 tokens
- 100 documents × 3 chunks = 300 chunks × 500 tokens = 150,000 tokens ≈ $0.003

For a student project, costs are negligible. For production: consider local models.

## How it fits in this project

Embeddings are implemented by Member 1 (Computer Science) in `ai/embeddings/embedder.py`. The embedding model is chosen once in Week 1 and used consistently throughout. The same model is called both when indexing documents (to create the stored vectors) and when processing user queries (to create the search vector).

## Related

- [Vector Databases](../retrieval/vector-database.md)
- [Retrieval-Augmented Generation (RAG)](../rag/rag.md)
- [Document Indexing Pipeline](document-indexing.md)
- [Large Language Models (LLMs)](../generation/llm.md)
- [Nextcloud RAG Case Study](../../../guides/cloud/nextcloud-rag-case-study/nextcloud.md)
- [Embedding Model Selection: Local vs. API](../../../overviews/ai/embedding-model-selection.md)
