# Module: Retrieval-Augmented Generation (RAG)

**Category:** AI / [LLM](../../../engineering/concepts/ai/generation/llm.md) · **Typical duration:** 4–5 weeks (15–20 hrs/week) · **Prerequisite modules:** [Prompt Engineering & LLM APIs](prompt-engineering-and-llm-apis.md), [Databases & Caching](../backend/databases-and-caching.md)

## Goal

Build a knowledge assistant that answers questions grounded in a real document set, with citations — the core skill behind most enterprise AI assistants.

## Core topics

- [ ] The [RAG](../../../engineering/concepts/ai/rag/rag.md) pipeline: load, chunk, embed, store, retrieve, generate, cite sources
- [ ] Document parsing for real-world formats (PDF, Word, HTML, tables)
- [ ] Chunking strategies: fixed-size, recursive, semantic, parent-child
- [ ] [Vector databases](../../../engineering/concepts/ai/retrieval/vector-database.md): index types ([HNSW](../../../engineering/concepts/ai/retrieval/hnsw.md)/IVF), distance metrics, metadata filtering, multi-tenancy
- [ ] [Hybrid search](../../../engineering/concepts/ai/retrieval/hybrid-search.md): sparse ([BM25](../../../engineering/concepts/ai/retrieval/bm25.md)) and dense retrieval, fused with [reciprocal rank fusion](../../../engineering/concepts/ai/retrieval/reciprocal-rank-fusion.md)
- [ ] Re-ranking with a [cross-encoder](../../../engineering/concepts/ai/retrieval/cross-encoder.md)
- [ ] Query rewriting, HyDE, multi-query, query decomposition
- [ ] Document-level permissions, incremental indexing, and versioning for a real multi-user system

## Resources

- A [RAG](../../../engineering/concepts/ai/rag/rag.md) framework's official tutorial — build the same pipeline in two frameworks to learn the pattern, not just one library's API
- Your chosen [vector database](../../../engineering/concepts/ai/retrieval/vector-database.md)'s own docs on index types and filtering
- [MTEB](../../../engineering/concepts/ai/evaluation/mteb.md)'s leaderboard, to benchmark a couple of embedding models on your own sample data — see [AI Research & Technology Benchmarking](../career/ai-research-and-benchmarking.md) for the full benchmarking methodology (MTEB, [BEIR](../../../engineering/concepts/ai/evaluation/beir.md), [HELM](../../../engineering/concepts/ai/evaluation/helm.md)) beyond just picking one model

## Milestone deliverable

A knowledge assistant with [hybrid search](../../../engineering/concepts/ai/retrieval/hybrid-search.md), a reranker, metadata filters, per-user permissions, and cited answers over a real (or realistic synthetic) document set.

## Related concepts

RAG, [Vector Database](../../../engineering/concepts/ai/retrieval/vector-database.md), Hybrid Search, [BM25](../../../engineering/concepts/ai/retrieval/bm25.md), [Reciprocal Rank Fusion](../../../engineering/concepts/ai/retrieval/reciprocal-rank-fusion.md), [Cross-Encoder Re-Ranking](../../../engineering/concepts/ai/retrieval/cross-encoder-reranking.md), [Embeddings](../../../engineering/concepts/ai/ingestion/embeddings.md), [Document Indexing](../../../engineering/concepts/ai/ingestion/document-indexing.md)
