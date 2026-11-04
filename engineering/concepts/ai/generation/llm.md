# Large Language Models (LLMs)

## What is it?

A Large Language Model (LLM) is an AI model trained on vast amounts of text that can understand and generate human language. LLMs can answer questions, summarize documents, explain concepts, write code, and carry out conversations. In this project, the LLM is the final step in the [RAG](../rag/rag.md) pipeline — it reads the retrieved document chunks and writes a natural-language answer.

## What the LLM does in this project

The LLM does NOT search documents — that is the retriever's job. The LLM only:
1. Reads the retrieved and permission-filtered document chunks
2. Reads the user's question
3. Generates a fluent, accurate answer based on the provided context
4. Cites which documents the answer came from

```
[Retrieved Chunks from Finance_Q3_Report_2026.txt]
+ [User Question: "What was Q3 revenue?"]
         ↓
         LLM
         ↓
"Based on the Q3 Finance Report, revenue for Q3 2026 reached
 2.4 million, exceeding the target by 12%."
```

## Hallucination

**Hallucination** is when an LLM generates text that sounds confident and fluent but is factually wrong or invented. This is a serious problem in AI systems.

[RAG](../rag/rag.md) mitigates hallucination by providing the LLM with specific context to base its answer on. The prompt instructs the LLM:
```
"Answer ONLY based on the provided context.
 If the answer is not in the context, say:
 'I could not find this information in your authorized documents.'"
```

This prevents the LLM from inventing information when no relevant document is found.

## LLM options for this project

| Option | Provider | Access | Notes |
|---|---|---|---|
| **GPT-4o** | OpenAI API | [API key](../../security/auth/api-key.md) required | Best quality, paid |
| **GPT-4o-mini** | OpenAI API | [API key](../../security/auth/api-key.md) required | Cheaper, good for prototypes |
| **[Azure](../../cloud/azure/azure.md) OpenAI** | [Microsoft Azure](../../cloud/azure/azure.md) | [Azure](../../cloud/azure/azure.md) subscription | Same models, hosted in [Azure](../../cloud/azure/azure.md) |
| **Llama 3** via Ollama | Local | Free, runs on VM | No API cost, runs locally |
| **Mistral** via Ollama | Local | Free, runs on VM | Lighter, less accurate |

For a student project with API access: **GPT-4o-mini** is recommended (low cost, good quality).
For a fully local setup: **Ollama with Llama 3** — runs as a [Docker](../../containers/docker.md) container on the VM.

## The prompt template

The prompt is how the [RAG](../rag/rag.md) system communicates with the LLM. Structure:

```
System message:
You are an internal document assistant for [Company Name].
Your job is to answer employee questions based on internal documents.
You must ONLY use the provided document context to answer.
You must NEVER reveal or reference documents the user is not authorized to access.
If the answer is not found in the context, say: "I could not find this in your authorized documents."
Always mention which document(s) your answer is based on.

User message:
CONTEXT FROM AUTHORIZED DOCUMENTS:
---
[chunk 1 text] (Source: Finance_Q3_Report_2026.txt)
[chunk 2 text] (Source: Finance_Budget_2026.txt)
---

QUESTION: What was the Q3 revenue?
```

## Token limit

Every LLM has a maximum [context window](context-window.md) — the total number of tokens (words) it can process at once. See [Tokenization](tokenization.md) for how text is actually converted into tokens, and [Context Window](context-window.md) for the general architectural concept behind this limit.
- GPT-4o: 128,000 tokens
- GPT-4o-mini: 128,000 tokens
- Llama 3 8B: 8,000 tokens

This is why chunking is important — you only send the top 3–5 most relevant chunks, not the entire document. See [Document Indexing Pipeline](../ingestion/document-indexing.md) for how chunking is done upstream.

## Cost estimation (OpenAI)

For a student project with light usage:
- GPT-4o-mini: $0.15 per 1M input tokens, $0.60 per 1M output tokens
- A typical [RAG](../rag/rag.md) query with 3 chunks ≈ 1,000 tokens input + 200 tokens output
- 100 test queries ≈ 120,000 tokens ≈ $0.02 total

Cost is not a concern for a prototype.

## How it fits in this project

The LLM is integrated by Member 1 (Computer Science) in `ai/rag/rag_pipeline.py`. The LLM is the final step — it only receives content that has already passed the permission filter. Member 4 (Networking) is responsible for deploying the LLM service (Ollama container or configuring API connectivity).

## Related

- [Retrieval-Augmented Generation (RAG)](../rag/rag.md)
- [Embeddings](../ingestion/embeddings.md)
- [AI Orchestration Frameworks](../../../overviews/ai/orchestration-frameworks.md)
- [Tokenization](tokenization.md) — how text becomes the tokens this note's limits are measured in
- [Context Window](context-window.md) — the general architectural concept behind the token limit
- [Prompt Engineering](prompt-engineering.md) — techniques for structuring the prompt template shown above
- [Temperature & Sampling Parameters](sampling-parameters.md) — controls for how the LLM's output is generated
- [Fine-tuning](../infrastructure/fine-tuning.md) — the alternative to [RAG](../rag/rag.md) when behavior, not knowledge, needs to change
- [LLM Evaluation](../evaluation/llm-evaluation.md) — how to measure whether this LLM/prompt setup is actually working well
- [Nextcloud RAG Case Study](../../../guides/cloud/nextcloud-rag-case-study/nextcloud.md)
