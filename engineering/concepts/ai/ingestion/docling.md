# Docling

Docling is an open-source Python library, originally developed by IBM Research's Deep Search team (DS4SD), for parsing real-world documents into a clean, structured format that's ready for [LLM](../generation/llm.md)/[RAG](../rag/rag.md) pipelines. Its core strength over a plain text-extraction library (PyMuPDF, pdfplumber) is that it understands document *structure* — page layout, reading order, table structure, and embedded images/charts — not just raw text.

## When to Use Docling

| Good fit                                                                                   | Poor fit                                                                           |
| ------------------------------------------------------------------------------------------ | ---------------------------------------------------------------------------------- |
| PDFs with tables, multi-column layout, or embedded figures that need to survive extraction | Simple single-column plain-text PDFs (a lighter extractor is enough)               |
| [RAG](../rag/rag.md) ingestion pipelines that need clean Markdown/structured chunks, not a text blob        | Extremely high-throughput ingestion where a lighter/faster extractor is acceptable |
| Mixed-format ingestion (PDF, DOCX, PPTX, HTML, images, audio) through one API              | Real-time, low-latency single-page extraction (model-backed steps add latency)     |
| Need table structure preserved as actual tables, not flattened text                        |                                                                                    |

## Core Concepts

| Term                                    | Meaning                                                                                                                                |
| --------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------- |
| **`DocumentConverter`**                 | The main entry point — takes a file path/URL and runs the full parsing pipeline                                                        |
| **`DoclingDocument`**                   | The unified internal representation of a parsed document (text, tables, images, layout, all in one object), regardless of input format |
| **Layout model**                        | A vision model that detects structural regions on a page (headers, paragraphs, tables, figures, footnotes)                             |
| **Table Structure model (TableFormer)** | A model specifically for reconstructing table structure (rows/columns/cells), not just extracting text inside table bounds             |
| **Export formats**                      | `DoclingDocument` can be exported to Markdown, HTML, plain text, [JSON](../../programming/fundamentals/json.md), or token sequences                                              |

## Supported Input Formats

PDF (with full layout/table/image understanding), DOCX, PPTX, XLSX, HTML, Markdown, images (PNG, TIFF, JPEG), and additional formats including EPUB, email (EML/MSG), and audio/video for transcription-based ingestion.

## Installation

```bash
pip install docling
# or, in a uv-managed project:
uv add docling
```

## Quick Start

```python
from docling.document_converter import DocumentConverter

converter = DocumentConverter()
result = converter.convert("report.pdf")   # local path, or a URL

print(result.document.export_to_markdown())
```

Tables in the source PDF come out as real Markdown tables (or structured [JSON](../../programming/fundamentals/json.md), if exported that way) — not as a wall of space-separated numbers — because the table structure model reconstructs rows and columns rather than just extracting whatever text falls inside the table's bounding box.

## Chunking for RAG

Docling ships a chunker that's layout- and structure-aware, so chunks don't split mid-table or mid-sentence the way naive fixed-length-character chunking can:

```python
from docling.document_converter import DocumentConverter
from docling.chunking import HybridChunker

converter = DocumentConverter()
doc = converter.convert("report.pdf").document

chunker = HybridChunker()
chunks = list(chunker.chunk(doc))

for chunk in chunks:
    text = chunker.contextualize(chunk)   # adds section-heading context to the chunk text
    # embed(text) → store in a vector database
```

This slots directly into the [Document Indexing Pipeline](document-indexing.md)'s "Text Extraction" and "Chunking" steps, replacing a plain PDF-text-extraction library when table/layout fidelity matters.

## Images and Charts

Docling classifies embedded images and, for charts specifically, can convert bar charts, pie charts, and line plots into structured tables or code rather than leaving them as an opaque picture the [LLM](../generation/llm.md) can't reason over. Picture regions can also be exported as cropped images alongside the surrounding text, so a downstream step can run them through a vision model if needed.

## Framework Integrations

Docling has ready-made loaders for [LangChain](../agents/langchain.md), [LlamaIndex](../agents/llamaindex.md), Haystack, and [CrewAI](../agents/crewai.md), so a `DoclingDocument` (or its chunks) can be dropped directly into an existing ingestion pipeline built on one of those frameworks — see [AI Orchestration Frameworks](../../../overviews/ai/orchestration-frameworks.md) for what each of those does.

## Docling vs Simpler PDF Extractors

| | Docling | PyMuPDF / pdfplumber | Unstructured.io |
|---|---|---|---|
| Table structure | Reconstructed (rows/columns) | Text only, tables often flattened/garbled | Reconstructed |
| Layout/reading order | Model-based, handles multi-column | Heuristic, weaker on complex layouts | Model-based |
| Chart understanding | Yes (bar/pie/line → table or code) | No | Partial |
| Speed | Slower (runs layout/table ML models) | Fast (no ML models) | Slower |
| Best for | [RAG](../rag/rag.md) pipelines needing structural fidelity | Quick text-only extraction | Comparable alternative to Docling |

## Related

- [Document Indexing Pipeline](document-indexing.md) — the broader pipeline Docling's extraction/chunking step plugs into
- [Retrieval-Augmented Generation (RAG)](../rag/rag.md) — the system this extracted, chunked content ultimately feeds
- [AI Orchestration Frameworks](../../../overviews/ai/orchestration-frameworks.md) — [LangChain](../agents/langchain.md)/[LlamaIndex](../agents/llamaindex.md), which Docling integrates with directly
- [Embeddings](embeddings.md) — what happens to Docling's output chunks next in a [RAG](../rag/rag.md) pipeline
- [Chunking Strategies & Libraries](../../../overviews/ai/chunking-strategies.md) — how Docling's `HybridChunker` compares to [LangChain](../agents/langchain.md), [LlamaIndex](../agents/llamaindex.md), Unstructured, and Chonkie
