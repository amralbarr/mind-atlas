# Multi-Agent Systems

## What is it?

A multi-agent system is an architecture where multiple [LLM](../generation/llm.md)-driven agents — each with its own role, context, and often its own tools — coordinate to complete a task, instead of a single model/[harness](ai-agent-harness.md) trying to do everything in one continuous loop. Each agent is a full `Model + Harness` unit in its own right (see [AI Agent Harness](ai-agent-harness.md)); a multi-agent system is what you get when several of those units are wired together with a communication and control structure on top.

This is a distinct concept from the *frameworks* that implement it — [AI Orchestration Frameworks](../../../overviews/ai/orchestration-frameworks.md) surveys concrete tools ([LangGraph](langgraph.md), [AutoGen](autogen.md), [CrewAI](crewai.md)) for building multi-agent systems; this note is about the underlying idea of *why and how* work gets divided across agents in the first place, independent of which framework implements it.

## Why split work across multiple agents at all

A single agent with one long [system prompt](../generation/system-prompt.md) and one continuous context can, in principle, do a whole complex task itself. Multi-agent systems trade that simplicity for a few concrete benefits:

| Benefit | Why it helps |
|---|---|
| **Context isolation** | Each agent only carries the context relevant to its own subtask, instead of one shared [context window](../generation/context-window.md) bloating with everything from every stage — directly mitigates the [context window](../generation/context-window.md) limits of a single agent |
| **Role specialization** | A narrowly-scoped [system prompt](../generation/system-prompt.md) ("you are a code reviewer, only flag bugs") produces more focused, reliable behavior than one agent asked to plan, write, and review all at once |
| **Parallelism** | Independent subtasks (e.g. researching three different topics) can run concurrently across agents rather than sequentially in one context |
| **Modularity** | Each agent can be developed, prompted, and evaluated independently — swapping the "reviewer" agent's prompt doesn't require touching the "coder" agent's |
| **Failure containment** | One agent going off-track (bad tool call, confused reasoning) is easier to detect and recover from when its scope is narrow than when it's tangled into one giant context |

The trade-off is coordination overhead: agents need a way to hand off work, share results, and avoid working at cross-purposes — which is exactly what [orchestration frameworks](../../../overviews/ai/orchestration-frameworks.md) and control patterns exist to manage.

## Common coordination patterns

**Sequential / pipeline** — agents run one after another, each consuming the previous agent's output:
```
Planner Agent → Researcher Agent → Writer Agent → Reviewer Agent
```
Simple to reason about; each agent's role and handoff point are fixed and explicit.

**Hierarchical / orchestrator-worker** — a coordinating agent decides which specialized agent to invoke for each subtask and assembles the results, rather than a fixed linear chain:
```
              ┌── Research Agent
Orchestrator ─┼── Code Agent
              └── QA Agent
```
This scales better to tasks whose shape isn't known upfront — the orchestrator can decide dynamically which specialist is needed next.

**Peer-to-peer / conversational** — agents communicate directly with each other in a shared conversation, each contributing and reacting to what others said, rather than passing through a central coordinator:
```
Engineer Agent ↔ Reviewer Agent ↔ Manager Agent
```
Well suited to tasks that benefit from back-and-forth (a developer agent writes code, a reviewer critiques it, the developer revises) rather than a strict one-way handoff.

**Role-based teams** — each agent is assigned a fixed persona/responsibility up front (researcher, writer, analyst), similar to how a human team is structured, and the system routes subtasks to the agent whose role matches:
```
Research Agent → collects information
Writer Agent   → drafts the output
QA Agent       → validates the draft
```

These patterns aren't mutually exclusive — a hierarchical orchestrator might dispatch to agents that then have their own peer-to-peer conversation, for instance.

## What actually needs to be shared between agents

Coordinating multiple agents requires solving a few concrete problems regardless of pattern:

- **Shared state** — what one agent produces (a plan, a research result, a code diff) has to be made available to the next agent, usually by writing it into a shared store or passing it explicitly as that agent's input context.
- **Control flow** — deciding which agent runs next, when the overall task is done, and how to handle an agent that fails or produces unusable output.
- **Tool/permission boundaries** — agents often shouldn't share the same tool access; a research agent might need web search but not filesystem write access, while a code agent needs the opposite.

This is precisely the layer that frameworks like [LangGraph](langgraph.md) (explicit state graphs), [AutoGen](autogen.md) (conversational agent loops), and [CrewAI](crewai.md) (role-based crews) are built to handle — see [AI Orchestration Frameworks](../../../overviews/ai/orchestration-frameworks.md) for how each concretely implements these coordination patterns.

## When multi-agent is worth the complexity

Splitting into multiple agents adds real overhead — more moving parts, harder debugging (which agent introduced the error?), and more tokens spent on hand-offs between agents. It tends to pay off when a task naturally decomposes into distinct roles requiring different context/tools (research vs. writing vs. code vs. review), when a single agent's [context window](../generation/context-window.md) would otherwise get overloaded with unrelated concerns, or when subtasks are genuinely parallelizable. For tasks a single well-scoped agent handles reliably, adding more agents mostly adds complexity without adding capability.

## Related

- [AI Agent Harness](ai-agent-harness.md) — each agent in a multi-agent system is itself a Model + Harness unit
- [AI Orchestration Frameworks](../../../overviews/ai/orchestration-frameworks.md) — concrete frameworks ([LangGraph](langgraph.md), [AutoGen](autogen.md), [CrewAI](crewai.md)) that implement these coordination patterns
- [Context Window](../generation/context-window.md) — the per-agent limit that context isolation across agents helps work around
- [Function / Tool Calling](tool-calling.md) — the mechanism each agent uses to act, whether solo or as part of a multi-agent system
