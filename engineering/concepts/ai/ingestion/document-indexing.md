# Document Indexing Pipeline

## What is it?

Document indexing is the process of reading documents (PDF, Word, text files), extracting their text content, breaking it into manageable pieces, and storing those pieces in a searchable format. An index is like the back of a book — instead of reading every page to find information, you look it up in the index and go directly to the right page.

In this project, indexing is what makes AI-powered document search possible. Without indexing, the AI would have to read every document from scratch every time a user asks a question — which is too slow and too expensive.

## The indexing pipeline

```
Nextcloud (source documents)
         ↓
Step 1: Document Collection
  — List files via WebDAV API
  — Download each file
  — Record metadata (filename, folder, owner, permissions)
         ↓
Step 2: Text Extraction
  — PDF → extract text (PyMuPDF / pdfplumber)
  — Word (.docx) → extract text (python-docx)
  — Plain text (.txt) → read directly
         ↓
Step 3: Cleaning / Normalization
  — Remove headers, footers, page numbers
  — Fix encoding issues
  — Strip excessive whitespace
         ↓
Step 4: Chunking
  — Split text into overlapping chunks (~400 tokens each)
  — Each chunk is a self-contained excerpt
         ↓
Step 5: Embedding
  — Convert each chunk to a vector (embedding)
  — The vector numerically represents the meaning of the text
         ↓
Step 6: Store in Vector Index
  — Save: chunk text + embedding vector + metadata (permissions, filename, department)
  — Index is now ready for semantic search
```

## Why chunking?

A document cannot be sent to the AI as one block because:
- [LLMs](../generation/llm.md) have a token limit ([context window](../generation/context-window.md))
- A 50-page PDF is too large to fit in one prompt
- Chunking lets us retrieve only the relevant parts, not the entire document

**Chunk size:** ~300–500 tokens (~250–400 words)
**Overlap:** ~50 tokens between consecutive chunks so context is not lost at boundaries

For a comparison of chunking libraries/tools ([LangChain](../agents/langchain.md), [LlamaIndex](../agents/llamaindex.md), [Docling](docling.md), Unstructured, Chonkie, and others) and when to reach for each, see [Chunking Strategies & Libraries](../../../overviews/ai/chunking-strategies.md).

Example — a 3-page document becomes:
```
Chunk 1: paragraphs 1-3 (with overlap at boundary)
Chunk 2: paragraphs 3-6 (with overlap at boundary)
Chunk 3: paragraphs 6-8
```

## What is an embedding?

An embedding is a list of numbers (a vector) that represents the meaning of a text. Two texts with similar meaning have similar vectors — they are "close" in vector space — even if they use different words.

```
"What is the project budget?"
→ embedding → [0.12, -0.34, 0.87, 0.02, ...]  (hundreds of numbers)

"The Q3 budget allocation for Project A is..."
→ embedding → [0.11, -0.31, 0.85, 0.04, ...]  (very similar vector)
```

This is how semantic search works — it finds documents that mean the same thing as the question, not just documents that contain the exact same words. See [Embeddings](embeddings.md) for the full details.

## Metadata stored with each chunk

Each chunk in the index stores more than just text:

```json
{
  "chunk_id": "finance_q3_001",
  "document_id": "Finance_Q3_Report_2026.txt",
  "filename": "Finance_Q3_Report_2026.txt",
  "department": "Finance",
  "folder_path": "/Finance/",
  "allowed_groups": ["Finance", "Admin"],
  "chunk_index": 1,
  "content": "Q3 revenue reached 2.4M, exceeding the target by 12%...",
  "embedding": [0.12, -0.34, 0.87, ...]
}
```

The `allowed_groups` field is critical — it is used by the permission filter to prevent unauthorized users from retrieving this chunk.

## Vector store (search index)

The index is stored in a **[vector database](../retrieval/vector-database.md)** (also called a vector store). Options used in projects like this:

| Tool | Type | Notes |
|---|---|---|
| **[ChromaDB](../retrieval/vector-stores/chromadb.md)** | Local, embedded | Simple, good for prototypes and academic projects |
| **[FAISS](../retrieval/vector-stores/faiss.md)** | Local library | Fast, open-source, from Meta. No server needed. |
| **[Qdrant](../retrieval/vector-stores/qdrant.md)** | Server-based | More production-ready, supports metadata filtering |
| **[Azure AI Search](../../cloud/azure/azure-ai-search.md)** | Cloud service | Native [Azure](../../cloud/azure/azure.md) integration, managed service |

See [Vector Databases](../retrieval/vector-database.md) for a deeper comparison.

## How it fits in this project

Document indexing is owned by Member 1 (Computer Science). The indexing pipeline runs after Nextcloud is set up and documents are uploaded. It must be re-run (or run incrementally) whenever new documents are added. The indexed data feeds directly into the [RAG](../rag/rag.md) pipeline for AI search.

## Related

- [Embeddings](embeddings.md)
- [Vector Databases](../retrieval/vector-database.md)
- [Retrieval-Augmented Generation (RAG)](../rag/rag.md)
- [Pipeline Orchestration](../infrastructure/pipeline-orchestration.md)
- [Nextcloud RAG Case Study](../../../guides/cloud/nextcloud-rag-case-study/nextcloud.md)
- [Chunking Strategies & Libraries](../../../overviews/ai/chunking-strategies.md)
- [Embedding Model Selection: Local vs. API](../../../overviews/ai/embedding-model-selection.md)
