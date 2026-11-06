# Module: LLM Evaluation, Guardrails & Observability

**Category:** AI / [LLM](../../../engineering/concepts/ai/generation/llm.md) · **Typical duration:** 4 weeks (15–20 hrs/week) · **Prerequisite modules:** [Retrieval-Augmented Generation](retrieval-augmented-generation.md) or [Prompt Engineering & LLM APIs](prompt-engineering-and-llm-apis.md)

## Goal

Prove an AI system is accurate, safe, and affordable with numbers — the question every serious stakeholder asks before trusting it with real users.

## Core topics

- [ ] Evaluation metrics: faithfulness/groundedness, answer relevancy, context precision/recall, hallucination rate
- [ ] Building a golden evaluation dataset (synthetic generation plus human review)
- [ ] [LLM](../../../engineering/concepts/ai/generation/llm.md)-as-a-judge: rubric design, bias, checking the judge against human labels
- [ ] Running evals in CI; blocking a merge on a quality regression
- [ ] Agent-specific metrics: task success rate, tool-call accuracy, steps per task, cost per task
- [ ] Guardrails: input rails ([prompt injection](../../../engineering/concepts/security/attacks/prompt-injection.md)/jailbreak detection), output rails (PII masking, content filtering)
- [ ] The [OWASP Top 10 for LLM Applications](../../../engineering/concepts/security/governance/owasp-top-10-llm.md), and mapping a control to each risk
- [ ] [NIST AI RMF](../../../engineering/concepts/security/governance/nist-ai-rmf.md) for the broader governance picture (trustworthiness, risk mitigation) when the role touches enterprise/regulated deployment — see [AI Research & Technology Benchmarking](../career/ai-research-and-benchmarking.md)
- [ ] Observability: tracing prompts/tool calls, cost and latency dashboards, replaying a bad production trace

## Resources

- An evaluation framework's official docs (e.g. a pytest-style LLM eval library, or a dedicated [RAG](../../../engineering/concepts/ai/rag/rag.md)-evaluation toolkit)
- A guardrails framework's docs for [input/output](../../../engineering/concepts/programming/fundamentals/io.md) validation
- An LLM observability/tracing tool's own quickstart

## Milestone deliverable

An automated eval suite (run in CI) covering your [RAG](../../../engineering/concepts/ai/rag/rag.md) or agent milestone project, plus a guardrail that blocks at least one real risk (e.g. PII leakage or [prompt injection](../../../engineering/concepts/security/attacks/prompt-injection.md)), plus a dashboard showing cost/latency/quality per request.

## Related concepts

[LLM Evaluation](../../../engineering/concepts/ai/evaluation/llm-evaluation.md), [Groundedness and Correctness](../../../engineering/concepts/ai/evaluation/groundedness-and-correctness.md), [RAGAS](../../../engineering/concepts/ai/evaluation/ragas.md), [Langfuse](../../../engineering/concepts/ai/evaluation/langfuse.md), Prompt Injection
