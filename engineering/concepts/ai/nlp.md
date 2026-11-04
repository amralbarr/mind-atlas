# NLP (Natural Language Processing)

NLP is the broad field concerned with getting computers to process and extract meaning from human language — everything from "is this review positive or negative" to "what are the named people and organizations in this document" to "summarize this paragraph." It's the umbrella field that [Azure AI Language](../cloud/azure/azure-ai-services.md) (and services like it) packages into ready-to-call APIs, and the same field [LLMs](generation/llm.md) have largely reshaped over the last few years.

## The core task taxonomy

These are the classic, named NLP tasks — the same ones [Azure AI Language](../cloud/azure/azure-ai-services.md) exposes as distinct API calls:

| Task                               | What it does                                                                                                                                    | Example                                                                              |
| ---------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------ |
| **Sentiment analysis**             | Classifies text as positive, negative, neutral (or a score along that spectrum)                                                                 | "This product is amazing" → positive                                                 |
| **Key phrase extraction**          | Pulls out the main topics/phrases from a text without summarizing it                                                                            | A product review → `["battery life", "screen quality"]`                              |
| **Named Entity Recognition (NER)** | Identifies and categorizes specific entities — people, organizations, locations, dates                                                          | "Satya Nadella leads Microsoft" → `Person: Satya Nadella`, `Organization: Microsoft` |
| **PII detection**                  | A specialized form of NER focused specifically on personally identifiable information — names, phone numbers, national IDs, credit card numbers | Used to redact or flag sensitive content before storage/logging                      |
| **Summarization**                  | Condenses a longer text into a shorter one while preserving the key information                                                                 | A 10-page report → a 3-sentence summary                                              |
| **Text classification**            | Assigns a text to one or more predefined categories                                                                                             | A support ticket → `category: billing`                                               |

## Classical NLP vs. LLM-based NLP — the real industry shift

This is the distinction that actually matters for a design decision, not just trivia:

| | Classical / task-specific NLP | [LLM](generation/llm.md)-based NLP |
|---|---|---|
| **How it works** | A separate model trained specifically for each task (a sentiment classifier, a NER model, a summarization model) | One general-purpose [LLM](generation/llm.md), given the task via a prompt (zero-shot or few-shot) — no task-specific training required |
| **Example** | [Azure AI Language](../cloud/azure/azure-ai-services.md)'s sentiment/NER/summarization endpoints, spaCy's NER pipeline | "Extract the named entities from this text" as a prompt to GPT-4o or any other capable [LLM](generation/llm.md) |
| **Accuracy on the exact task it was built for** | Often very strong — purpose-built and tuned for that one task | Good, often competitive, but not always as precise on narrow, well-defined tasks |
| **Flexibility** | Fixed to the tasks the service actually offers | Can handle a completely novel task description with no retraining — just change the prompt |
| **Cost/latency per call** | Typically cheap and fast — small, specialized models | Typically more expensive and slower per call — a large general model doing more work |
| **Combining multiple tasks** | One API call per task | Often one prompt can do sentiment + entities + summary together in a single call |

Neither replaced the other outright — the practical decision is: reach for a dedicated service like [Azure AI Language](../cloud/azure/azure-ai-services.md) when the task is one of its well-defined, high-volume, cost-sensitive operations; reach for a general [LLM](generation/llm.md) when the task is novel, needs flexible instructions, or benefits from combining several NLP operations in one pass alongside actual reasoning.

## Where NLP output feeds the rest of this handbook's AI pipeline

- **[Embeddings](ingestion/embeddings.md)** are themselves an NLP technique — turning text into a numeric representation of its meaning, which is what makes [vector search](retrieval/vector-database.md) possible at all.
- **[Tokenization](generation/tokenization.md)** is the NLP preprocessing step every [LLM](generation/llm.md) (and every classical NLP model) depends on.
- **[RAG](rag/rag.md)** combines retrieval (an NLP/search problem) with generation (an NLP/language-modeling problem) into one pipeline.
- PII detection specifically matters for the same reason [prompt injection](../security/attacks/prompt-injection.md) and [access control](retrieval/vector-database.md#metadata-filtering) matter in an enterprise [RAG](rag/rag.md) system — sensitive content needs to be identified and handled correctly before it's indexed, logged, or shown to the wrong user.

## Related

- [Azure AI services](../cloud/azure/azure-ai-services.md) — [Azure](../cloud/azure/azure.md) AI Language is the managed implementation of the classic NLP task taxonomy above
- [Large Language Models (LLMs)](generation/llm.md) — the general-purpose alternative to task-specific NLP models
- [Embeddings](ingestion/embeddings.md) — NLP's technique for turning text into a numeric, comparable representation
- [Tokenization](generation/tokenization.md) — the preprocessing step underlying both classical and [LLM](generation/llm.md)-based NLP
- [RAG](rag/rag.md)
- [Structured Output](generation/structured-output.md) — how an LLM's free-text NLP output gets turned into the kind of structured fields (entities, categories, scores) a classic NLP API would return natively
