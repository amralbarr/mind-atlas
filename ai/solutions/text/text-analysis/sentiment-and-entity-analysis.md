# Sentiment Analysis, Entity Extraction & Text Classification

## Description
Analyzing free text to derive signals about it: sentiment (positive/negative/neutral/mixed, overall or per-entity), named entities (people, organizations, locations, products), key phrases, and category/topic classification. Used for understanding large volumes of unstructured text — reviews, support tickets, social mentions, survey responses — without reading each one manually. Not to be confused with the [IR analyzer pipeline also called "text analysis"](../../../../engineering/concepts/ai/retrieval/text-analysis.md) in search engines (tokenization/stemming for indexing) — this is about deriving meaning/labels from text, not preparing it for search.

## Input
- Free-form text: reviews, support tickets, survey responses, social media posts, transcripts, emails

## Output
- Sentiment label(s) and confidence score, optionally per entity/aspect
- A list of extracted named entities and key phrases
- A classification label (topic, intent, category) per document

## Related Capabilities
- [Structured Data Extraction from Text](../text-to-structured-data/structured-data-extraction-from-text.md) — entity extraction output is itself a form of structured data; the two overlap heavily, with text analysis leaning toward pre-built categories (sentiment, standard entity types) and structured-data extraction toward a custom schema
- [AI Customer Support Agents](../text-to-text/ai-customer-support-agents.md) — ticket routing/prioritization often runs sentiment and intent classification first
- Underlying concepts already in the handbook: [NLP](../../../../engineering/concepts/ai/nlp.md)

## Software & Platforms

**Open source (self-hosted, free):**
- [spaCy](../../../tools-platforms/text-and-llm-tools/spacy.md) — industrial-strength Python NLP library with built-in named entity recognition, classification pipelines, and pretrained models for 70+ languages

**Paid / managed:**
- [AWS Comprehend](../../../tools-platforms/text-and-llm-tools/aws-comprehend.md) — sentiment, entity recognition, key phrases, and custom classification as a managed AWS API
- [Azure AI Language](../../../tools-platforms/text-and-llm-tools/azure-ai-language.md) — sentiment/opinion mining, NER (79+ languages GA), key phrase extraction, and custom classification
- [Google Cloud Natural Language](../../../tools-platforms/text-and-llm-tools/google-cloud-natural-language.md) — sentiment, entity sentiment, entity analysis, content classification, and syntax analysis

## Applications
- Customer review and social media monitoring
- Support ticket triage/prioritization by sentiment and urgency
- Brand/competitor mention tracking
- Survey response analysis at scale
- Compliance/content moderation (flagging sensitive entities or topics)

## Market note
General-purpose LLMs can now perform all of these tasks via prompting with comparable or better accuracy than the purpose-built classifiers above, especially for nuanced sentiment or domain-specific categories — the dedicated APIs still win on cost-per-call at very high volume and on compliance-friendly fixed-schema output (a stable, auditable label set rather than free-form LLM text).
