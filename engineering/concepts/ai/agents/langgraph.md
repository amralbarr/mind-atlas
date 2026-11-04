# LangGraph

LangGraph is a library (built by the [LangChain](langchain.md) team) for stateful, multi-step agent workflows — modeled explicitly as a graph of nodes and edges with shared state, giving deliberate control over branching, loops, and multi-agent handoffs that plain [LangChain](langchain.md) agents historically struggled to express reliably. See [AI Orchestration Frameworks](../../../overviews/ai/orchestration-frameworks.md) for how it compares to [AutoGen](autogen.md) and [CrewAI](crewai.md).

## Core Concepts

| Term | Meaning |
|---|---|
| **State** | A shared, typed object passed between every node in the graph — each node reads from and writes updates to it, rather than agents passing messages informally |
| **Node** | A single step in the workflow — usually a function or an [LLM](../generation/llm.md) call that takes the current state and returns an update |
| **Edge** | A connection from one node to the next; a **conditional edge** routes to different nodes based on the current state, enabling branching logic |
| **Graph** | The full workflow definition — nodes plus edges — compiled into an executable object |
| **Checkpointing** | LangGraph can persist state at each step, enabling pause/resume, human-in-the-loop approval steps, and replaying a run from a specific point |

## Defining a Simple Graph

```python
from langgraph.graph import StateGraph, END
from typing import TypedDict

class AgentState(TypedDict):
    query: str
    research: str
    draft: str

def research_node(state: AgentState) -> dict:
    state["research"] = f"Findings about: {state['query']}"
    return state

def writer_node(state: AgentState) -> dict:
    state["draft"] = f"Report based on: {state['research']}"
    return state

graph = StateGraph(AgentState)
graph.add_node("research", research_node)
graph.add_node("write", writer_node)
graph.set_entry_point("research")
graph.add_edge("research", "write")
graph.add_edge("write", END)

app = graph.compile()
result = app.invoke({"query": "Q3 budget trends"})
```

## Conditional Branching

```python
def route_after_review(state: AgentState) -> str:
    return "revise" if state.get("needs_revision") else "publish"

graph.add_conditional_edges("review", route_after_review, {
    "revise": "write",
    "publish": END,
})
```

This is what makes LangGraph suited to multi-step reasoning that plain [LangChain](langchain.md) chains (a fixed linear sequence) can't express — a review step can loop back to revision an arbitrary number of times based on runtime state, not a hardcoded chain length.

## Common Questions

**Why did LangGraph become popular instead of just using [LangChain](langchain.md)'s agent classes?**
> Plain [LangChain](langchain.md) agents made tool-calling decisions largely opaque and hard to constrain — LangGraph's explicit node/edge/state model gives a workflow author direct control over exactly which transitions are allowed, what state persists between steps, and where a human-approval checkpoint can be inserted, rather than trusting the agent's own judgment for control flow.

**Is LangGraph only for [multi-agent systems](multi-agent-systems.md)?**
> No — it's equally useful for a single agent that needs a non-trivial control flow (loops, conditional branches, retries with state), not just for coordinating multiple distinct agents. Multi-agent orchestration is one common use case, not the only one. See [Multi-Agent Systems](multi-agent-systems.md) for the underlying concept LangGraph, [AutoGen](autogen.md), and [CrewAI](crewai.md) each implement differently.

## Related

- [AI Orchestration Frameworks](../../../overviews/ai/orchestration-frameworks.md)
- [LangChain](langchain.md)
- [AutoGen](autogen.md)
- [CrewAI](crewai.md)
- [Multi-Agent Systems](multi-agent-systems.md)
- [AI Agent Harness](ai-agent-harness.md)
