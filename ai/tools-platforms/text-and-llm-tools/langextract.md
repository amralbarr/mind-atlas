# LangExtract

**Type:** Open source (Apache 2.0) — by Google (not an officially supported Google product)

## Category
LLM-powered structured information extraction library

## AI Capabilities
- Extracts structured data from unstructured text from user-defined instructions and a handful of examples — no fine-tuning required
- Maps every extraction back to its exact character offset in the source text (precise source grounding) for auditability
- Intelligent chunking and multi-pass parallel extraction for long documents, improving recall
- Works with Gemini models and with open-source/on-device models

## Related AI Solutions
- [Structured Data Extraction from Text](../../solutions/text/text-to-structured-data/structured-data-extraction-from-text.md)

## Notes
- Released by Google on July 30, 2025; used for cases like pulling medications/dosages from clinical notes or contract clauses for compliance review.
- Source-grounding (knowing exactly where in the text each field came from) is its main differentiator versus [Instructor](instructor.md)/[Outlines](outlines.md).
