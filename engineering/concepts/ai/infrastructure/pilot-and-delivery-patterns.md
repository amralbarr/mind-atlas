# Pilot and Delivery Patterns

Concepts for scoping, sequencing, and reasoning about AI project delivery.

## Bounded Pilot

A first delivery scoped deliberately small — fixed users, fixed data, fixed feature set, clear acceptance criteria — to validate an approach and shared infrastructure before committing to full rollout.

**"Bounded" means:**
- Defined scope: one department, one document set, one query type
- Defined success: acceptance criteria agreed before work starts (e.g. Recall@5 ≥ 0.80, p95 latency < 3s)
- Defined end: you can declare it done, measure it, and decide whether to expand

**Why bounded matters:** an unbounded pilot grows indefinitely ("just one more use case") and never produces a measurable result. A bounded pilot produces evidence — which is what you bring to the stakeholder conversation about whether to proceed and how.

**What a good pilot validates:**
- The shared infrastructure (ingestion pipeline, embedding model, retrieval layer, evaluation harness, observability)
- That the data is actually available and usable
- That the acceptance criteria are the right ones
- That the team can deliver and operate this class of system

**Interview shape:**
> "I identify a bounded use case that can validate the shared components — the ingestion pipeline, retrieval layer, evaluation harness. I fix the scope and agree acceptance criteria before writing any code. The pilot produces evidence we use to decide whether and how to expand."

---

## Common Components

The shared infrastructure that multiple AI use cases will reuse — built once in a bounded pilot, then inherited by subsequent use cases.

**In a [RAG](../rag/rag.md) / AI platform:**

| Component | What it is | Validated by the pilot |
|---|---|---|
| Ingestion pipeline | Document parsing, chunking, embedding, storage | ✓ |
| Embedding model | Chosen model, dimensionality, language support | ✓ |
| Vector store | pgvector / [Azure AI Search](../../cloud/azure/azure-ai-search.md), index schema | ✓ |
| Retrieval layer | [Hybrid search](../retrieval/hybrid-search.md), re-ranking, permission filtering | ✓ |
| Evaluation harness | Fixed test set, Recall@k / groundedness measurement | ✓ |
| Observability stack | [OpenTelemetry](../../backend/observability/opentelemetry.md) traces, latency/error dashboards | ✓ |
| Auth / access control | [JWT](../../security/auth/jwt.md) validation, document-level permission enforcement | ✓ |

**The sequencing argument:** if the first use case builds these components well, the second use case only needs to add its own document set and acceptance criteria — the platform is already proven. If the first use case skips them ("we'll add observability later"), every subsequent use case inherits the same gaps.

**Interview shape:**
> "I look for a pilot that validates the common components — the shared infrastructure every future use case will rely on. Solving it once properly is faster than solving it five times badly."

---

## Trade-offs

A trade-off is a design decision where gaining something on one dimension costs something on another. Stating a trade-off well requires naming both sides and which you chose *and why* — "I chose X because of Y constraint, accepting Z cost."

**Why it matters in interviews:** the difference between a junior and senior engineer is not knowing more tools — it is being able to articulate *why* a choice was made given specific constraints, and what was given up.

**Common AI/[RAG](../rag/rag.md) trade-offs:**

| Decision | Option A | Option B | Typical reasoning |
|---|---|---|---|
| Retrieval approach | Vector-only (faster, simpler) | [Hybrid search](../retrieval/hybrid-search.md) (slower, better recall) | Hybrid if keyword matches matter (product names, IDs) |
| Chunk size | Small (precise retrieval) | Large (more context per chunk) | Small for dense fact retrieval; large for narrative/reasoning tasks |
| Auth pattern | Stateless [JWT](../../security/auth/jwt.md) (no DB call) | Stateful [API key](../../security/auth/api-key.md) (instant revocation) | [JWT](../../security/auth/jwt.md) for user sessions; [API key](../../security/auth/api-key.md) for third-party integrations |
| Inference | Self-hosted [vLLM](vllm.md) (control, cost) | Managed endpoint (simplicity, speed to market) | Self-hosted if data cannot leave the org or cost at scale matters |
| Access token TTL | Short (15 min, more secure) | Long (1 day, fewer re-auths) | Short + refresh token rotation is the correct answer for most cases |
| Evaluation timing | Build eval harness first | Build pipeline first, eval later | Eval harness first — without a baseline, you cannot measure improvement |
| Chunking strategy | Fixed character size (simple) | Structure-aware (headings/paragraphs) | Structure-aware almost always wins for document retrieval |

**How to state a trade-off in an interview:**
> "I chose [X] because [constraint or priority]. The cost was [Z], which we accepted because [reason — e.g. the system was internal, latency was more important than cost, the team had no [Kubernetes](../../distributed-systems/kubernetes/ingress.md) experience]."

**The bad answer:** "X is better than Y." — no constraint, no cost, no reasoning.
**The good answer:** "Given [constraint], X was the right call because [reason], accepting [cost]."

---

## Related

- [AI Use Case Prioritization](ai-use-case-prioritization.md)
- [LLM Evaluation](../evaluation/llm-evaluation.md)
- [Fixed Evaluation Dataset](../evaluation/fixed-evaluation-dataset.md)
- [Retrieval Metrics](../evaluation/retrieval-metrics.md)
- [Hybrid Search](../retrieval/hybrid-search.md)
- [RAG](../rag/rag.md)
