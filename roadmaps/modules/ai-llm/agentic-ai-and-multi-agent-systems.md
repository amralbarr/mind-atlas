# Module: Agentic AI & Multi-Agent Systems

**Category:** AI / [LLM](../../../engineering/concepts/ai/generation/llm.md) · **Typical duration:** 5–6 weeks (15–20 hrs/week) · **Prerequisite modules:** [Prompt Engineering & LLM APIs](prompt-engineering-and-llm-apis.md), [Retrieval-Augmented Generation](retrieval-augmented-generation.md)

## Goal

Design agents that plan, call tools, keep state, and hand risky steps to a human — and know when a fixed pipeline would have been the better (cheaper, more reliable) choice.

## Core topics

- [ ] The agent loop: observe, think, act; [tool calling](../../../engineering/concepts/ai/agents/tool-calling.md) with schemas
- [ ] Workflows vs autonomous agents — when a fixed pipeline beats an agent
- [ ] Build one agent with no framework first, so you understand what a framework is hiding
- [ ] An agent-orchestration framework in depth: state graphs, conditional routing, persistence/checkpointing, human-in-the-loop approval, memory (short-term vs long-term)
- [ ] Multi-agent patterns: supervisor, hierarchical teams, planner-executor, reflection/critic, parallel fan-out
- [ ] Failure handling: loop limits, timeouts, fallbacks
- [ ] A standard tool-exposure protocol for connecting an agent to external tools
- [ ] Production concerns: least-privilege tool permissions, sandboxing

## Resources

- Your chosen orchestration framework's own introductory course/docs
- A published essay on effective agent design from a major model provider
- Build the same small task in at least two different agent frameworks to compare patterns

## Milestone deliverable

A multi-agent system for one real task in your target domain, where a supervisor routes to at least two specialized sub-agents, a human approves the final high-stakes decision, and state persists across a restart.

## Related concepts

[Multi-Agent Systems](../../../engineering/concepts/ai/agents/multi-agent-systems.md), [LangGraph](../../../engineering/concepts/ai/agents/langgraph.md), Tool Calling, [Model Context Protocol](../../../engineering/concepts/ai/agents/model-context-protocol.md), [AI Agent Harness](../../../engineering/concepts/ai/agents/ai-agent-harness.md)
