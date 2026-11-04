# Pydantic AI

Pydantic AI is an open-source Python agent framework, built by the team behind [Pydantic](../../programming/python/pydantic.md) (the most-downloaded Python [data validation](../../programming/fundamentals/data-validation.md) library), for building production-grade [LLM](../generation/llm.md) applications with the same "type-safety first" philosophy [Pydantic](../../programming/python/pydantic.md) brought to web APIs. Its pitch is: [FastAPI](../../programming/python/fastapi.md) made building APIs feel obvious by leaning on Python type hints and [Pydantic](../../programming/python/pydantic.md) validation — Pydantic AI tries to do the same for agent development.

## When to Use Pydantic AI

| Good fit | Poor fit |
|---|---|
| Production agents that must return validated, typed data | Quick throwaway scripts with no structure needs |
| Teams already using [FastAPI](../../programming/python/fastapi.md) + [Pydantic](../../programming/python/pydantic.md) (shared mental model) | Heavy multi-agent graph orchestration ([LangGraph](langgraph.md) fits better) |
| Swapping model providers without rewriting agent logic | Projects needing a huge pre-built tool/integration ecosystem ([LangChain](langchain.md) has more) |
| Unit-testing agent logic without burning API calls (`TestModel`) | |

## Core Concepts

| Term | Meaning |
|---|---|
| **`Agent`** | The core orchestrator — wraps a model, a [system prompt](../generation/system-prompt.md)/instructions, tools, and an expected output type |
| **`RunContext`** | A typed context object passed into tools and dynamic instructions, carrying injected dependencies |
| **[Dependency injection](../../programming/fundamentals/dependency-injection.md) (`deps_type`)** | Pass runtime objects (DB connections, API clients, the current user) into an agent without global state, fully typed |
| **Tools (`@agent.tool`)** | Python functions the model can call; the function's type hints and docstring become the schema and description the model sees |
| **`output_type`** | A [Pydantic](../../programming/python/pydantic.md) `BaseModel` (or other type) the final agent output is validated against — no manual [JSON](../../programming/fundamentals/json.md) parsing |
| **`TestModel`** | A built-in fake model that runs agents offline, with no real [LLM](../generation/llm.md) call — used for unit tests |
| **Model-agnostic** | One agent definition can target OpenAI, Anthropic, Google, Bedrock, [Azure AI Foundry](../../cloud/azure/azure-ai-foundry.md), Groq, Mistral, xAI, Ollama, and others by swapping a model string |

## Installation

```bash
pip install pydantic-ai
# or, in a uv-managed project:
uv add pydantic-ai
```

## Quick Start

```python
from pydantic import BaseModel
from pydantic_ai import Agent, RunContext

class SupportOutput(BaseModel):
    advice: str
    needs_escalation: bool

class Deps:
    def __init__(self, customer_id: int):
        self.customer_id = customer_id

agent = Agent(
    "openai:gpt-4o",
    deps_type=Deps,
    output_type=SupportOutput,
    instructions="You are a helpful banking support agent.",
)

@agent.tool
async def get_balance(ctx: RunContext[Deps]) -> float:
    """Return the customer's current account balance."""
    return await fetch_balance_from_db(ctx.deps.customer_id)

result = await agent.run(
    "What's my balance, and should I be worried about it?",
    deps=Deps(customer_id=123),
)
print(result.output.advice)          # typed, validated SupportOutput
print(result.output.needs_escalation)
```

The model never sees `Deps` directly — the harness passes it through `RunContext` so tools can use it (a DB session, an authenticated client, feature flags) without reaching for globals, mirroring how [FastAPI](../../programming/python/fastapi.md)'s [dependency injection](../../programming/fundamentals/dependency-injection.md) keeps route handlers testable.

## Structured Output

Because `output_type` is a normal [Pydantic](../../programming/python/pydantic.md) model, invalid or incomplete model responses are caught and retried automatically rather than surfacing as a raw [JSON](../../programming/fundamentals/json.md)-parsing exception in application code — see [Structured Output](../generation/structured-output.md) for the general mechanism this relies on.

## Streaming

```python
async with agent.run_stream("Summarize this in one sentence.") as response:
    async for chunk in response.stream_text():
        print(chunk, end="", flush=True)
```

Streamed output is typically pushed to a client over [Server-Sent Events](../../protocols/sse.md) in a [FastAPI](../../programming/python/fastapi.md) backend, since both are async-native and pair naturally.

## Testing Without Calling a Real LLM

```python
from pydantic_ai.models.test import TestModel

def test_support_agent():
    with agent.override(model=TestModel()):
        result = agent.run_sync("What's my balance?", deps=Deps(customer_id=1))
        assert isinstance(result.output, SupportOutput)
```

`TestModel` fabricates plausible tool calls and outputs against the agent's schema, so tests run offline, deterministically, and without API cost.

## Pydantic AI vs Other Agent Frameworks

| | Pydantic AI | [LangChain](langchain.md) | [LangGraph](langgraph.md) |
|---|---|---|---|
| Core value prop | Type-safe agents, [Pydantic](../../programming/python/pydantic.md)-native validation | Broadest tool/integration ecosystem | Stateful multi-agent graphs |
| Output validation | Built-in (`output_type` = [Pydantic](../../programming/python/pydantic.md) model) | Manual / output parsers | Manual |
| [Dependency injection](../../programming/fundamentals/dependency-injection.md) | Built-in (`RunContext`) | Not a first-class concept | Not a first-class concept |
| Best for | Production services with strict [I/O](../../programming/fundamentals/io.md) contracts | Rapid prototyping, wide integrations | Complex multi-step/multi-agent workflows |

See [AI Orchestration Frameworks](../../../overviews/ai/orchestration-frameworks.md) for where [LangChain](langchain.md)/[LangGraph](langgraph.md)/[AutoGen](autogen.md)/[CrewAI](crewai.md) each fit.

## Related Concepts

- [Function / Tool Calling](tool-calling.md) — the underlying mechanism `@agent.tool` builds on
- [Structured Output / JSON Mode](../generation/structured-output.md) — what `output_type` validation relies on
- [AI Agent Harness](ai-agent-harness.md) — the loop `Agent.run()` implements under the hood
- [AI Orchestration Frameworks](../../../overviews/ai/orchestration-frameworks.md) — how Pydantic AI compares to [LangChain](langchain.md)/[LangGraph](langgraph.md)/[CrewAI](crewai.md)
- [Agentic RAG](../rag/agentic-rag.md) — a common pattern built on top of an agent framework like this one
- [ASGI](../../backend/architecture/asgi.md) — the async runtime Pydantic AI's `async`/`await` API is built to run inside (e.g. under [FastAPI](../../programming/python/fastapi.md))
