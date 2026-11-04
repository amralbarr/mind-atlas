# OCR (Optical Character Recognition)

OCR converts an image of text — a scanned page, a photographed document, a PDF with no embedded text layer — into actual machine-readable characters. It's the step that sits before everything else in a document pipeline: `OCR → cleaning/normalization → chunking → embeddings → retrieval`, which is why it shows up as a black-box first stage in so many pipeline diagrams throughout this handbook (see [Pipeline Orchestration](../infrastructure/pipeline-orchestration.md), [Decouple Pipeline Stages](../../distributed-systems/patterns/decouple-stages.md)) without those diagrams explaining what actually happens inside it.

## How it works, at a level worth knowing

Two stages, whether the engine is classical or deep-learning-based:

1. **Layout/text detection** — find where the text actually is on the page (text regions, columns, reading order, tables vs. paragraphs).
2. **Character/word recognition** — convert each detected text region into actual characters, typically via a trained recognition model (classical: feature-based classifiers; modern: CNN/Transformer-based sequence models).

Quality depends heavily on scan resolution, contrast, skew, font, handwriting (much harder than print), and — critically for this handbook's Arabic-content use cases — how well the engine's recognition model was trained on the target script, since Arabic's connected cursive letterforms behave very differently from Latin script's discrete characters.

## OCR artifacts: what actually goes wrong

"OCR artifacts" means the text OCR produces doesn't match the real text — and these errors propagate into every downstream step (chunking, embedding, indexing) silently, since nothing downstream knows the text is wrong unless it's checked.

| Artifact | What it looks like | Why it happens |
|---|---|---|
| **Character confusion** | `"rn"` misread as `"m"`, `"l"`/`"1"`/`"I"` confused | Visually similar glyphs, especially at low resolution or in certain fonts |
| **Broken/merged words** | Words split with spurious spaces, or run together with no space at all | Layout detection misjudging word/character boundaries |
| **Reading-order errors** | Multi-column text interleaved out of order; tables flattened into nonsensical text | Layout analysis failing to correctly segment columns/regions before recognition |
| **Diacritic/accent loss or corruption** | Accented or diacritic-marked characters dropped or misrecognized | Small marks are easy to miss at low resolution — this hits Arabic (see [Arabic Normalization for Retrieval](../retrieval/analyzer-pipeline/arabic-normalization.md)) and any other diacritic-heavy script especially hard |
| **Right-to-left text reversed or interleaved wrong** | Arabic text extracted in the wrong visual/logical order | Some extraction tools don't correctly handle bidirectional (RTL/LTR mixed) text layout |
| **Table structure loss** | A table's rows/columns collapse into an unstructured wall of text | Plain OCR has no concept of table structure unless the engine specifically models it |

**The critical implication: no amount of downstream [text normalization](../retrieval/analyzer-pipeline/text-normalization.md) can fix text that was extracted wrong in the first place.** If OCR output is garbled, [normalization](../retrieval/analyzer-pipeline/text-normalization.md), [stemming](../retrieval/analyzer-pipeline/stemming.md), and embedding all operate on corrupted input — the fix has to happen at the OCR/extraction stage itself (a better engine, better scan quality, or a human-reviewed correction pass), not further down the pipeline. Before investigating anything else in a pipeline producing bad retrieval results, pull a random sample of extracted chunks and actually read them.

## Libraries and technologies

| Tool | Type | Notes |
|---|---|---|
| **Tesseract** | Open-source, self-hosted | The long-standing open-source default; supports 100+ languages including Arabic, but generally weaker on complex layouts and handwriting than newer deep-learning engines |
| **EasyOCR** | Open-source, self-hosted | Deep-learning-based (PyTorch), broad multilingual support including Arabic, easier to get started with than Tesseract for non-Latin scripts |
| **PaddleOCR** | Open-source, self-hosted | Deep-learning-based, strong multilingual and layout-detection support, widely used in production pipelines |
| **[AWS](../../cloud/infrastructure/aws.md) Textract** | Managed cloud API | Includes table and form structure extraction, not just raw text |
| **[Azure](../../cloud/azure/azure.md) AI Document Intelligence** | Managed cloud API | Layout- and table-aware extraction; see [Azure AI services](../../cloud/azure/azure-ai-services.md) |
| **Google Cloud Vision OCR** | Managed cloud API | General-purpose OCR, part of Google's broader Vision API |
| **[Docling](docling.md)** | Open-source, self-hosted | Doesn't do raw OCR itself as its primary function, but integrates OCR engines (including EasyOCR/Tesseract backends) as part of its broader layout- and table-aware document parsing pipeline for scanned PDFs |

## Related

- [Docling](docling.md) — document parsing pipeline that integrates OCR for scanned PDFs
- [Document Indexing Pipeline](document-indexing.md) — where OCR sits as the first stage
- [Arabic Normalization for Retrieval](../retrieval/analyzer-pipeline/arabic-normalization.md) — Arabic-specific OCR failure modes and how they interact with normalization
- [Text Normalization](../retrieval/analyzer-pipeline/text-normalization.md)
- [Pipeline Orchestration](../infrastructure/pipeline-orchestration.md) — where OCR fits as a pipeline stage
