# LangChain

LangChain is a general-purpose framework for building [LLM](../generation/llm.md) applications — prompt templates, [tool calling](tool-calling.md), retrieval, memory, and agents, composed together instead of hand-wiring raw API calls to a model provider. See [AI Orchestration Frameworks](../../../overviews/ai/orchestration-frameworks.md) for how it compares to the other options in this space.

## Core Concepts

| Term | Meaning |
|---|---|
| **LCEL (LangChain Expression Language)** | The modern way to compose a chain — a declarative pipe syntax (`prompt \| model \| parser`) that replaced the older `LLMChain`/`SequentialChain` classes |
| **Chain** | A composed sequence of steps (prompt → model → output parsing → next step) executed via `.invoke()` |
| **Retriever** | An [abstraction](../../programming/fundamentals/abstraction.md) over a [vector database](../retrieval/vector-database.md) (or any lookup source) that returns relevant documents for a query — the retrieval half of [RAG](../rag/rag.md) |
| **Agent** | A loop where the model itself decides which tool to call and when, rather than following a fixed chain — see [AI Agent Harness](ai-agent-harness.md) for the general execution-loop concept this implements |
| **Memory** | State carried across turns in a conversation (chat history, summarized context) |

## Installation

```bash
pip install langchain langchain-openai langchain-core
```

## A Basic LCEL Chain

```python
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

llm = ChatOpenAI(model="gpt-4o-mini")
prompt = ChatPromptTemplate.from_template("Explain {topic} in one paragraph for a {audience}.")
parser = StrOutputParser()

chain = prompt | llm | parser

result = chain.invoke({"topic": "CI/CD", "audience": "junior developer"})
```

Each stage is a runnable that implements the same `.invoke()`/`.stream()`/`.batch()` interface — this uniformity is what lets arbitrarily different steps (a prompt, a model call, a retriever, a custom function) compose with the same `|` syntax.

## A Simple RAG Chain

```python
from langchain_core.runnables import RunnablePassthrough

retriever = vectorstore.as_retriever(search_kwargs={"k": 4})

rag_chain = (
    {"context": retriever, "question": RunnablePassthrough()}
    | prompt
    | llm
    | parser
)

answer = rag_chain.invoke("What was Q3 revenue?")
```

## Common Questions

**Is LangChain still relevant now that [LangGraph](langgraph.md) exists?**
> Yes, for a different layer — LangChain covers the building blocks (prompts, models, retrievers, LCEL chains), while [LangGraph](langgraph.md) is specifically for stateful, branching, multi-step agent workflows built *on top of* those same building blocks. A simple [RAG](../rag/rag.md) chatbot doesn't need [LangGraph](langgraph.md); a multi-agent workflow with retries and human-approval steps usually does.

**When is LangChain the wrong tool?**
> For complex multi-agent orchestration with explicit control over state and branching, or for pipeline scheduling (cron-like recurring jobs) — see [LangGraph](langgraph.md) and [Airflow](../infrastructure/airflow.md)/[Prefect](../infrastructure/prefect.md) respectively, which are purpose-built for those problems.

## Related

- [AI Orchestration Frameworks](../../../overviews/ai/orchestration-frameworks.md)
- [LlamaIndex](llamaindex.md)
- [LangGraph](langgraph.md)
- [Retrieval-Augmented Generation (RAG)](../rag/rag.md)
- [Tool / Function Calling](tool-calling.md)
- [Python for AI Engineering](../infrastructure/python-ai-engineering.md)
