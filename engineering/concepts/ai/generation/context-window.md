# Context Window

## What is it?

The **context window** is the maximum number of [tokens](tokenization.md) an [LLM](llm.md) can attend to at once — the total budget shared by the [system prompt](system-prompt.md), conversation history, any retrieved documents, and the model's own output. Once that budget is used up, older content has to be dropped, summarized, or never sent in the first place; the model has no memory of anything outside its current context window unless something external (a database, a [RAG](../rag/rag.md) retriever, a harness's memory system) re-supplies it on the next call.

```
Context window (e.g. 128,000 tokens)
┌─────────────────────────────────────────────────────────┐
│ System prompt │ Conversation history │ Retrieved context │ ← Output tokens
└─────────────────────────────────────────────────────────┘
        all of this together must fit inside the limit
```

## Why it's finite

Context windows are finite because of how the underlying transformer architecture works: self-attention compares every token to every other token in the context, so compute and memory cost grow roughly with the square of the context length (naive attention is O(n²)). Doubling the context window doesn't just double the cost — it roughly quadruples it, before architectural tricks are applied. This is why context length has historically been one of the more expensive dimensions to scale, and why it took specific architectural work (efficient attention variants, sliding-window attention, position-encoding schemes that generalize to longer sequences) to push windows from a few thousand tokens to hundreds of thousands or millions.

## Long-context models

Context windows have grown dramatically. As of 2026, flagship models from the major labs have largely converged around **1 million tokens** (roughly 750,000 words), with some models advertising far larger windows (10 million tokens) aimed at bulk archival or codebase-scale tasks rather than deep reasoning over all of it.

| Class | Typical window | Use case |
|---|---|---|
| Smaller/cheaper models | 128K–256K tokens | Most chat and [RAG](../rag/rag.md) use cases |
| Flagship models | ~1M tokens | Long documents, large codebases, extended agent sessions |
| Extreme long-context models | Up to ~10M tokens | Bulk archival search, not deep multi-step reasoning |

**Important caveat: advertised ≠ effective context.** A model's stated maximum window is not the same as how well it actually uses that context. Model quality on "needle in a haystack" style retrieval and multi-hop reasoning tends to degrade well before the advertised limit is reached — a phenomenon informally called "lost in the middle," where content in the middle of a long context is attended to less reliably than content near the start or end. Treating the advertised window as a hard reliability guarantee, rather than a hard capacity limit, is a common mistake.

## Managing a limited context window

Since context is always finite in practice (even at 1M tokens, cost and latency scale with how much you send), production systems actively manage what goes into it:

| Technique | What it does |
|---|---|
| **Retrieval ([RAG](../rag/rag.md))** | Only send the most relevant chunks of a larger corpus, not the whole thing — see [RAG](../rag/rag.md) |
| **Summarization / compaction** | Periodically compress older conversation turns into a shorter summary instead of keeping full history |
| **Truncation** | Drop the oldest turns once a token budget is hit (simplest, but loses information) |
| **Sliding window** | Keep only the most recent N turns/tokens, discarding older ones |
| **Prompt caching** | Some providers let you cache a static prefix (e.g. a long [system prompt](system-prompt.md)) so repeated calls don't re-pay the cost of re-processing it |

An [AI agent harness](../agents/ai-agent-harness.md) is typically the piece of software responsible for this — deciding when to summarize, what to keep, and what to drop as a session grows.

## Context window vs. token limit vs. rate limit

These three get conflated but are distinct:

| Term | What it constrains |
|---|---|
| **Context window** | Architectural limit — the max tokens a model can process in a single call |
| **Token limit (per project/budget)** | A cost or product decision to cap usage, unrelated to the model's actual capability |
| **Rate limit** | How many requests/tokens per minute an [API key](../../security/auth/api-key.md) is allowed to send — an infrastructure constraint, not a model constraint |

See [llm.md](llm.md)'s "Token limit" section for how this played out concretely for one project (a fixed comparison table of specific models' windows and why chunking mattered given those numbers).

## Related

- [Tokenization](tokenization.md) — what a token actually is and how text is converted into them
- [Large Language Models (LLMs)](llm.md) — project-specific token limit numbers and chunking rationale
- [Retrieval-Augmented Generation (RAG)](../rag/rag.md) — the primary technique for working around a limited context window
- [AI Agent Harness](../agents/ai-agent-harness.md) — owns context/state management across a long-running session
- [Document Indexing Pipeline](../ingestion/document-indexing.md) — chunking strategy that keeps retrieved content within budget
