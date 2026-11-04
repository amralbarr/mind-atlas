# AI Orchestration Frameworks

A common design topic: there are a lot of framework names in this space, and the hard part isn't knowing them — it's knowing **when to use each one**. This page compares them and links to a dedicated note for each rather than describing them in full here.

## High-Level Categories

| Category | Tools |
|---|---|
| [LLM](../../concepts/ai/generation/llm.md) Applications | [LangChain](../../concepts/ai/agents/langchain.md), [LlamaIndex](../../concepts/ai/agents/llamaindex.md) |
| Agent Systems | [LangGraph](../../concepts/ai/agents/langgraph.md), [AutoGen](../../concepts/ai/agents/autogen.md), [CrewAI](../../concepts/ai/agents/crewai.md) |
| Workflow Orchestration | [Airflow](../../concepts/ai/infrastructure/airflow.md), [Prefect](../../concepts/ai/infrastructure/prefect.md) |
| Background Tasks | [Celery](../../concepts/distributed-systems/messaging/celery.md) |

## LangChain vs. LlamaIndex

| [LangChain](../../concepts/ai/agents/langchain.md) | [LlamaIndex](../../concepts/ai/agents/llamaindex.md) |
|---|---|
| General [LLM](../../concepts/ai/generation/llm.md) framework — chaining, tools, agents | Data/[RAG](../../concepts/ai/rag/rag.md) focused — ingestion, indexing, retrieval |
| Best for: [RAG](../../concepts/ai/rag/rag.md), [tool calling](../../concepts/ai/agents/tool-calling.md), agents, memory, chatbots | Best for: connecting [LLMs](../../concepts/ai/generation/llm.md) to large document/data sources |

## LangGraph vs. AutoGen vs. CrewAI

| Tool | Model | Best for |
|---|---|---|
| **[LangGraph](../../concepts/ai/agents/langgraph.md)** | Explicit graph of nodes/edges with shared state | Production agent workflows needing precise control over branching/loops |
| **[AutoGen](../../concepts/ai/agents/autogen.md)** | Open-ended agent-to-agent conversation, with automatic code execution | Research, dynamic problem-solving, collaborative debugging |
| **[CrewAI](../../concepts/ai/agents/crewai.md)** | Predefined roles and tasks handed off in sequence | Business-automation workflows with a known division of labor |

See [Multi-Agent Systems](../../concepts/ai/agents/multi-agent-systems.md) for the underlying concept (why/how work divides across agents) all three implement differently.

## Airflow vs. Prefect

| [Airflow](../../concepts/ai/infrastructure/airflow.md) | [Prefect](../../concepts/ai/infrastructure/prefect.md) |
|---|---|
| DAGs defined via a dedicated DSL/operators | Flows are plain Python functions (`@flow`/`@task`) |
| Large, mature operator ecosystem | Lighter-weight, more Python-native, less configuration |
| Best for: large/complex, multi-team pipeline estates | Best for: Python-heavy teams wanting less boilerplate |

Neither is a fit for real-time agentic decision-making — that's what the Agent Systems row above is for. [Celery](../../concepts/distributed-systems/messaging/celery.md) is a different layer again: ad-hoc background jobs (a queued task per request), not scheduled/dependency-ordered pipelines.

## Applied Example: an AI Platform Architecture

How these tools compose in a real product:

```text
User chat            → Frontend → NestJS → Python AI Service   (LangChain + LlamaIndex)
Multi-agent system    → Planner → Researcher → Coder → Reviewer (LangGraph)
OCR processing        → Upload PDF → OCR → Vectorize → Store    (Celery)
Nightly model training → Collect logs → Train → Deploy          (Airflow or Prefect)
```

## Current Industry Trend (2026)

For AI products, this stack appears frequently in AI Engineer, [LLM](../../concepts/ai/generation/llm.md) Engineer, and Agentic AI roles:

```text
FastAPI + LangChain + LlamaIndex + LangGraph + Redis + Celery + PostgreSQL
```

See [FastAPI](../../concepts/programming/python/fastapi.md) for the web framework underpinning most of these stacks.

## Related

- [LangChain](../../concepts/ai/agents/langchain.md)
- [LlamaIndex](../../concepts/ai/agents/llamaindex.md)
- [LangGraph](../../concepts/ai/agents/langgraph.md)
- [AutoGen](../../concepts/ai/agents/autogen.md)
- [CrewAI](../../concepts/ai/agents/crewai.md)
- [Airflow](../../concepts/ai/infrastructure/airflow.md)
- [Prefect](../../concepts/ai/infrastructure/prefect.md)
- [Celery](../../concepts/distributed-systems/messaging/celery.md)
- [AI Agent Harness](../../concepts/ai/agents/ai-agent-harness.md) — the execution loop and runtime these frameworks implement for you
- [Pipeline Orchestration](../../concepts/ai/infrastructure/pipeline-orchestration.md)
- [Retrieval-Augmented Generation (RAG)](../../concepts/ai/rag/rag.md)
- [Python for AI Engineering](../../concepts/ai/infrastructure/python-ai-engineering.md)
- [Multi-Agent Systems](../../concepts/ai/agents/multi-agent-systems.md)
- [Message Queues](../../concepts/distributed-systems/messaging/queues.md)
- [System Design](../../concepts/backend/architecture/system-design.md)
