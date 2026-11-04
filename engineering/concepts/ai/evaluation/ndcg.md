# NDCG (Normalized Discounted Cumulative Gain)

**The core question:** Not just *whether* relevant results appear near the top, but *how relevant* each one is — rewarding a ranking that puts the most relevant results first, when relevance itself is graded rather than a flat yes/no.

```
DCG  = Σ (2^rel_i - 1) / log2(i + 1)     for rank i = 1, 2, 3, ...
IDCG = DCG of the same relevance grades, sorted into their ideal order
NDCG = DCG / IDCG
```

`rel_i` is the graded relevance of the result at rank `i` (e.g. 0 = irrelevant, 1 = somewhat relevant, 3 = highly relevant) — this is what distinguishes NDCG from [Recall@k/Precision@k](retrieval-metrics.md), which only know "relevant" or "not."

## Worked Example

Relevance grades for a ranked result list `[3, 0, 1]` (rank 1 has grade 3, rank 2 has grade 0, rank 3 has grade 1):

```
DCG  = (2³-1)/log₂(2) + (2⁰-1)/log₂(3) + (2¹-1)/log₂(4)
     =    7/1        +      0/1.585   +    1/2
     =    7          +      0         +    0.5
     =    7.5

Ideal order (sorted descending): [3, 1, 0]
IDCG = (2³-1)/log₂(2) + (2¹-1)/log₂(3) + (2⁰-1)/log₂(4)
     =    7/1        +      1/1.585   +    0/2
     =    7          +      0.631     +    0
     =    7.631

NDCG@3 = 7.5 / 7.631 ≈ 0.983
```

The result list wasn't in its ideal order (the grade-1 item is ranked ahead of nothing it should be behind, but the actual top grade-3 item is already in the right place) — NDCG@3 of 0.983 reflects that the ranking is very close to ideal, not perfect, because of how the discount (`log2(i+1)`) and gain (`2^rel - 1`) terms interact once grades aren't binary.

## Two Deliberate Design Choices in the Formula

| Choice | What it does | Why |
|---|---|---|
| **Logarithmic discount** (`log2(i+1)`) | Penalizes a relevant result less harshly the further down it sits, but the penalty still grows every rank | A linear discount would punish rank 10 ten times as hard as rank 1; the log keeps the gap between adjacent low ranks small while still rewarding rank 1 heavily |
| **Exponential gain** (`2^rel - 1`) | A grade-3 result contributes far more than 3× a grade-1 result (`2³-1=7` vs `2¹-1=1`) | Makes a genuinely highly-relevant result dominate the score, rather than letting several mediocre results add up to outweigh one excellent one |

## NDCG vs. Recall@k/Precision@k vs. MRR

| Metric | Needs graded relevance? | Rewards |
|---|---|---|
| **[Recall@k](retrieval-metrics.md#recallk) / [Precision@k](retrieval-metrics.md#precisionk)** | No — binary relevant/not | Whether relevant results are present in the top-k set at all |
| **[MRR](mrr.md)** | No — binary relevant/not | How early the *first* relevant result appears |
| **NDCG** | Yes — needs a relevance grade per result | Both position *and* degree of relevance, across the whole ranked list, not just the first hit |

NDCG is strictly more informative when graded relevance data exists, but that's exactly its practical cost: Recall@k, Precision@k, and [MRR](mrr.md) only need a binary relevant/irrelevant label per document, which is far cheaper to collect (a yes/no judgment) than a multi-level relevance grade (which usually needs a human rater applying a defined rubric, or an [LLM](../generation/llm.md)-as-judge producing a consistent grade rather than a binary call). This is why NDCG is the standard in classical search-ranking research and competitions (where graded relevance judgments are a core part of the benchmark) but shows up less often in day-to-day [RAG](../rag/rag.md) evaluation, where a binary "did the retrieved chunk actually get used to answer correctly" judgment is usually both cheaper to collect and sufficient for the decision being made (ship/don't ship, regression/no regression).

## Common Questions

**If NDCG is more informative, why does this handbook's [RAG](../rag/rag.md) evaluation lean on Recall@k/MRR instead?**
> Cost of the judgment, not quality of the metric. A graded relevance scale needs a defined rubric and a rater (human or [LLM](../generation/llm.md)-as-judge) applying it consistently across the whole evaluation set, which is more expensive to build and maintain than a binary "did this chunk get cited and used" label. Teams adopt NDCG when they already have graded judgments for another reason (e.g. licensing a search-quality benchmark) or when ranking quality beyond the top few results genuinely matters for the product.

**What happens if two different queries have different numbers of relevant results — can NDCG still compare them fairly?**
> Yes — that's the entire purpose of the "normalized" step. Dividing by IDCG (the best possible DCG for that query's own specific relevance grades) rescales every query's score to the same 0-1 range regardless of how many relevant results it has or how they're graded, which is exactly what makes averaging NDCG across queries with different ideal rankings meaningful.

**Is NDCG@k truncated the same way Recall@k is?**
> Yes — DCG and IDCG are both summed only over the first k ranks, so NDCG@3 only considers whether the top 3 results are well-ordered by relevance; anything beyond rank k (relevant or not) has no effect on the score, the same truncation behavior [Recall@k](retrieval-metrics.md#recallk) has.

## Related

- [Retrieval Metrics](retrieval-metrics.md) — the full metrics family (Recall@k, Precision@k, NDCG) this file's metric belongs to
- [MRR](mrr.md) — the binary-relevance metric for "how early does the first good result appear," the cheaper alternative when a full relevance grade isn't available
- [Groundedness and Correctness](groundedness-and-correctness.md) — the generation-side quality dimensions NDCG doesn't measure; NDCG only scores the ranking of retrieved candidates, not whether the final generated answer is accurate
- [LLM Evaluation](llm-evaluation.md) — where graded relevance judgments, when collected via LLM-as-judge, feed into this formula
- [Cross-Encoder Re-Ranking](../retrieval/cross-encoder-reranking.md) — the stage most likely to move NDCG, by reordering candidates according to a finer-grained relevance signal than the first-pass retriever used
