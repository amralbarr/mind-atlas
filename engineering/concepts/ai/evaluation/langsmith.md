# LangSmith

LangSmith is [LangChain](../agents/langchain.md)'s platform for tracing, testing, and monitoring [LLM](../generation/llm.md)/agent applications — it's a closed-source, [LangChain](../agents/langchain.md)-affiliated SaaS, in contrast with [Langfuse](langfuse.md)'s open-core, self-hostable-by-default model. It's framework-agnostic in practice: it can trace and evaluate apps built with [LangGraph](../agents/langgraph.md), [CrewAI](../agents/crewai.md), [Pydantic AI](../agents/pydantic-ai.md), or plain custom code via its SDK, not just [LangChain](../agents/langchain.md) itself. See [Langfuse vs. LangSmith](../../../overviews/ai/langfuse-vs-langsmith.md) for the full comparison.

## What it actually does

| Capability | What it covers |
|---|---|
| **Tracing** | Captures [LLM](../generation/llm.md) calls, chain executions, and retrieval steps as a nested trace tree, natively supporting [OpenTelemetry](../../backend/observability/opentelemetry.md) and the [OpenTelemetry](../../backend/observability/opentelemetry.md) GenAI semantic conventions |
| **Datasets & evaluation** | Stores example inputs/expected-outputs as [datasets](fixed-evaluation-dataset.md), and runs an evaluation harness that scores a candidate prompt/model/agent version against them — the same offline-regression pattern described in [LLM Evaluation](llm-evaluation.md) |
| **Production monitoring** | Dashboards over live traffic — cost, latency, error rate, feedback scores — with the ability to drill from an aggregate metric back down to the individual trace that produced it |
| **Framework integrations** | First-class support beyond [LangChain](../agents/langchain.md)/[LangGraph](../agents/langgraph.md): [AutoGen](../agents/autogen.md), [CrewAI](../agents/crewai.md), [Pydantic AI](../agents/pydantic-ai.md), OpenAI's Agents SDK, Microsoft's Agent Framework, and others, via its SDK or raw [OpenTelemetry](../../backend/observability/opentelemetry.md) |

## Basic usage

```bash
pip install langsmith
```

```python
import os
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = "..."

from langsmith import traceable

@traceable(name="answer_question", run_type="chain")
def answer_question(question: str) -> str:
    # any LLM call made inside this function (OpenAI SDK, LangChain, etc.)
    # is automatically captured as a nested run under this trace
    ...
```

The `@traceable` decorator mirrors [Langfuse](langfuse.md)'s `@observe()`: it wraps a function as a trace span, nesting whatever [LLM](../generation/llm.md)/tool calls happen inside it, without requiring the function's own logic to change. Because [LangChain](../agents/langchain.md) and [LangGraph](../agents/langgraph.md) already call into LangSmith's tracing internally, apps built on either one get full traces for free just by setting the two environment variables above — no decorator needed.

## Self-hosted vs. managed

LangSmith is managed-SaaS-first: a free Developer tier and a paid Plus tier cover most individual and small-team usage, usage-priced per trace ingested beyond an included allotment. Self-hosting (running the whole platform inside your own [Kubernetes](../../distributed-systems/kubernetes/ingress.md) cluster, so no trace data leaves your environment) is offered only at the Enterprise tier, which is the main practical reason teams with strict data-residency requirements pick [Langfuse](langfuse.md) instead.

## Where it fits in an LLM/agent workflow

LangSmith is typically wired in at the same point [Langfuse](langfuse.md) would be: enabled early via environment variables or the `@traceable` decorator so every call is traced from the start, then used for the same two ongoing jobs described in [LLM Evaluation](llm-evaluation.md) — pre-deployment regression testing against a [fixed evaluation dataset](fixed-evaluation-dataset.md), and live production monitoring once deployed. It's the natural default when a team is already standardized on [LangChain](../agents/langchain.md)/[LangGraph](../agents/langgraph.md), since tracing requires no additional instrumentation in that case.

## Related

- [Langfuse vs. LangSmith](../../../overviews/ai/langfuse-vs-langsmith.md) — full comparison with the open-source alternative
- [Langfuse](langfuse.md) — the closest competing platform
- [LangChain](../agents/langchain.md) / [LangGraph](../agents/langgraph.md) — the frameworks LangSmith traces with zero extra instrumentation
- [LLM Evaluation](llm-evaluation.md) — the evaluation methodology LangSmith's dataset/evaluation features implement
- [Fixed Evaluation Dataset](fixed-evaluation-dataset.md) — what LangSmith's dataset feature runs regression tests against
