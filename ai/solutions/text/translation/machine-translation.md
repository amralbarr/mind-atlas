# Machine Translation

## Description
Translating text (or speech transcripts) from one language to another automatically. Modern machine translation is almost entirely neural (encoder-decoder transformer models, the same underlying architecture family as [LLMs](../../../../engineering/concepts/ai/generation/llm.md)), ranging from dedicated translation-only models (DeepL, NLLB, Argos) to general-purpose LLMs being prompted to translate. Dedicated translation engines are typically faster, cheaper per character, and more consistent for high-volume/low-latency use than routing translation through a general chat LLM.

## Input
- Source text (or batches of text/documents) and a target language
- Optionally: a glossary/terminology list for domain-specific consistency

## Output
- Translated text in the target language, often alongside a confidence/quality signal

## Related Capabilities
- [AI Writing Assistants & Content Generation](../writing-and-content-generation/ai-writing-assistants.md) — localized content generation often pairs translation with a rewrite pass for tone/register
- [Text Analysis](../text-analysis/sentiment-and-entity-analysis.md) — multilingual sentiment/entity tools often translate first, then analyze
- Underlying concepts already in the handbook: [LLM](../../../../engineering/concepts/ai/generation/llm.md)

## Software & Platforms

**Open source (self-hosted, free):**
- [LibreTranslate](../../../tools-platforms/text-and-llm-tools/libretranslate.md) — self-hosted translation API server with a web UI, built on Argos Translate
- [Argos Translate](../../../tools-platforms/text-and-llm-tools/argos-translate.md) — offline Python translation library with downloadable language packages

**Paid / managed:**
- [DeepL](../../../tools-platforms/text-and-llm-tools/deepl.md) — widely regarded as the highest-quality translation API for its supported language pairs
- [Google Cloud Translation](../../../tools-platforms/text-and-llm-tools/google-cloud-translation.md) — broadest language coverage, deeply integrated into Google Cloud
- [Azure AI Translator](../../../tools-platforms/text-and-llm-tools/azure-ai-translator.md) — Microsoft's managed translation API, integrated into the Azure AI Language/Foundry suite

## Applications
- Website and app localization (UI strings, help centers, product listings)
- Real-time chat/support translation for multilingual customer bases
- Document and contract translation
- Subtitle/caption translation for video content

## Market note
Self-hosted engines (LibreTranslate/Argos) trade translation quality for zero per-character cost and full data privacy — they're meaningfully behind DeepL/Google/Azure on fluency for most language pairs, so the choice is a real quality-vs-control tradeoff, not just a pricing one.
