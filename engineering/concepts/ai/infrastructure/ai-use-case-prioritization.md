# AI Use Case Prioritization

A five-criterion framework for comparing and sequencing multiple AI use cases running in parallel. Used when a team or stakeholder has several AI initiatives competing for capacity and must decide what to build first.

## The Five Criteria

| Criterion | The question it asks |
|---|---|
| **Business Value** | How much time or money will this save, or how significantly will it improve the customer experience? |
| **Data Readiness** | Is the required data available, clean, and accessible — and do we have permission to use it? |
| **Risk** | What happens if the model is wrong? Is there sensitive data involved, or a legal/regulatory implication? |
| **Integration Effort** | How many systems must be connected? Are the teams that own them cooperative and available? |
| **Measurable Acceptance Criteria** | How will we know the project succeeded? Are there clear, agreed numbers before we start? |

## Applying the Framework

Score each candidate use case against all five criteria before committing capacity. The goal is not a formula — it is a structured conversation that surfaces hidden assumptions before work starts.

**Business Value** — avoid vague claims ("this will save a lot of time"). Push for a concrete estimate: number of hours per week, cost of the current manual process, error rate of the existing approach. An AI use case with modest but certain value often beats a transformative one that depends on assumptions no one has validated.

**Data Readiness** — the most common project failure mode in enterprise AI. Questions to ask: Does the data exist in a queryable system, or only in PDFs and emails? How clean is it — has anyone looked at a sample? Who owns it, and how long will access approval take? If data readiness is low, the project will stall regardless of how high its business value scores.

**Risk** — consider two dimensions: (1) consequence of a wrong answer (low-stakes: a recommendation the user ignores; high-stakes: a medical or financial decision), and (2) data sensitivity (PII, confidential documents, regulated data). High risk does not mean do not proceed — it means plan for evaluation, human review, and audit trails before launch.

**Integration Effort** — an AI feature is only as fast to deliver as its slowest upstream dependency. A use case that requires connecting to three legacy systems owned by teams with no bandwidth is effectively blocked, regardless of its value. Map dependencies and team availability before scoring this criterion.

**Measurable Acceptance Criteria** — the discipline that separates a successful AI project from a demo. Define before you build: what metric, measured how, on what data, constitutes success? Without this, you ship when you run out of time, not when the system works. Examples: Recall@5 ≥ 0.80 on the evaluation set; abstention rate < 10% on in-scope queries; latency p95 < 3 seconds under 50 concurrent users.

## Sequencing Decision

After scoring, look for the use case that:
1. Has the highest business value with the lowest risk
2. Has data that is already accessible
3. Can validate shared components (embedding pipeline, retrieval layer, evaluation harness) that future use cases will reuse — a "pilot" that builds the platform, not just one feature

Defer use cases where data access is blocked or acceptance criteria cannot be agreed — starting without these locks in scope creep and delivers a demo, not a production system.

## Interview Answer Shape

> "I compare business value, data readiness, risk, integration effort, and measurable acceptance criteria. I look for a use case that scores well across all five — not just high business value — because a project with great potential but blocked data or undefined success criteria will stall. I also look for a pilot that validates shared components so the first delivery builds a platform the next use cases can reuse. I make dependencies and capacity visible upfront, agree acceptance criteria with stakeholders before writing any code, and avoid committing to production dates before data access and quality are understood."

## Related
- [Pilot and Delivery Patterns](pilot-and-delivery-patterns.md) — bounded pilot, common components, and how to state trade-offs
- [Governed Data](../../cloud/data/governed-data.md) — what "Data Readiness" means in practice: quality, lineage, access control, auditability
- [LLM Evaluation](../evaluation/llm-evaluation.md)
- [Fixed Evaluation Dataset](../evaluation/fixed-evaluation-dataset.md)
- [Retrieval Metrics](../evaluation/retrieval-metrics.md)
- [RAG](../rag/rag.md)
