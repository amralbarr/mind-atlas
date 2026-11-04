# LlamaIndex

LlamaIndex is a framework focused specifically on connecting [LLMs](../generation/llm.md) to data — documents, PDFs, databases, APIs — where the hard part is finding and structuring the relevant information *before* it ever reaches the model. See [AI Orchestration Frameworks](../../../overviews/ai/orchestration-frameworks.md) for how it compares to [LangChain](langchain.md), the framework it's most often paired or compared with.

## Core Concepts

| Term | Meaning |
|---|---|
| **Document** | A raw source of data (a file, a webpage, a database row) before being processed |
| **Node** | A chunk of a document — the actual unit that gets embedded and retrieved, analogous to what [Document Indexing](../ingestion/document-indexing.md) calls a "chunk" |
| **Index** | A structure built over a set of nodes to support efficient retrieval — a `VectorStoreIndex` is the most common, backed by a [vector database](../retrieval/vector-database.md) |
| **Query Engine** | The retrieval + synthesis pipeline: given a query, find relevant nodes, then generate an answer grounded in them |
| **Ingestion pipeline** | The configurable sequence of transformations (chunking, metadata extraction, embedding) applied to raw documents before indexing |

## Installation

```bash
pip install llama-index
```

## Building an Index and Querying It

```python
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader

documents = SimpleDirectoryReader("./data").load_data()
index = VectorStoreIndex.from_documents(documents)

query_engine = index.as_query_engine()
response = query_engine.query("What was Q3 revenue?")
print(response)
```

`VectorStoreIndex.from_documents` handles chunking, embedding, and storage in one call — the same pipeline [Document Indexing](../ingestion/document-indexing.md) describes generically, wrapped into a few lines.

## Using a Specific Vector Store Backend

```python
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core import StorageContext
import chromadb

chroma_client = chromadb.PersistentClient(path="./chroma_db")
collection = chroma_client.get_or_create_collection("docs")

vector_store = ChromaVectorStore(chroma_collection=collection)
storage_context = StorageContext.from_defaults(vector_store=vector_store)

index = VectorStoreIndex.from_documents(documents, storage_context=storage_context)
```

See [ChromaDB](../retrieval/vector-stores/chromadb.md) for the underlying store this connects to.

## Custom Chunking Configuration

```python
from llama_index.core.node_parser import SentenceSplitter

splitter = SentenceSplitter(chunk_size=400, chunk_overlap=50)
nodes = splitter.get_nodes_from_documents(documents)
index = VectorStoreIndex(nodes)
```

## Common Questions

**LlamaIndex vs. [LangChain](langchain.md) — do you need both?**
> They're commonly used together, not as alternatives to choose between: LlamaIndex specializes in the ingestion/indexing/retrieval side, while [LangChain](langchain.md) provides the broader chaining, agent, and tool-calling scaffolding. A common stack uses LlamaIndex to build and query an index, then feeds its output into a [LangChain](langchain.md) chain or agent.

**When does LlamaIndex stop being enough on its own?**
> When the application needs more than retrieval-then-answer — multi-step reasoning, tool use beyond lookup, or stateful multi-agent workflows are outside LlamaIndex's core focus; that's where [LangChain](langchain.md) and especially [LangGraph](langgraph.md) take over.

## Related

- [AI Orchestration Frameworks](../../../overviews/ai/orchestration-frameworks.md)
- [LangChain](langchain.md)
- [Vector Databases](../retrieval/vector-database.md)
- [Document Indexing Pipeline](../ingestion/document-indexing.md)
- [Retrieval-Augmented Generation (RAG)](../rag/rag.md)
- [Chunking Strategies & Libraries](../../../overviews/ai/chunking-strategies.md) — how LlamaIndex's node parsers compare to [Docling](../ingestion/docling.md), [LangChain](langchain.md), Unstructured, and Chonkie
