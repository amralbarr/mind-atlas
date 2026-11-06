# AI OCR & Structured Data Extraction

## Description
Pulling structured data — fields, key-value pairs, tables, line items — out of documents, forms, invoices, and receipts, rather than just a flat text dump. Modern tools layer a trained extraction/classification model on top of [OCR](../../../../engineering/concepts/ai/ingestion/ocr.md) (or a vision-language model that reads the page directly), so the output is usable JSON/CSV instead of raw text someone still has to parse by hand. This is the stage that feeds [document-processing](../document-processing/) pipelines and [RAG](../document-understanding/rag-retrieval-augmented-generation.md) ingestion alike.

## Input
- Scanned/photographed documents, PDFs (including no-text-layer scans), forms, invoices, receipts, IDs

## Output
- Structured data: key-value pairs, extracted tables, line items, bounding boxes, confidence scores — usually JSON or CSV

## Related Capabilities
- [Document Processing (IDP)](../document-processing/intelligent-document-processing.md) — end-to-end pipelines that use this extraction step as one stage
- [Document Conversion](../document-conversion/ai-document-conversion.md) — same OCR/layout foundation, aimed at producing an editable document instead of structured fields
- [RAG](../document-understanding/rag-retrieval-augmented-generation.md) — extracted/cleaned text is what gets chunked and indexed downstream
- Underlying concepts already in the handbook — [OCR](../../../../engineering/concepts/ai/ingestion/ocr.md), [Docling](../../../../engineering/concepts/ai/ingestion/docling.md), [Document Indexing](../../../../engineering/concepts/ai/ingestion/document-indexing.md), [Embeddings](../../../../engineering/concepts/ai/ingestion/embeddings.md)

## Software & Platforms

**Open source (self-hosted, free):**
- [Unstructured.io](../../../tools-platforms/document-tools/unstructured-io.md) — open-source library for partitioning/extracting structured elements from any document format
- [Docling](../../../../engineering/concepts/ai/ingestion/docling.md) — layout- and table-aware parsing (already in the handbook as an ingestion concept)

**Paid / managed:**
- [AWS Textract](../../../tools-platforms/document-tools/aws-textract.md) — OCR plus table/form/invoice/ID extraction, usage-based
- [Google Document AI](../../../tools-platforms/document-tools/google-document-ai.md) — OCR, layout parsing, and prebuilt/custom extractors
- [Azure AI Document Intelligence](../../../../engineering/concepts/cloud/azure/azure-ai-services.md) — Microsoft's equivalent, already in the handbook under Azure AI services
- [LlamaParse](../../../tools-platforms/document-tools/llamaparse.md) — parsing-as-a-service tuned for feeding RAG pipelines, from the LlamaIndex team
- [Mistral OCR](../../../tools-platforms/document-tools/mistral-ocr.md) — API-based document OCR with strong multilingual (including Arabic) support

## Applications
- Invoice and receipt processing (accounts payable automation)
- Form/application intake (insurance claims, loan applications, government forms)
- ID/passport/KYC document verification
- Turning scanned archives into searchable, structured records
