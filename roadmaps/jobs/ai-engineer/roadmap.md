# Example: Senior AI Engineer / Agentic AI Architect Roadmap, Zero to Hero

A complete worked example of the [roadmap system](../../README.md), assembled from [modules/](../../modules/) for the job profile in [job-profile-ai-engineer.md](job-profile.md). Genericized — no company, no candidate-specific gap analysis, no single target language baked in. (The original job this was modeled on involved a specific target language with its own [NLP](../../../engineering/concepts/ai/nlp.md) quirks; swap in whichever language/dialect your own target role needs wherever this roadmap says "target language.")

## How to use this roadmap

- Total: ~54 weeks at 15–20 hours/week, zero prior AI experience to interview-ready.
- **Fast-track rule:** try each phase's milestone first; skip ahead if you can already build it unaided.
- **Build, don't just watch:** every phase's milestone extends the last. By the final phase they add up to one flagship knowledge-and-automation copilot (see Portfolio).
- **One tool per category:** go deep on one tool per category (e.g. one agent framework, one [vector database](../../../engineering/concepts/ai/retrieval/vector-database.md)) and know the alternatives by name, not by hands-on depth.
- **Weekly rhythm:** roughly 60% building, 30% studying, 10% writing notes.

## Phase 0 — [Programming Fundamentals](../../modules/foundations/programming-fundamentals.md) (weeks 1–3)

Goal: write clean code without looking up the basics. Milestone: see the module.

## Phase 1 — [Version Control & CLI](../../modules/foundations/version-control-and-cli.md) + [APIs & Backend Services](../../modules/backend/apis-and-services.md) (weeks 4–7)

Goal: ship a real authenticated backend API — the skeleton of the final copilot. Milestone: combine both modules' milestones into one authenticated, streaming, tested API service.

## Phase 2 — [Databases & Caching](../../modules/backend/databases-and-caching.md) + [Containers & CI/CD](../../modules/backend/containers-and-ci-cd.md) (weeks 8–9)

Goal: give the backend skeleton a real persistence layer, a cache, and a CI pipeline.

## Phase 3 — [System Design Fundamentals](../../modules/backend/system-design-fundamentals.md) (week 10)

Goal: be able to defend the architecture decisions made so far.

## Phase 4 — [Math for ML](../../modules/data-and-ml/math-for-ml.md) → [Classical Machine Learning](../../modules/data-and-ml/classical-machine-learning.md) → [Deep Learning Foundations](../../modules/data-and-ml/deep-learning-foundations.md) (weeks 11–18)

Goal: understand how models learn, with working code, not proofs. Milestone: a classical-ML model with a full pipeline, plus a small neural net trained from scratch.

## Phase 5 — [NLP & Transformer Architecture](../../modules/ai-llm/nlp-and-transformers.md) (weeks 19–20)

Goal: explain attention and transformer architecture from tokens to output.

## Phase 6 — [Prompt Engineering & LLM APIs](../../modules/ai-llm/prompt-engineering-and-llm-apis.md) (weeks 21–22)

Goal: get reliable, structured, cost-aware output from an [LLM](../../../engineering/concepts/ai/generation/llm.md) API. Milestone: a structured-extraction endpoint over free-text input in your target domain and language, with token/cost logging.

## Phase 7 — [Retrieval-Augmented Generation](../../modules/ai-llm/retrieval-augmented-generation.md) (weeks 23–28)

Goal: the core of the role — an enterprise knowledge assistant. Milestone: a hybrid-search, reranked, permissioned, cited knowledge assistant over real or realistic documents in your target domain.

## Phase 8 — [Agentic AI & Multi-Agent Systems](../../modules/ai-llm/agentic-ai-and-multi-agent-systems.md) (weeks 29–34)

Goal: agents that plan, call tools, and defer the risky step to a human. Milestone: a multi-agent workflow for one real decision in your target domain, with a human-approval gate and persisted state.

## Phase 9 — [LLM Evaluation, Guardrails & Observability](../../modules/ai-llm/llm-evaluation-and-guardrails.md) (weeks 35–38)

Goal: prove the system is accurate, safe, and affordable — with numbers. Milestone: an eval suite in CI, a guardrail against one real risk, and a cost/latency/quality dashboard.

## Phase 10 — [AI Research & Technology Benchmarking](../../modules/career/ai-research-and-benchmarking.md) (weeks 39–40)

Goal: the step up from AI builder to AI research/innovation engineer — evaluate technology choices with evidence instead of intuition. Milestone: a benchmark report comparing at least four retrieval configurations (BM25, dense, hybrid, hybrid+reranked) on your Phase 7 knowledge assistant's document set, against a hand-built ground-truth question set, with a stated recommendation and its limitations.

## Phase 11 — [LLM Deployment & Inference](../../modules/ai-llm/llm-deployment-and-inference.md) (weeks 41–46)

Goal: serve an open-weight model on your own infrastructure — valuable wherever on-prem/data-residency matters. Milestone: a benchmark report comparing full-precision vs quantized serving, then switch the copilot to the self-hosted model.

## Phase 12 — [MLOps & Cloud AI Platforms](../../modules/platform/mlops-and-cloud-ai-platforms.md) (weeks 47–50)

Goal: ship and operate the whole system repeatably. Milestone: the full copilot deployed via [CI/CD](../../../engineering/concepts/devops/ci-cd.md) with tests/evals gating every merge and a canary rollout.

## Phase 13 — [Domain Specialization](../../modules/career/domain-specialization.md) + [Security Fundamentals](../../modules/platform/security-fundamentals.md) (weeks 51–52, plus ~1 hr/week throughout)

Goal: talk like someone who has actually shipped AI inside a regulated organization. Fill in the domain-specialization module with your target industry's real vocabulary, use cases, and regulation (data-protection law, AI-governance framework, sector-specific security standard — whichever apply in your jurisdiction and industry). Map each control to a feature of the copilot (audit logs, PII masking, data residency, human approval).

## Phase 14 — [Soft Skills & Interview Prep](../../modules/career/soft-skills-and-interview-prep.md) (weeks 53–54)

Goal: interview-ready for [system design](../../../engineering/concepts/backend/architecture/system-design.md), coding, and behavioral rounds.

## Portfolio

See [modules/career/portfolio-and-certifications.md](../../modules/career/portfolio-and-certifications.md) for the general approach. For this roadmap specifically:

| Project | Built in | Requirement it proves |
| --- | --- | --- |
| Data-cleaning CLI | Phase 0 | Programming fundamentals |
| Authenticated streaming API | Phase 1–2 | Production-ready backend |
| Classical ML model + from-scratch neural net | Phase 4 | ML/DL understanding |
| Structured extraction endpoint | Phase 6 | Prompting, function calling, cost control |
| Knowledge assistant ([RAG](../../../engineering/concepts/ai/rag/rag.md)) | Phase 7 | Enterprise RAG |
| Multi-agent workflow | Phase 8 | Agentic AI / copilot |
| Eval suite + guardrails + dashboard | Phase 9 | Evaluation and observability |
| Retrieval benchmark report (BM25 vs dense vs hybrid vs reranked) | Phase 10 | Research methodology, evidence-based technology evaluation |
| Self-hosted inference benchmark | Phase 11 | Cost-optimized open-source deployment |
| CI/CD deployment to a container orchestrator | Phase 12 | Secure, scalable deployment |
| Domain + compliance mapping doc | Phase 13 | Architecture review, governance |

**Presenting it:** one repo, an architecture diagram in the README, a results table (quality metric, p95 latency, cost per 1,000 requests), a short demo. Use only public or synthetic data.

## Certifications

Pick certs matched to the job posting, always re-verified against the vendor's current catalog before committing time or money — AI/cloud vendors retire and rename certifications often. See [modules/career/portfolio-and-certifications.md](../../modules/career/portfolio-and-certifications.md).

## Sources

This example condenses the structure of a real multi-month roadmap built from a real (now-genericized) job posting. For sourcing specific courses/books/tools, see each module's own Resources section rather than this file — that keeps the example stable even as specific course offerings change over time.
