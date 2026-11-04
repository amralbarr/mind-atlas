# AI Agent Harness

## What is it?

An **agent harness** (also called **agentic harness**, or just **harness**) is the surrounding software that runs an [LLM](../generation/llm.md) in a loop and turns it from a text-in/text-out model into something that can actually take action. The model does the reasoning; the harness does everything else — it calls the model, executes the tool calls the model asks for, feeds results back in, manages context/memory across turns, enforces permissions and guardrails, and decides when the loop stops.

The relationship is usually summarized as:

```
Agent = Model + Harness
```

- **Model** — the [LLM](../generation/llm.md) itself (Claude, GPT, Llama, etc.). Takes text in, produces text out. No memory, no tools, no persistence on its own.
- **Harness** — the execution layer: calls the model, dispatches its tool calls to real systems (filesystem, shell, APIs, other models), returns results, tracks state across turns, and enforces what the model is and isn't allowed to do.
- **Agent** — the working system you actually interact with: model + harness together.

Without a harness, an [LLM](../generation/llm.md) can only produce a single text completion. It cannot read a file, run a command, remember what happened three turns ago, or be stopped mid-task by a permission check — all of that is harness responsibility.

## The tool-use loop

Concretely, a harness runs (a variant of) this loop:

```
1. Send conversation/context to the model
2. Model responds — either final text, or a request to call a tool
3. If it's a tool call:
     a. Harness validates the call against permissions/guardrails
     b. Harness executes the tool (file read, shell command, API call, subagent dispatch...)
     c. Harness feeds the tool's result back into the context
     d. Go to step 1
4. If it's final text: return it, loop ends (or waits for the next user turn)
```

This is often called the **ReAct loop** (reason → act → observe → repeat) in the research literature, but "harness" refers to the concrete piece of software implementing that loop for a given product, not the abstract pattern itself.

## What a harness actually manages

A harness is more than just the loop. In practice it owns:

| Responsibility | What it means |
|---|---|
| **Session/conversation loop** | Repeatedly calling the model and deciding when a turn/task is done |
| **Tool execution** | Parsing the model's tool-call request and actually running it against a real system |
| **Permissions & guardrails** | Deciding which tool calls are allowed to run without asking, which need approval, and which are blocked outright |
| **Context/state management** | Tracking conversation history, summarizing/compacting when the [context window](../generation/context-window.md) fills up, persisting state across turns or sessions |
| **Memory** | Longer-lived state beyond a single session (project files, prior decisions, user preferences) |
| **Observability** | Logging what the model decided, what ran, and why — needed to debug and audit agent behavior |
| **Wiring extensions** | Plugging in tools, skills, subagents, or plugins the model can invoke |

Because models across vendors have converged in raw capability, the quality of the harness — how well it manages context, permissions, and tool dispatch — increasingly determines how well an agent actually performs on real tasks, not just how good the underlying model is.

## Harness vs. scaffold vs. framework vs. agent

These terms get used loosely and overlap, but a reasonable way to separate them:

| Term | What it refers to |
|---|---|
| **Model** | The raw [LLM](../generation/llm.md) — text in, text out |
| **Scaffold** | The behavior-shaping layer: [system prompt](../generation/system-prompt.md), tool descriptions, how responses are parsed. Defines what the model perceives and is told to do. |
| **Harness** | The execution layer: calls the model, dispatches tool calls, decides when to stop, enforces permissions. Defines what the model is actually allowed and able to do. |
| **Agent** | Model + harness (+ scaffold) together — the complete working system |
| **Agent framework** | A reusable library/toolkit ([LangGraph](langgraph.md), [AutoGen](autogen.md), [CrewAI](crewai.md) — see [AI Orchestration Frameworks](../../../overviews/ai/orchestration-frameworks.md)) that gives you a harness (and often a scaffold) off the shelf, instead of building one yourself |

In short: [prompt engineering](../generation/prompt-engineering.md) shapes a single interaction, context engineering shapes what the model sees at a given moment, and harness engineering shapes the entire operational environment the model runs inside — it's the broadest of the three and contains the other two as parts.

## Concrete examples

- **Claude Code** — a harness for coding tasks: it runs the tool-use loop, executes file edits/shell commands/searches, enforces permission prompts before risky actions, manages context across a long session, and wires up subagents, plugins, and skills. Anthropic explicitly describes the underlying Claude Agent SDK as "a general-purpose agent harness adept at coding, as well as other tasks that require the model to use tools to gather context, plan, and execute."
- **[LangChain](langchain.md)'s `AgentExecutor`** — a lighter-weight harness: it repeatedly calls the model, parses tool-call output, executes the requested tool, and feeds the result back until the model returns a final answer.
- **AutoGPT-style loops** — early autonomous-agent harnesses that let a model plan, act, and re-plan against its own previous outputs with minimal human intervention, and were an early demonstration of how much a harness (not just a bigger model) determines whether an agent behaves usefully or spirals into unproductive loops.
- **A custom [RAG](../rag/rag.md)/agent backend** (e.g. the kind described in [Pipeline Orchestration](../infrastructure/pipeline-orchestration.md)) is also a harness in miniature once it starts deciding *when* to call the [LLM](../generation/llm.md) again, *which* tool/retriever to invoke, and *what* context to carry forward — even if nobody on the team calls it that.

## Why this term matters

"Harness" is useful specifically because it names the thing that has no equivalent without it: an [LLM](../generation/llm.md) API call by itself is stateless and toolless. Whenever a product claims to have "an AI agent," what actually distinguishes it from a chatbot wrapping a single API call is the harness underneath — the loop, the tool wiring, the permission model, and the state it carries across steps.

## Related

- [AI Orchestration Frameworks](../../../overviews/ai/orchestration-frameworks.md) — concrete frameworks ([LangGraph](langgraph.md), [AutoGen](autogen.md), [CrewAI](crewai.md)) that implement a harness for you
- [Pipeline Orchestration](../infrastructure/pipeline-orchestration.md) — the same "manage steps, state, and control flow" problem, applied to AI pipelines more broadly
- [Large Language Models (LLMs)](../generation/llm.md) — the model half of `Agent = Model + Harness`
- [Function / Tool Calling](tool-calling.md) — the mechanism the harness's tool-dispatch step is built on
- [Model Context Protocol (MCP)](model-context-protocol.md) — a standardized way to wire tools/data sources into a harness
- [Context Window](../generation/context-window.md) — what the harness's context/state management is working within
- [Multi-Agent Systems](multi-agent-systems.md) — what you get when multiple harness+model units coordinate on one task
