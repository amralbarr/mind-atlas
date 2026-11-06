# Module: Prompt Engineering & LLM APIs

**Category:** AI / [LLM](../../../engineering/concepts/ai/generation/llm.md) · **Typical duration:** 2 weeks (15–20 hrs/week) · **Prerequisite modules:** [NLP & Transformer Architecture](nlp-and-transformers.md) (concepts) and [APIs & Backend Services](../backend/apis-and-services.md) (to wire a model into a real service)

## Goal

Get reliable, structured, cost-aware output from an LLM through its API — the day-to-day craft behind almost every AI feature.

## Core topics

- [ ] Zero-shot, few-shot, and structured prompting (clear roles, sectioned instructions)
- [ ] Reasoning techniques: chain-of-thought, self-consistency, ReAct
- [ ] System prompts, personas, output constraints
- [ ] Calling a model's API: streaming, error handling, retries
- [ ] Function/[tool calling](../../../engineering/concepts/ai/agents/tool-calling.md), [structured output / JSON mode](../../../engineering/concepts/ai/generation/structured-output.md), schema-validated responses
- [ ] Prompt caching and context-window management (trimming, summarizing history)
- [ ] Token counting, cost per request, and routing cheap vs strong models

## Resources

- Your chosen model provider's own prompt-engineering guide and API cookbook
- A schema-validation library for structured LLM output in your language

## Milestone deliverable

An API endpoint that extracts structured, validated fields from free-text input into [JSON](../../../engineering/concepts/programming/fundamentals/json.md), with token/cost logging per call and a documented comparison of two different prompts on a small test set.

## Related concepts

[Prompt Engineering](../../../engineering/concepts/ai/generation/prompt-engineering.md), [Structured Output](../../../engineering/concepts/ai/generation/structured-output.md), [Context Window](../../../engineering/concepts/ai/generation/context-window.md), [Sampling Parameters](../../../engineering/concepts/ai/generation/sampling-parameters.md)
