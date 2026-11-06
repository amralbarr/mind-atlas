# Document & Meeting Summarization

## Description
Condensing a long document, article, or recorded conversation into a shorter form — a paragraph abstract, bullet-point key points, or (for meetings) a transcript plus summary, decisions, and action items. Meeting summarization specifically combines speech-to-text transcription with an LLM summarization pass over the transcript. Document summarization at scale (long reports, long contracts) typically needs chunking/map-reduce strategies once the document exceeds the model's [context window](../../../../engineering/concepts/ai/generation/context-window.md).

## Input
- A long document, article, email thread, or chat log
- A recorded or live meeting (audio/video) for meeting-summarization tools

## Output
- A short abstract or bullet-point summary
- For meetings: a full transcript, a summary, decisions made, and extracted action items (often itself a [text-to-structured-data](../text-to-structured-data/structured-data-extraction-from-text.md) output)

## Related Capabilities
- [AI Writing Assistants & Content Generation](../writing-and-content-generation/ai-writing-assistants.md) — the same LLM capability run in the opposite direction (expanding instead of condensing)
- [Structured Data Extraction from Text](../text-to-structured-data/structured-data-extraction-from-text.md) — action items/decisions pulled from a meeting summary are a structured-extraction task
- [RAG](../../documents/document-understanding/rag-retrieval-augmented-generation.md) — for summarizing across many documents at once rather than one at a time, retrieval narrows down what to summarize first
- Underlying concepts already in the handbook: [LLM](../../../../engineering/concepts/ai/generation/llm.md), [Context Window](../../../../engineering/concepts/ai/generation/context-window.md) (why long documents need chunking before summarization)

## Software & Platforms

**Open source (self-hosted, free):**
- [Hugging Face Transformers](../../../tools-platforms/text-and-llm-tools/hugging-face-transformers.md) — open-source library with pretrained summarization models (e.g. BART, PEGASUS) you can self-host and fine-tune

**Paid / managed:**
- [Otter.ai](../../../tools-platforms/text-and-llm-tools/otter-ai.md) — meeting transcription, AI summaries, and action-item extraction
- [Fireflies.ai](../../../tools-platforms/text-and-llm-tools/fireflies-ai.md) — meeting recording, transcription, and AI summaries across video-call platforms, with CRM integrations
- [Fathom](../../../tools-platforms/text-and-llm-tools/fathom.md) — free meeting recorder/notetaker with AI summaries and call highlights

## Applications
- Meeting notes, decisions, and action-item capture (sales calls, standups, interviews)
- Long-document and report condensation (legal, research, news)
- Email thread and support-ticket summarization for faster triage
- TL;DR generation for articles and internal documentation

## Market note
For plain document summarization, most teams now just prompt a general-purpose LLM (via its own chat UI or API) rather than reaching for a dedicated summarization product — dedicated tools mostly add value for meeting-specific workflows (calendar/video-call integration, speaker diarization, CRM sync).
