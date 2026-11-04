# Embedding Model Selection: Local vs. API

Choosing an embedding model for a [RAG](../../concepts/ai/rag/rag.md) system — especially a multilingual one (e.g. Arabic/English, like an enterprise knowledge platform) — comes down to six axes: local vs. API deployment, language support quality, retrieval accuracy, memory footprint, operational simplicity, and cost/privacy. This page compares real current options on those axes rather than treating "which embedding model" as a single generic question.

## Local vs. API — the deployment decision first

| | Local / Self-hosted | Remote / API |
|---|---|---|
| **Model cost** | Usually free to download (check the license for commercial use) | Bundled into per-token usage price |
| **Infrastructure** | Needs a machine/server with enough RAM/VRAM | No dedicated embedding server needed |
| **Per-request cost** | No API fee; pay for compute/electricity instead | Billed per token processed |
| **Privacy** | Data can stay entirely inside your own infrastructure | Text is sent to a third-party provider — review retention/DPA terms |
| **Maintenance** | You own upgrades, scaling, uptime | Provider's responsibility |
| **Scaling under load** | Bounded by your own hardware and parallelism | Bounded by the provider's rate limits/plan |
| **Offline resilience** | Can keep running through an internet outage if fully self-hosted | Depends on connectivity and provider uptime |

Neither option is free — local trades a per-token bill for a hardware/ops bill. For sensitive internal documents (contracts, HR data, customer records), local deployment gives stronger data-residency guarantees, but it does **not** automatically guarantee privacy: you still have to secure logs, storage, backups, and access control yourself.

## Local multilingual embedding models

Run via `sentence-transformers`, `Ollama`, or similar — no [API key](../../concepts/security/auth/api-key.md), no per-call fee (verify each model's license for commercial use).

| Model | Language coverage | Size / dimensions | Max context | Best for |
|---|---|---|---|---|
| **BGE-M3** | Multilingual | 567M params, 1024-dim | 8K tokens | Arabic/English [RAG](../../concepts/ai/rag/rag.md) — supports dense, sparse, and multi-vector retrieval in one model |
| **Qwen3-Embedding-0.6B** | Multilingual | 0.6B | Varies by config | Lightweight option for testing multilingual semantic search |
| **Qwen3-Embedding-4B / 8B** | Multilingual | 4B / 8B | Varies by config | Higher-quality option when more compute is available |
| **multilingual-e5-large** | 94 languages | 1024-dim | 512 tokens | Strong multilingual retrieval; requires `query:` / `passage:` prefixes — easy to get wrong |
| **GTE-multilingual-base** | 70+ languages | 305M, 768-dim | 8K tokens | Good balance of model size and long-context support |
| **EmbeddingGemma 2** | 100+ languages | 270M (text) up to 740M (multimodal) | 8K tokens | Fully local; same model family can extend to image/audio/video |
| **Nomic Embed Text v2 (MoE)** | Multilingual | Mixture-of-experts | Varies | Worth benchmarking as a multilingual alternative to BGE-M3 |
| **Snowflake Arctic Embed 2** | Multilingual | ~568M | Varies | Multilingual search; validate Arabic quality on your own data |
| **nomic-embed-text** | English-first | ~274MB (Ollama package) | 2K tokens | Lightweight option for English-heavy corpora |
| **mxbai-embed-large** | English-first | ~335M | Varies | Local English semantic search |

Two caveats that matter in practice: the package size reported by a tool like Ollama is not the same as the RAM/VRAM needed at inference time, and a model card claiming "supports Arabic" does not guarantee good quality on Arabic dialects or on domain-specific terms like product/company names — that has to be measured on your own queries.

## API embedding models

No model weights to manage — send text, get vectors back, pay per token.

| Provider / model | Price per 1M input tokens | Cost for 10M tokens | Notes |
|---|---|---|---|
| OpenAI `text-embedding-3-small` | $0.02 | $0.20 | Cheapest reasonable baseline; see [Embeddings](../../concepts/ai/ingestion/embeddings.md) |
| OpenAI `text-embedding-3-large` | $0.13 | $1.30 | Larger, higher-accuracy OpenAI option, also used for non-English tasks |
| Voyage `voyage-4-lite` | $0.02 | $0.20 | Low-cost tier; Voyage has offered a free first-N-tokens allowance per account on some plans — check current terms |
| Voyage `voyage-4` | $0.06 | $0.60 | General-purpose multilingual embedding |
| Voyage `voyage-4-large` | $0.12 | $1.20 | Tuned for retrieval quality across languages |
| Cohere Embed | Varies by version/plan | Varies | Multilingual variants exist — confirm current pricing for the exact model version used |

Prices move; verify current rates on each provider's pricing page before committing, and remember this only covers the embedding step — re-indexing cost, the generation model's own token cost, and vector-database/storage cost are separate line items in a full [RAG](../../concepts/ai/rag/rag.md) budget.

## A simple cost intuition

- A ~400-word chunk ≈ 500 tokens.
- 100 documents × 3 chunks each = 300 chunks × 500 tokens = 150,000 tokens ≈ $0.003 at `text-embedding-3-small` pricing.
- At production scale (10M+ tokens for a large corpus, plus periodic re-indexing), the gap between the cheapest and most expensive API option can still be a few dollars per run — small compared to compute/engineering cost, but worth tracking if you re-embed frequently.

## How to actually decide (don't pick from the table alone)

1. Build a real evaluation set: 100–300 real questions in every language you support (e.g. Arabic + English), each paired with the correct source chunk.
2. Build one **separate index per candidate model** — never mix vectors from different embedding models in the same index.
3. Measure **Recall@5** and **[MRR](../../concepts/ai/evaluation/retrieval-metrics.md#mrr-mean-reciprocal-rank)** per model, plus end-to-end answer quality, latency, and memory footprint.
4. Factor in re-indexing cost and expected usage volume before picking the cheapest-looking option on paper.

## A reasonable starting shortlist

For a pgvector-backed, Arabic/English enterprise [RAG](../../concepts/ai/rag/rag.md) system:

- **BGE-M3** — strong local starting point for bilingual Arabic/English content, no per-call fee, supports hybrid (dense + sparse) retrieval out of the box — see [Hybrid Search](../../concepts/ai/retrieval/hybrid-search.md).
- **EmbeddingGemma 2** — lighter-weight local option, useful if hardware is constrained or if the roadmap includes multimodal (image/audio) retrieval later.
- **OpenAI `text-embedding-3-small`** — cheap, managed cloud baseline to benchmark local options against.

## Related

- [Embeddings](../../concepts/ai/ingestion/embeddings.md)
- [Hybrid Search](../../concepts/ai/retrieval/hybrid-search.md)
- [Vector Databases](../../concepts/ai/retrieval/vector-database.md)
- [Retrieval-Augmented Generation (RAG)](../../concepts/ai/rag/rag.md)
- [Chunking Strategies & Libraries](chunking-strategies.md)
- [Document Indexing Pipeline](../../concepts/ai/ingestion/document-indexing.md)
- [RAG & Grounding Interview Q&A](../../interview/interview-01/qa-rag.md)
