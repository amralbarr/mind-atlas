# Structured Data Extraction from Text

## Description
Turning unstructured or semi-structured free text into structured data (JSON, a database row, a typed object) that conforms to a schema you define — "extract name, date, amount, and line items from this email" rather than a fixed, pre-built entity set. Built on an LLM's [structured output](../../../../engineering/concepts/ai/generation/structured-output.md)/constrained-decoding capability: the schema is defined once (often as a Pydantic/JSON Schema model), and the model's output is guaranteed to validate against it instead of needing fragile regex or manual parsing of free-form LLM text.

## Input
- Unstructured text (emails, contracts, forms, chat transcripts, articles, support tickets)
- A target schema (fields, types, nested structures) describing what to extract

## Output
- A schema-validated structured object (JSON) per input document, ready to insert into a database or call another API with

## Related Capabilities
- [Sentiment Analysis, Entity Extraction & Text Classification](../text-analysis/sentiment-and-entity-analysis.md) — overlaps heavily; that capability covers pre-built categories (sentiment, standard entities), this one covers an arbitrary custom schema
- [RAG](../../documents/document-understanding/rag-retrieval-augmented-generation.md) — often the step right before extraction when the source is a large document corpus rather than a single short text
- Underlying concepts already in the handbook: [Structured Output / JSON Mode](../../../../engineering/concepts/ai/generation/structured-output.md), [Function / Tool Calling](../../../../engineering/concepts/ai/agents/tool-calling.md) (tool-call arguments are the same underlying mechanism)

## Software & Platforms

**Open source (self-hosted, free):**
- [Instructor](../../../tools-platforms/text-and-llm-tools/instructor.md) — Pydantic-based structured-output library for LLMs, with Python/TypeScript/Ruby/Elixir implementations
- [Outlines](../../../tools-platforms/text-and-llm-tools/outlines.md) — constrained-generation library guaranteeing schema-valid output at the token level, across many model backends
- [LangExtract](../../../tools-platforms/text-and-llm-tools/langextract.md) — Google's LLM-powered extraction library with precise source grounding (maps every extraction back to its exact character offset)

**Paid / managed:**
- [LlamaExtract](../../../tools-platforms/text-and-llm-tools/llamaextract.md) — LlamaCloud's managed schema-based extraction service, with multiple accuracy/cost tiers per page

## Applications
- Invoice/receipt/form field extraction into a database
- Resume parsing into structured candidate profiles
- Extracting structured action items, decisions, and dates from meeting transcripts or emails
- Populating CRM/ERP records from unstructured correspondence
- Turning free-text clinical or legal notes into structured, queryable fields

## Applications note
For scanned/image-based documents (PDFs, photographed forms) rather than plain text, this pairs with OCR/document-parsing (layout-aware extraction) — this note covers extracting structure from text that's already machine-readable.
