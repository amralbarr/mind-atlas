# Chunking Strategies & Libraries for RAG

Chunking is the step in [Document Indexing](../../concepts/ai/ingestion/document-indexing.md) that decides how a document gets split before embedding. There's a range of tooling here — some libraries just split text, others parse the document's actual structure (PDF layout, tables, headings) first and chunk around that structure. This page compares the common options and when to reach for each one.

## Libraries at a glance

| Library                                                  | Chunking approaches                                            | Local or cloud                | When to use it                                                                                                                       |
| -------------------------------------------------------- | -------------------------------------------------------------- | ----------------------------- | ------------------------------------------------------------------------------------------------------------------------------------ |
| **[LangChain](../../concepts/ai/agents/langchain.md) Text Splitters**                             | Fixed-size, Recursive, Markdown-aware, HTML-aware, token-based | Local                         | General-purpose and flexible, especially if the rest of the pipeline already uses [LangChain](../../concepts/ai/agents/langchain.md)                                          |
| **[LlamaIndex](../../concepts/ai/agents/llamaindex.md)** | Sentence, Semantic, Hierarchical, Sentence-window              | Mostly local                  | When you need Nodes + metadata + hierarchical retrieval, not just flat chunks                                                        |
| **[Docling](../../concepts/ai/ingestion/docling.md)**    | Hybrid, hierarchical, structure-aware (`HybridChunker`)        | Local, or as a hosted service | Best choice for real PDFs/complex documents — preserves tables and headings instead of flattening them                               |
| **Unstructured**                                         | By-title, document-element-aware, table-aware, fixed-size      | Local or API                  | Mixed-format ingestion: PDF, Word, HTML, slide decks, etc.                                                                           |
| **Chonkie**                                              | Token-aware, Recursive, Semantic, and others                   | Local                         | A lightweight, standalone chunking library when you don't want a full [RAG](../../concepts/ai/rag/rag.md) framework                                                  |
| **semantic-text-splitter**                               | Hierarchical splitting with token-based size limits            | Local                         | Fast splitting that respects paragraph/sentence boundaries — despite the name, it does not require [embeddings](../../concepts/ai/ingestion/embeddings.md) for the split decision |
| **py_document_chunker**                                  | Recursive, Semantic, Structure-aware                           | Local                         | Adds metadata support plus [LangChain](../../concepts/ai/agents/langchain.md)/[LlamaIndex](../../concepts/ai/agents/llamaindex.md) integration [hooks](../../concepts/frontend/hooks.md)                                                                    |

## Which one to actually reach for

- **[Docling](../../concepts/ai/ingestion/docling.md) — for real documents.** If the system ingests PDFs, contracts, reports, or anything with tables, start here. Its `HybridChunker` chunks around the document's actual structure (headings, table boundaries) instead of blindly splitting characters — see [Docling](../../concepts/ai/ingestion/docling.md) for the full write-up and a working example.
- **[LangChain](../../concepts/ai/agents/langchain.md) Text Splitters — for general-purpose splitting.** Start with `RecursiveCharacterTextSplitter`, then layer on a Markdown- or HTML-aware splitter if the source format calls for it. Good choice when you want direct, simple control without adopting a larger framework.
- **Chonkie — for a standalone, minimal dependency.** Useful if you're building a custom [RAG](../../concepts/ai/rag/rag.md) service and don't want to pull in [LangChain](../../concepts/ai/agents/langchain.md) or [LlamaIndex](../../concepts/ai/agents/llamaindex.md) just for chunking.

## Quick example (LangChain)

```bash
pip install langchain-text-splitters
```

```python
from langchain_text_splitters import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(
    chunk_size=2000,
    chunk_overlap=200,
    separators=["\n\n", "\n", "。", ".", " ", ""],
)
chunks = splitter.split_text(document_text)

for i, chunk in enumerate(chunks):
    print(f"Chunk {i}: {chunk[:100]}")
```

Two things easy to get wrong here: `chunk_size` is measured in **characters** by default, not tokens (use a token-aware splitter variant if you need an exact token budget — see [Tokenization](../../concepts/ai/generation/tokenization.md)), and the default separator list is tuned for Latin-script prose — a corpus with real Arabic content needs separators adjusted for Arabic sentence/paragraph punctuation.

## Do you need semantic chunking?

Semantic chunking decides split points based on where the *meaning* of the text shifts — usually by running the text through [embeddings](../../concepts/ai/ingestion/embeddings.md) or a model to detect topic boundaries, rather than cutting at a fixed size. It's slower and more expensive per document than fixed-size or structure-aware chunking, and it is not automatically better for every corpus. Reserve it for document types where structural chunking (headings/paragraphs) demonstrably underperforms — free-flowing transcripts or unstructured notes, for example — rather than defaulting to it everywhere.

## A practical pipeline

1. **Extract structure first** — use [Docling](../../concepts/ai/ingestion/docling.md) (or a format-appropriate tool) rather than extracting raw text blindly.
2. **Chunk along structure** — split on headings/paragraphs via structure-aware or recursive chunking.
3. **Test semantic chunking only where it's needed** — on the subset of documents where structural chunking performs poorly.
4. **Evaluate with Recall@5 and final answer quality** — not by eyeballing chunk boundaries. See the evaluation methodology in [Embedding Model Selection](embedding-model-selection.md).

This is also the lens for [RAG Q&A — Q5](../../interview/interview-01/qa-rag.md#q5--how-do-you-choose-chunk-size-and-overlap) on chunk size/overlap: structure first, a sensible token-based default (e.g. ~512 tokens, 10% overlap) second, and measurement decides any further tuning — never a fixed number applied blindly across every document type.

## Related

- [Document Indexing Pipeline](../../concepts/ai/ingestion/document-indexing.md)
- [Docling](../../concepts/ai/ingestion/docling.md)
- [LlamaIndex](../../concepts/ai/agents/llamaindex.md)
- [Embedding Model Selection](embedding-model-selection.md)
- [Tokenization](../../concepts/ai/generation/tokenization.md)
- [Retrieval-Augmented Generation (RAG)](../../concepts/ai/rag/rag.md)
- [RAG & Grounding Interview Q&A](../../interview/interview-01/qa-rag.md)
