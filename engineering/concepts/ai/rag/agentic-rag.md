# Agentic RAG

## What is it?

Agentic [RAG](rag.md) is [Retrieval-Augmented Generation](rag.md) where an [LLM](../generation/llm.md) **agent** — not a fixed, hand-coded pipeline — decides when to retrieve, what to retrieve, how many times to retrieve, and which tool/source to retrieve from. In classic [RAG](rag.md) the flow is a straight line the developer wrote in advance: embed the query, search once, stuff the top-N chunks into the prompt, generate. In agentic RAG, retrieval itself becomes one tool among several that the model can choose to call, re-call with a different query, or skip entirely, based on its own reasoning about whether it has enough information yet.

```
Classic RAG (fixed pipeline):
Query → Embed → Retrieve (once) → Stuff context → Generate → Answer

Agentic RAG (agent-directed):
Query → Agent reasons: "do I need to search? what for?"
           ↓
      [search_docs tool] → results → "is this enough, or do I need more?"
           ↓                              ↓
      not enough → reformulate query → search again
           ↓
      enough → [maybe call another tool: SQL lookup, web search, calculator]
           ↓
      Generate final answer (with citations)
```

## Why go beyond a fixed pipeline?

| Limitation of classic [RAG](rag.md) | What agentic RAG addresses |
|---|---|
| One retrieval pass, fixed top-N — if the first search misses, there's no recovery | The agent can re-query, rephrase, or broaden/narrow the search if the first pass looks insufficient |
| Can only search one index/source | The agent can choose between multiple tools — a vector store, a [SQL](../../databases/relational/sql.md) database, a web search API — based on the question |
| Cannot decompose a multi-part question | Multi-hop questions ("compare X's Q1 and Q3 numbers") can be broken into several targeted retrieval calls |
| No self-check on retrieved evidence | The agent can evaluate whether retrieved chunks actually answer the question before generating, and retry if not |
| Retrieves even when retrieval isn't needed | The agent can skip retrieval entirely for questions it can answer directly (small talk, math, already-in-context info) |

The tradeoff is cost and latency: each reasoning/retrieval round is an extra [LLM](../generation/llm.md) call, so agentic RAG is slower and more expensive per query than a single-pass pipeline. It's worth it when query difficulty varies a lot and a fixed single-shot retrieval regularly under- or over-fetches.

## How it's built

Agentic RAG is not a separate framework — it's a design pattern built on two things that already exist independently in this handbook:

1. **[Function / Tool Calling](../agents/tool-calling.md)** — retrieval is exposed to the model as a callable tool (e.g. `search_documents(query: str) -> list[Chunk]`), the same wire mechanism used for any other tool.
2. **An [AI Agent Harness](../agents/ai-agent-harness.md)** — the surrounding loop that lets the model call that tool multiple times, inspect results, decide to call it again with different arguments, and eventually stop and produce a final answer.

In practice this is usually implemented with an agent framework — [Pydantic AI](../agents/pydantic-ai.md), [LangGraph](../agents/langgraph.md), or similar (see [AI Orchestration Frameworks](../../../overviews/ai/orchestration-frameworks.md)) — where retrieval is just one `@agent.tool`-decorated function alongside others, and the framework's harness manages the reasoning loop.

```python
from pydantic_ai import Agent, RunContext

agent = Agent("openai:gpt-4o", instructions="Answer using the search tool when you need facts.")

@agent.tool
async def search_documents(ctx: RunContext, query: str, k: int = 5) -> list[str]:
    """Search the knowledge base for chunks relevant to `query`."""
    return await vector_store.search(query, top_k=k)

# The model itself decides whether/how many times to call search_documents
# before producing a final answer — the developer doesn't hardcode the call.
result = await agent.run("Compare Q1 and Q3 revenue, then explain the trend.")
```

## Common agentic RAG patterns

| Pattern | What it does |
|---|---|
| **Query rewriting / decomposition** | The agent breaks a complex question into sub-queries and retrieves for each separately |
| **Iterative retrieval (retrieve-and-refine)** | Retrieve → judge sufficiency → if insufficient, reformulate and retrieve again |
| **Multi-source routing** | The agent picks which tool/index to query (vector store vs. [SQL](../../databases/relational/sql.md) vs. web search) based on question type |
| **Self-critique / re-ranking** | The agent evaluates retrieved chunks against the question and discards irrelevant ones before generating |
| **Corrective [RAG](rag.md) (CRAG)** | If retrieved documents are graded as low-relevance, fall back to a broader search (e.g. the web) instead of generating from weak context |

## Related

- [Retrieval-Augmented Generation (RAG)](rag.md) — the fixed-pipeline baseline this pattern extends
- [Function / Tool Calling](../agents/tool-calling.md) — the mechanism that exposes retrieval as something an agent can choose to invoke
- [AI Agent Harness](../agents/ai-agent-harness.md) — the loop that lets the agent call the retrieval tool repeatedly and decide when to stop
- [Pydantic AI](../agents/pydantic-ai.md) — an agent framework commonly used to build this pattern
- [Hybrid Search](../retrieval/hybrid-search.md) — often the retrieval tool itself, regardless of whether it's called once (classic [RAG](rag.md)) or agent-directed
- [Multi-Agent Systems](../agents/multi-agent-systems.md) — agentic RAG taken further, where retrieval/generation/critique are split across separate coordinating agents
