# Outlines

**Type:** Open source (Apache 2.0) — by .txt (dottxt)

## Category
Constrained-generation library for LLMs

## AI Capabilities
- Guarantees output matching a JSON Schema, Pydantic model, regex, grammar, or multiple-choice set *during* generation (constrained decoding), not via post-hoc parsing/retries
- Supports local inference (Hugging Face Transformers, llama.cpp), self-hosted serving (vLLM, Ollama), and hosted APIs (OpenAI, Gemini)
- Supports streaming, nested structures, and batch generation

## Related AI Solutions
- [Structured Data Extraction from Text](../../solutions/text/text-to-structured-data/structured-data-extraction-from-text.md)

## Notes
- Compare to [Instructor](instructor.md): Instructor validates-and-retries against a schema after generation; Outlines constrains token sampling so invalid output is never produced in the first place.
