# OWASP Top 10 for LLM Applications

The OWASP Top 10 for LLM Applications is a community-maintained checklist of the ten most critical security risks specific to applications built on [LLMs](../../ai/generation/llm.md) — first released in 2023, with a significantly revised 2025 edition reflecting real-world incidents, new attack techniques, and the growth of agentic systems. It's the [LLM](../../ai/generation/llm.md)-specific sibling of the long-standing general OWASP Top 10 for web applications, following the same format (a ranked, numbered list of risk categories, each with description, example attack scenarios, and mitigations) but scoped to what's actually new or different about building on top of a language model rather than a conventional web backend.

## The 2025 list

| ID | Risk | What it covers |
|---|---|---|
| **LLM01** | **[Prompt Injection](../attacks/prompt-injection.md)** | Attacker-controlled input overriding the application's intended instructions — the #1 risk for the second edition running |
| **LLM02** | **Sensitive Information Disclosure** | The model revealing PII, credentials, proprietary data, or other sensitive content through its output |
| **LLM03** | **Supply Chain** | Risk introduced by third-party models, [fine-tuning](../../ai/infrastructure/fine-tuning.md) datasets, plugins, or dependencies the application didn't build itself |
| **LLM04** | **Data and Model Poisoning** | Training, fine-tuning, or embedding data manipulated to introduce vulnerabilities, backdoors, or biases into the resulting model |
| **LLM05** | **Improper Output Handling** | Treating a model's output as safe-to-use without validation — e.g. passing it unsanitized into a shell command, a database query, or rendered HTML |
| **LLM06** | **Excessive Agency** | An LLM-based agent granted more permissions, tool access, or autonomy than its actual task requires, widening the blast radius of any single failure or successful attack |
| **LLM07** | **[System Prompt](../../ai/generation/system-prompt.md) Leakage** | Exposure of the internal system prompt — a new 2025 entry, since a leaked system prompt can reveal sensitive instructions, embedded credentials, or operational logic |
| **LLM08** | **Vector and Embedding Weaknesses** | Risks specific to [RAG](../../ai/rag/rag.md) architectures — a reminder that [RAG](../../ai/rag/rag.md) is a new attack surface (e.g. poisoned or unauthorized content entering the index), not an automatic safety mechanism |
| **LLM09** | **Misinformation** | The model confidently generating false content, a risk distinct from a direct security exploit but still named explicitly because of its real-world impact |
| **LLM10** | **Unbounded Consumption** | Uncontrolled resource usage — excessive token generation, unbounded loops in agentic workflows, or denial-of-service via resource exhaustion |

## LLM01: Prompt Injection, in full

[Prompt injection](../attacks/prompt-injection.md) keeps the top spot because it's the risk category this entire checklist is most directly downstream of — most of the other nine either enable a prompt injection attack, are a consequence of one succeeding, or compound its impact. This handbook covers the attack itself, its direct-vs-indirect distinction, and its full layered defense pipeline (delimiting content, upstream access-control filtering, constrained tool permissions, detection layers, output filtering) in its own dedicated note: see [Prompt Injection](../attacks/prompt-injection.md).

## How the other risks connect to defenses already covered elsewhere

Several of the other nine risks map directly onto mitigations and concepts already covered elsewhere in this handbook, rather than requiring entirely new tooling:

| OWASP risk | Related handbook coverage |
|---|---|
| LLM02 (Sensitive Information Disclosure) | The query-time [authorization](../authorization/authorization.md) filter and output filtering described in [Prompt Injection — Defenses](../attacks/prompt-injection.md#defenses-enforced-outside-the-model-not-inside-it) |
| LLM06 (Excessive Agency) | [Tool Calling](../../ai/agents/tool-calling.md)'s emphasis on the executing service independently validating and authorizing every proposed call, regardless of what the model requests |
| LLM07 (System Prompt Leakage) | The [system prompt](../../ai/generation/system-prompt.md) disclosure test case already included in [Prompt Injection — Adversarial test cases](../attacks/prompt-injection.md#adversarial-test-cases) |
| LLM08 (Vector and Embedding Weaknesses) | Metadata-filtering access control covered in [Vector Databases](../../ai/retrieval/vector-database.md#metadata-filtering), and the ingestion-time vs. query-time detection placement discussed in [Prompt Injection](../attacks/prompt-injection.md#where-to-place-a-detection-layer-ingestion-time-vs-query-time) |
| LLM09 (Misinformation) | The same groundedness/faithfulness evaluation this handbook already recommends via [RAGAS](../../ai/evaluation/ragas.md) and [Groundedness and Correctness](../../ai/evaluation/groundedness-and-correctness.md) |

This is a deliberate overlap, not duplication: OWASP names the risk category from a security-checklist perspective, while this handbook's own concept notes go deeper on the actual mechanism and defense for the ones most relevant to a [RAG](../../ai/rag/rag.md)/agentic system specifically.

## Where this fits next to NIST AI RMF

The [NIST AI RMF](nist-ai-rmf.md) and this checklist answer different questions at different altitudes: this list is the concrete, testable, security-engineering checklist a development team runs through before shipping (does each of these ten things have a mitigation, and has it been tested); the [NIST AI RMF](nist-ai-rmf.md) is the broader organizational governance process (who's accountable, what gets measured, how risk decisions get made and revisited) that this checklist's findings feed into. Citing both together in a technology recommendation's risk section — specific LLM-level vulnerabilities from this list, broader governance posture from [NIST AI RMF](nist-ai-rmf.md) — covers a wider and more credible slice of "have we actually thought about risk here" than either one alone.

## How it's used in practice

A team building or reviewing an LLM-powered application walks through all ten risk categories and, for each one, records: does this risk apply to our architecture, what's the current mitigation (if any), and has it actually been tested (e.g. via the kind of adversarial test cases described in [Prompt Injection — Adversarial test cases](../attacks/prompt-injection.md#adversarial-test-cases))? Treating this as a one-time checklist filled in before launch, rather than a living list re-reviewed whenever the architecture changes (a new tool is added, agentic autonomy increases, a new third-party model is integrated), is itself one of the more common practical failure modes — several of these risks (LLM03, LLM06) are specifically about *new* surface introduced by a later change, not just the system as originally shipped.

## Related

- [Prompt Injection](../attacks/prompt-injection.md) — the full treatment of LLM01, the risk category most of the other nine are downstream of
- [NIST AI RMF](nist-ai-rmf.md) — the complementary, organizational governance framework this checklist's findings feed into
- [Tool Calling](../../ai/agents/tool-calling.md) — where independent [authorization](../authorization/authorization.md) enforcement addresses LLM06 (Excessive Agency)
- [RAG](../../ai/rag/rag.md) — the architecture LLM08 (Vector and Embedding Weaknesses) is specifically about
- [RAGAS](../../ai/evaluation/ragas.md) — the evaluation discipline most directly relevant to catching LLM09 (Misinformation)
- [Lakera Guard](../attacks/lakera-guard.md) / [Azure Prompt Shields](../attacks/azure-prompt-shields.md) — concrete detection-layer products that mitigate several of these risk categories at once
