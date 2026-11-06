# MTEB (Massive Text Embedding Benchmark)

MTEB is the standard public benchmark for comparing [embedding](../ingestion/embeddings.md) models against each other — instead of every team re-running its own ad hoc comparison of candidate models on a handful of in-house examples, MTEB runs a fixed, large battery of tasks across many languages and publishes a shared leaderboard so results are directly comparable model-to-model. It was introduced in a 2022 paper from Hugging Face and partners and has since become the default reference point anyone picking an embedding model for [RAG](../rag/rag.md), classification, or clustering checks first.

## What it actually measures

A single embedding model is rarely used for just one job — the same vectors might back semantic search, clustering, deduplication, or classification. MTEB reflects that by scoring every candidate model across 8 distinct task categories rather than one:

| Task category | What it tests |
|---|---|
| **Retrieval** | Given a query, find the relevant passage(s) in a corpus — the task closest to [RAG](../rag/rag.md)'s own retrieval step, and the category [BEIR](beir.md)'s datasets are folded into |
| **Semantic Textual Similarity (STS)** | Score how similar two sentences are in meaning, against human-labeled similarity scores |
| **Classification** | Use the embedding as a frozen feature vector fed into a simple classifier |
| **Clustering** | Group [embeddings](../ingestion/embeddings.md) into clusters and check how well the clusters match known categories |
| **Reranking** | Given a query and an initial candidate list, reorder it by embedding similarity — a [bi-encoder](../retrieval/bi-encoder.md)-only version of the problem [Cross-Encoder Re-Ranking](../retrieval/cross-encoder-reranking.md) solves with a slower, more accurate model |
| **Pair Classification** | Decide whether two texts are duplicates/paraphrases or not |
| **Summarization** | Score how well a generated summary's embedding matches a reference summary's embedding |
| **Bitext Mining** | Find matching sentence pairs across two languages — a cross-lingual retrieval task |

Altogether this spans 50+ datasets, and the benchmark has grown over time to cover 100+ languages plus multimodal (text+image) embedding tasks, not just English text.

## Why one leaderboard score isn't the whole answer

A model that leads the overall MTEB leaderboard is usually strong on average across all 8 categories and every included language — but "average across everything" can hide a model that's mediocre at the one category and language that actually matters for a specific deployment. A model optimized hard for English STS can still underperform a lower-ranked model on, say, Arabic retrieval specifically. The practical lesson, repeated throughout this handbook's evaluation notes (see [LLM Evaluation](llm-evaluation.md) on benchmark saturation and [RAGAS](ragas.md) on the limits of any single aggregate score): filter the public leaderboard down to the specific task category and language that matches the real use case, and — where the decision is high-stakes or the budget allows — validate the top few candidates against a real, representative sample of the actual target corpus rather than trusting the aggregate rank alone.

## MTEB vs. BEIR

MTEB is the broader, multi-task benchmark; [BEIR](beir.md) is a retrieval-only benchmark that predates MTEB and was folded in as MTEB's own Retrieval task category. A model's MTEB "Retrieval" score and its [BEIR](beir.md) score are drawing on largely the same underlying datasets — the difference is that MTEB also scores the same model on STS, clustering, classification, and the other six categories above, while [BEIR](beir.md) only ever cared about retrieval, and specifically about zero-shot transfer across the retrieval architectures it compares (sparse [BM25](../retrieval/bm25.md), dense, and reranked). Picking an embedding model for a [RAG](../rag/rag.md) pipeline specifically is really asking a retrieval question, so the MTEB Retrieval leaderboard and the [BEIR](beir.md) leaderboard are the two most directly relevant views — not the all-task aggregate score.

## How it's used in practice

```
Candidate shortlist: 3-5 embedding models
         │
         ▼
Filter MTEB leaderboard to: task = Retrieval, language = target language(s)
         │
         ▼
Shortlist narrows to models strong specifically on that slice
         │
         ▼
Validate top 1-2 candidates against the real corpus
(own Recall@k / Precision@k eval set, see Retrieval Metrics)
         │
         ▼
Final pick — balanced against vector dimensionality, cost, and latency,
not leaderboard rank alone
```

A higher-scoring model is also typically a larger, slower, and more expensive one to run at scale — MTEB's leaderboard does report embedding dimensionality and model size, which is worth weighing against the marginal accuracy gain before defaulting to the top-ranked entry for a production system with real latency/cost constraints.

## Related

- [BEIR](beir.md) — the retrieval-only, zero-shot benchmark whose datasets are folded into MTEB's own Retrieval task category
- [HELM](helm.md) — a comparable "don't trust one leaderboard number" multi-metric framework, but for full language models rather than embedding models
- [Embeddings](../ingestion/embeddings.md) — the thing MTEB is actually scoring
- [Retrieval Metrics](retrieval-metrics.md) — Recall@k/Precision@k, the same metric family used to validate a shortlisted model against a real corpus
- [Cross-Encoder Re-Ranking](../retrieval/cross-encoder-reranking.md) — MTEB's Reranking task category is a bi-encoder-only approximation of the same reordering problem
- [RAG](../rag/rag.md) — the system an embedding model chosen via MTEB usually ends up powering
- [LLM Evaluation](llm-evaluation.md) — the same benchmark-saturation caution ("a leaderboard score doesn't guarantee good performance on your actual task") applies here
