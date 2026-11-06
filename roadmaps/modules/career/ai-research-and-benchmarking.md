# Module: AI Research & Technology Benchmarking

**Category:** Career (cross-cutting — the senior/architect-level skill layered on top of an AI builder's existing technical modules) · **Typical duration:** 2 weeks (15–20 hrs/week) · **Prerequisite modules:** [Retrieval-Augmented Generation](../ai-llm/retrieval-augmented-generation.md), [LLM Evaluation, Guardrails & Observability](../ai-llm/llm-evaluation-and-guardrails.md)

## Goal

This is the module that separates an AI builder from an AI research/innovation engineer: not learning to build another [RAG](../../../engineering/concepts/ai/rag/rag.md) pipeline or agent from scratch, but learning to decide — with evidence, not intuition — whether a new technique, model, or framework is actually worth adopting.

## Core topics

- [ ] The technology research cycle: identify a specific problem → research existing solutions (papers, open-source implementations, commercial options) → compare approaches → build a controlled proof of concept → evaluate across multiple dimensions → document a recommendation with stated limitations
- [ ] Reading a research paper systematically: abstract first, then methodology, experiments, and — critically — the limitations section, rather than reading linearly start to finish
- [ ] Tracking the field: a daily habit of skimming new papers and their open-source implementations, picking one problem to go deep on rather than reading everything shallowly
- [ ] Embedding and retrieval benchmarks: [MTEB](../../../engineering/concepts/ai/evaluation/mteb.md) (for choosing an embedding model across languages and task types) and [BEIR](../../../engineering/concepts/ai/evaluation/beir.md) (for comparing retrieval methods — sparse, dense, hybrid, reranked) — and their real limitation: a leaderboard-topping model doesn't necessarily win on your actual language, domain, latency, and cost constraints
- [ ] Holistic language-model benchmarking: how [HELM](../../../engineering/concepts/ai/evaluation/helm.md)'s multi-metric approach (accuracy, calibration, robustness, fairness, efficiency) differs from a single leaderboard number, and why multi-dimensional evaluation matters more than one headline score
- [ ] [LLM](../../../engineering/concepts/ai/generation/llm.md)-as-a-judge methodology: building a golden/[fixed evaluation dataset](../../../engineering/concepts/ai/evaluation/fixed-evaluation-dataset.md), writing a grading rubric, and validating the judge's verdicts against real human labels before trusting it
- [ ] Enterprise AI governance frameworks: [NIST AI RMF](../../../engineering/concepts/security/governance/nist-ai-rmf.md) (trustworthiness, evaluation and validation, risk mitigation, governance) and the [OWASP Top 10 for LLM Applications](../../../engineering/concepts/security/governance/owasp-top-10-llm.md) — both belong in a technology recommendation's risk section, not treated as separate paperwork
- [ ] Writing the recommendation itself: what you compared, on what dataset, under what conditions, what it cost, where it fails, and a clear adopt/improve/reject call

## Resources

- NIST AI RMF's Generative AI Profile, for the governance half of a real enterprise recommendation
- The OWASP Top 10 for LLM Applications, read in full at least once
- The original MTEB and BEIR papers, not just their leaderboard pages
- [HELM](../../../engineering/concepts/ai/evaluation/helm.md)'s own documentation for how it structures a multi-metric benchmark
- A paper-aggregator site that links each paper to its open-source implementation, so you default to "read it, then try to reproduce one experiment" instead of "read it and move on"

## Milestone deliverable

A benchmark report comparing at least four retrieval configurations (sparse/[BM25](../../../engineering/concepts/ai/retrieval/bm25.md)-style, dense, hybrid, hybrid plus reranking) on one real or realistic bilingual document set, against a hand-built ground-truth question set (direct questions, multi-document questions, questions with no answer in the corpus, questions with conflicting information). Report [retrieval metrics](../../../engineering/concepts/ai/evaluation/retrieval-metrics.md) per configuration, plus latency and cost, plus a written recommendation stating which configuration you'd actually ship and why — this directly extends the [Retrieval-Augmented Generation](../ai-llm/retrieval-augmented-generation.md) module's own milestone rather than starting a new project from zero.

## Related concepts

[RAGAS](../../../engineering/concepts/ai/evaluation/ragas.md), Retrieval Metrics, Fixed Evaluation Dataset, [Hybrid Search](../../../engineering/concepts/ai/retrieval/hybrid-search.md), [Cross-Encoder Re-Ranking](../../../engineering/concepts/ai/retrieval/cross-encoder-reranking.md)
