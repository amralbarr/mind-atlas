# BEIR (Benchmarking-IR)

BEIR is a standard benchmark for comparing information-retrieval methods under **zero-shot** conditions — a retriever is scored on datasets and domains it was never trained or fine-tuned on, rather than on a held-out split of the same data it was trained against. It was introduced in a 2021 paper and packaged as an open-source Python evaluation toolkit, and it answers a specific, practical question: does a retrieval method that does well on the dataset it was built for still do well on a different domain it's never seen — the situation almost every real deployment is actually in, since the production corpus is rarely identical to whatever dataset the retriever was originally tuned on.

## What it's made of

BEIR combines 18 publicly available retrieval datasets spanning diverse domains and task types — question answering, fact-checking, duplicate-question detection, entity retrieval, citation prediction, and more — rather than one dataset from one domain. Each dataset supplies a corpus, a set of queries, and relevance judgments, the same ingredients [Retrieval Metrics](retrieval-metrics.md)'s Recall@k/Precision@k scoring needs, just standardized and pre-packaged across many different corpora at once instead of one team building its own evaluation set from scratch.

## What it compares

BEIR evaluates the same retrieval architectures teams actually have to choose between in production, scored zero-shot across all 18 datasets rather than just one:

| Architecture | What it is | How it did on BEIR |
|---|---|---|
| **Lexical ([BM25](../retrieval/bm25.md))** | Token-matching, [TF-IDF](../retrieval/tf-idf.md)-weighted sparse scoring | A surprisingly strong, consistent baseline — dense models frequently failed to beat it zero-shot |
| **Sparse neural (e.g. docT5query)** | Document-expansion methods that add predicted query terms to documents before indexing, then score lexically | Outperformed plain [BM25](../retrieval/bm25.md) on roughly 11 of the 18 datasets |
| **Dense ([bi-encoder](../retrieval/bi-encoder.md) [embeddings](../ingestion/embeddings.md))** | Query and document separately embedded, compared by vector similarity — see [Bi-Encoder](../retrieval/bi-encoder.md) | Inconsistent zero-shot performance — often strong on domains resembling its training data, but degraded sharply under larger domain shift |
| **Re-ranked ([BM25](../retrieval/bm25.md) + [cross-encoder](../retrieval/cross-encoder.md))** | [BM25](../retrieval/bm25.md) retrieves a candidate set, a [cross-encoder](../retrieval/cross-encoder.md) re-scores it — see [Cross-Encoder Re-Ranking](../retrieval/cross-encoder-reranking.md) | The best overall zero-shot generalizer — beat plain [BM25](../retrieval/bm25.md) on 16 of the 18 datasets |

## The headline finding, and why it matters

BEIR's most cited result is that dense embedding retrievers — the component most [RAG](../rag/rag.md) systems default to — are not reliably better than decades-old [BM25](../retrieval/bm25.md) once the evaluation corpus is genuinely different from what the dense model was trained on. This is the empirical backing behind a recurring piece of advice elsewhere in this handbook: [hybrid search](../retrieval/hybrid-search.md) (combining lexical and dense scoring, see [BM25 vs Hybrid Search vs RRF](../../../overviews/ai/bm25-vs-hybrid-search-vs-rrf.md)) and [cross-encoder re-ranking](../retrieval/cross-encoder-reranking.md) on top of a cheap first-stage retriever consistently outperform relying on a single dense embedding model alone — BEIR is the specific benchmark where that pattern was first demonstrated systematically across many domains rather than argued from intuition.

## BEIR vs. MTEB

[MTEB](mteb.md) is the broader benchmark, and folds BEIR's own datasets in as its Retrieval task category — so a model's [MTEB](mteb.md) Retrieval score and its BEIR score draw on largely the same underlying data. The difference in practice: BEIR is retrieval-only and architecture-comparing by design (lexical vs. dense vs. reranked), which makes it the more direct reference when the decision in front of you is "what retrieval architecture should this pipeline use," whereas [MTEB](mteb.md) is the better reference when the decision is "which specific embedding model should I use," since it also scores models on classification, clustering, and the other task categories [MTEB](mteb.md) covers that BEIR never touches.

## Practical takeaway for a RAG pipeline

```
Don't assume: "I'll use a top-MTEB-ranked dense embedding model
               and that alone will retrieve well on my corpus."

BEIR's finding instead supports:
  1. Start with (or keep) BM25 as a baseline — it's rarely
     embarrassingly bad, even zero-shot, and is cheap
  2. Add a dense retriever and merge via hybrid search
  3. Add cross-encoder re-ranking on the merged candidate set
  4. Validate all of the above against your own corpus using
     Recall@k / Precision@k (BEIR's generalization claims are
     about domain shift on average — they don't guarantee your
     specific domain behaves identically)
```

## Related

- [MTEB](mteb.md) — the broader multi-task embedding benchmark that folds BEIR's own retrieval datasets in as its Retrieval category
- [BM25](../retrieval/bm25.md) — the lexical baseline BEIR showed to be more robust zero-shot than many dense retrievers expected
- [Hybrid Search](../retrieval/hybrid-search.md) — the combined lexical+dense architecture BEIR's findings motivate over dense-only retrieval
- [Cross-Encoder Re-Ranking](../retrieval/cross-encoder-reranking.md) — the architecture that generalized best zero-shot across BEIR's 18 datasets
- [Bi-Encoder](../retrieval/bi-encoder.md) — the dense-retrieval mechanism whose zero-shot weakness BEIR specifically surfaced
- [Retrieval Metrics](retrieval-metrics.md) — the Recall@k/Precision@k scoring BEIR's own datasets are evaluated with
- [RAG](../rag/rag.md) — the system whose retrieval-architecture choice BEIR's findings most directly inform
