# Python Overview

For AI Engineer + Full Stack work, it's useful to organize Python knowledge into:

1. Documentation & learning sources
2. Web frameworks
3. [LLM](../../concepts/ai/generation/llm.md) frameworks & orchestration
4. Data science & AI libraries
5. Backend & infrastructure libraries
6. Must-know libraries

## Documentation & Learning Sources

The most important source is the [official Python documentation](https://docs.python.org/3/). For package installation and discovery, use [PyPI (Python Package Index)](https://pypi.org/) — the equivalent of npm for Node.js. A beginner-friendly alternative is the [W3Schools Python tutorial](https://www.w3schools.com/python/default.asp).

Most Python libraries publish documentation on their official docs site, their GitHub repository, and their PyPI page.

### Documentation Sites You'll Use Daily

- **Official Python:** [Python Documentation](https://docs.python.org/3/)
- **Package repository:** [PyPI](https://pypi.org/)
- **AI/ML:** [PyTorch Docs](https://pytorch.org/docs/stable/index.html), [Hugging Face Docs](https://huggingface.co/docs), [scikit-learn Docs](https://scikit-learn.org/stable/documentation.html)
- **[LLM](../../concepts/ai/generation/llm.md) frameworks:** [LangChain Docs](https://python.langchain.com/docs/introduction/), [LlamaIndex Docs](https://docs.llamaindex.ai/), [LangGraph Docs](https://langchain-ai.github.io/langgraph/)

## Python Web Frameworks

### FastAPI

The most important framework for AI startups today — async support, automatic [OpenAPI](../../concepts/backend/api/openapi.md) docs, type hints, high performance. Used heavily in AI APIs, [RAG](../../concepts/ai/rag/rag.md) systems, and [LLM](../../concepts/ai/generation/llm.md) services. See [FastAPI](../../concepts/programming/python/fastapi.md) for the dedicated note (installation, [dependency injection](../../concepts/programming/fundamentals/dependency-injection.md), streaming responses).

### Django

A full-stack framework including an [ORM](../../concepts/backend/data/orm.md), admin panel, [authentication](../../concepts/security/auth/authentication.md), and migrations. Good for enterprise systems and SaaS products.

### Flask

A minimal framework, good for prototypes, small APIs, and microservices.

### What AI Companies Use Most

Current trend for AI products and APIs: **[FastAPI](../../concepts/programming/python/fastapi.md) > [Flask](../../concepts/programming/python/flask.md) > [Django](../../concepts/programming/python/django.md)**.

## LLM Frameworks

These are relevant in 2026 — each has its own dedicated note; see [AI Orchestration Frameworks](../ai/orchestration-frameworks.md) for the full comparison of when to use each.

- **[LangChain](../../concepts/ai/agents/langchain.md)** — agents, tools, [RAG](../../concepts/ai/rag/rag.md), memory, workflows.
- **[LlamaIndex](../../concepts/ai/agents/llamaindex.md)** — focused on document ingestion, retrieval, and [RAG](../../concepts/ai/rag/rag.md) pipelines.
- **[LangGraph](../../concepts/ai/agents/langgraph.md)** — [multi-agent systems](../../concepts/ai/agents/multi-agent-systems.md), workflow graphs, stateful agents. Very popular now.
- **[AutoGen](../../concepts/ai/agents/autogen.md)** — agent-to-agent collaboration.
- **[CrewAI](../../concepts/ai/agents/crewai.md)** — role-based agent orchestration.

### Orchestration Frameworks

For complex AI workflows — see [AI Orchestration Frameworks](../ai/orchestration-frameworks.md):

| Framework | Purpose |
|---|---|
| [LangGraph](../../concepts/ai/agents/langgraph.md) | Agent workflows |
| [Apache Airflow](../../concepts/ai/infrastructure/airflow.md) | Data pipelines |
| [Prefect](../../concepts/ai/infrastructure/prefect.md) | Modern orchestration |
| [Celery](../../concepts/distributed-systems/messaging/celery.md) | Background jobs |

## LLM Ecosystem Libraries

- **OpenAI** — [OpenAI Platform Docs](https://platform.openai.com/docs)
- **Anthropic** — [Anthropic Docs](https://docs.anthropic.com/)
- **Google** — [Google AI Docs](https://ai.google.dev/)
- **Hugging Face** — ecosystem includes `transformers`, `datasets`, `tokenizers`, and inference tooling.

## Data Science Libraries

Must-know:

- **NumPy** — foundation of scientific computing. `import numpy as np`
- **Pandas** — DataFrames. `df.head()`
- **Matplotlib** — charts and graphs.
- **Seaborn** — statistical visualization.

## Machine Learning Libraries

- **PyTorch** — the most important framework today for AI engineering.
- **TensorFlow** — still used, though less dominant than PyTorch for modern [LLM](../../concepts/ai/generation/llm.md) work.
- **Scikit-learn** — classical machine learning.

## Computer Vision

- **OpenCV** — general-purpose computer vision.
- **Ultralytics** — [YOLO](../../concepts/ai/computer-vision/yolo.md) models.

## Database Libraries

- **[PostgreSQL](../../concepts/databases/relational/postgresql.md)** — `psycopg`
- **SQLAlchemy** — the most common [ORM](../../concepts/backend/data/orm.md).
- **Redis** — `redis-py`

## Async Libraries

- **[asyncio](../../concepts/backend/architecture/asyncio.md)** — Python's built-in async framework. See [asyncio](../../concepts/backend/architecture/asyncio.md) — the Python equivalent of the JS [event loop](../../concepts/programming/javascript/event-loop.md).
- **aiohttp** — async [HTTP](../../concepts/networking/http.md) client/server.
- **httpx** — a modern [HTTP](../../concepts/networking/http.md) client, very common with [FastAPI](../../concepts/programming/python/fastapi.md).

## Infrastructure Libraries

- **[Pydantic](../../concepts/programming/python/pydantic.md)** — extremely important, used by [FastAPI](../../concepts/programming/python/fastapi.md) for [data validation](../../concepts/programming/fundamentals/data-validation.md).
- **[Celery](../../concepts/distributed-systems/messaging/celery.md)** — background jobs.
- **Uvicorn** — the [ASGI](../../concepts/backend/architecture/asgi.md) server for [FastAPI](../../concepts/programming/python/fastapi.md).

## Preparing for AI Engineer Roles

Focus in this order:

**Python Core:** [OOP](../../concepts/programming/fundamentals/oop.md), [asyncio](../../concepts/backend/architecture/asyncio.md), generators, context managers, typing. See [OOP](../../concepts/programming/fundamentals/oop.md) for the core-language fundamentals.

**Backend:** [FastAPI](../../concepts/programming/python/fastapi.md), SQLAlchemy, [PostgreSQL](../../concepts/databases/relational/postgresql.md), Redis.

**AI:** PyTorch, Hugging Face, Transformers.

**[LLM](../../concepts/ai/generation/llm.md) Engineering:** [LangChain](../../concepts/ai/agents/langchain.md), [LlamaIndex](../../concepts/ai/agents/llamaindex.md), [LangGraph](../../concepts/ai/agents/langgraph.md), [RAG](../../concepts/ai/rag/rag.md), [vector databases](../../concepts/ai/retrieval/vector-database.md).

**Infrastructure:** [Docker](../../concepts/containers/docker.md), [Celery](../../concepts/distributed-systems/messaging/celery.md), [Kafka](../../concepts/distributed-systems/messaging/kafka.md), Redis.

For an AI Engineer + NestJS/Next.js Full Stack profile, the highest-ROI Python stack is:

```text
Python
FastAPI
Asyncio
Pydantic
SQLAlchemy
PostgreSQL
Redis
PyTorch
Transformers
LangChain
LangGraph
LlamaIndex
Docker
```

## Related

- [Python for AI Engineering](../../concepts/ai/infrastructure/python-ai-engineering.md)
- [asyncio](../../concepts/backend/architecture/asyncio.md)
- [OOP](../../concepts/programming/fundamentals/oop.md)
- [The Event Loop](../../concepts/programming/javascript/event-loop.md)
- [FastAPI](../../concepts/programming/python/fastapi.md)
- [AI Orchestration Frameworks](../ai/orchestration-frameworks.md)
- [Celery](../../concepts/distributed-systems/messaging/celery.md)
