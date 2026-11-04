# Langfuse vs. LangSmith

Both are [LLM](../../concepts/ai/generation/llm.md)/agent observability platforms covering the same three jobs — tracing, prompt management, and evaluation against datasets — for roughly the same use case: knowing what a production [LLM](../../concepts/ai/generation/llm.md)/agent pipeline actually did, and whether a prompt or model change made it better or worse. The difference that actually drives the choice between them is openness and hosting model, not feature coverage.

## The comparison

| | [Langfuse](../../concepts/ai/evaluation/langfuse.md) | [LangSmith](../../concepts/ai/evaluation/langsmith.md) |
|---|---|---|
| **License / core** | Open-source (MIT core) | Closed-source SaaS |
| **Self-hosting** | Fully supported, first-class — [Docker Compose](../../concepts/containers/docker-compose.md) or [Kubernetes](../../concepts/distributed-systems/kubernetes/ingress.md), at any tier | Enterprise-tier only; free/Plus tiers are cloud-only |
| **Affiliation** | Independent, framework-agnostic from the start | Built by the [LangChain](../../concepts/ai/agents/langchain.md) team, tightest integration with [LangChain](../../concepts/ai/agents/langchain.md)/[LangGraph](../../concepts/ai/agents/langgraph.md) |
| **Tracing decorator** | `@observe()` | `@traceable` |
| **Zero-instrumentation tracing** | Via drop-in SDK wrappers (e.g. `langfuse.openai`) | Automatic for apps already built on [LangChain](../../concepts/ai/agents/langchain.md)/[LangGraph](../../concepts/ai/agents/langgraph.md) — tracing is already wired into those libraries internally |
| **Evaluation** | [LLM-as-judge](../../concepts/ai/evaluation/llm-evaluation.md), code evaluators, human feedback, against [datasets](../../concepts/ai/evaluation/fixed-evaluation-dataset.md) | Same shape — dataset-based evaluation harness, [LLM-as-judge](../../concepts/ai/evaluation/llm-evaluation.md) and custom evaluators |
| **Pricing shape** | Free if self-hosted; usage-priced on Cloud | Free/Plus tiers usage-priced per trace ingested beyond an included allotment; Enterprise adds self-hosting |
| **Data residency** | Full control if self-hosted | Only guaranteed if on the Enterprise self-hosted tier |

## How to actually choose

The decision collapses to two questions:

1. **Does data have to stay inside your own infrastructure?** If yes (regulatory, contractual, or just cost-at-scale reasons), [Langfuse](../../concepts/ai/evaluation/langfuse.md)'s first-class self-hosting at every tier is the deciding factor — getting the same guarantee from [LangSmith](../../concepts/ai/evaluation/langsmith.md) means committing to its Enterprise tier.
2. **Is the stack already built on [LangChain](../../concepts/ai/agents/langchain.md)/[LangGraph](../../concepts/ai/agents/langgraph.md)?** If so, [LangSmith](../../concepts/ai/evaluation/langsmith.md) requires no additional instrumentation at all — tracing is already flowing through those libraries. A framework-agnostic stack (raw SDK calls, [CrewAI](../../concepts/ai/agents/crewai.md), [Pydantic AI](../../concepts/ai/agents/pydantic-ai.md)) doesn't get that advantage from either tool, since both ship comparable integrations for non-[LangChain](../../concepts/ai/agents/langchain.md) frameworks.

Outside of those two factors, the two platforms solve the same problem with near-identical feature sets — picking either one and wiring it in early is far more valuable than optimizing the choice between them.

## Related

- [Langfuse](../../concepts/ai/evaluation/langfuse.md) — the open-source, self-hostable-first platform
- [LangSmith](../../concepts/ai/evaluation/langsmith.md) — the [LangChain](../../concepts/ai/agents/langchain.md)-affiliated managed platform
- [LLM Evaluation](../../concepts/ai/evaluation/llm-evaluation.md) — the evaluation methodology both platforms implement
- [RAGAS](../../concepts/ai/evaluation/ragas.md) — a metrics library that can run as an evaluator inside either platform
- [LangChain](../../concepts/ai/agents/langchain.md) / [LangGraph](../../concepts/ai/agents/langgraph.md) — the frameworks [LangSmith](../../concepts/ai/evaluation/langsmith.md) integrates with most tightly
