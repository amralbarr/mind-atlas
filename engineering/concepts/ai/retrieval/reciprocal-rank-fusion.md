# Reciprocal Rank Fusion (RRF)

Reciprocal Rank Fusion is the standard way to merge two or more independently-ranked result lists into one unified ranking — most commonly the vector-search list and the [BM25](bm25.md) keyword-search list in [hybrid search](hybrid-search.md). Its defining trait: it ignores the actual scores entirely and works purely from each result's **rank position** in each list.

## Why not just combine the raw scores?

Cosine similarity (vector search) and a [BM25](bm25.md) score (keyword search) live on completely different, incompatible scales — a cosine similarity is bounded between -1 and 1, while a [BM25](bm25.md) score is an unbounded, corpus-dependent number that can be anywhere from 0 to double digits depending on term rarity and document length. Adding `0.82 + 14.3` together is meaningless without first normalizing both to a comparable range, and that normalization step is itself a source of error (which normalization method, fit to which distribution, recalculated how often?).

RRF sidesteps the whole problem: it never looks at the scores, only at where each result *ranked* in its own list.

## The formula

```
RRF_score(d) = Σ  1 / (k + rank_i(d))
              i∈lists
```

For each list a document `d` appears in, take `1 / (k + rank)` — where `rank` is its position in that list (1st, 2nd, 3rd...) — and sum that across every list it appears in. `k` is a constant (commonly `60`, following the original paper) that controls how much weight very-top-ranked results get relative to lower ones; a document that doesn't appear in a list at all contributes nothing from that list.

## Worked example

Document `A` ranks 1st in the vector list and 3rd in the keyword list. Document `B` ranks 5th in the vector list but 1st in the keyword list. Using `k = 60`:

```
RRF(A) = 1/(60+1) + 1/(60+3) = 0.01639 + 0.01587 = 0.03226
RRF(B) = 1/(60+5) + 1/(60+1) = 0.01538 + 0.01639 = 0.03177
```

`A` wins narrowly — despite `B` being the #1 keyword match, its weaker vector-side showing (5th) pulls its combined score just below `A`'s. This is the behavior RRF is designed to produce: **a document that both methods agree is reasonably good tends to outrank a document only one method loves and the other ranks poorly** — agreement across signals matters more than any single method's top pick.

## Why `k` matters

`k` controls how steeply the reward drops off as rank gets worse:

- **Smaller `k`** (e.g. `k = 10`): the gap between rank 1 and rank 2 is proportionally large — top ranks dominate heavily.
- **Larger `k`** (e.g. `k = 60`, the common default): the curve is flatter — the difference between being ranked 1st and 5th matters less, so RRF behaves more like "did this show up near the top of either list" than "which list's #1 pick wins."

There's no universally correct value — like most of retrieval tuning, it's worth [measuring](../evaluation/retrieval-metrics.md) against your own real queries rather than assuming the paper's default transfers unchanged to every corpus.

## RRF vs. the alternatives

| Strategy                                                   | How it works                                                                                      | Trade-off                                                                                                                                                                |
| ---------------------------------------------------------- | ------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **RRF**                                                    | Rank-position-based, as above                                                                     | Robust to scale mismatches; ignores *how much* better a result is, only *that* it ranked higher                                                                          |
| **Weighted sum (`alpha` blending)**                        | Normalize both score sets to 0–1, combine as `alpha * vector_score + (1 - alpha) * keyword_score` | Preserves magnitude information RRF throws away, but requires getting the normalization and `alpha` right — and both can drift as the corpus changes                     |
| **[Cross-encoder re-ranking](cross-encoder-reranking.md)** | Run a separate, more expensive model that scores each query-document pair directly                | More accurate than either fusion method, but costs real latency/compute per query — often used as a second pass *after* RRF narrows the candidate set, not instead of it |
|                                                            |                                                                                                   |                                                                                                                                                                          |

## Where it shows up in this handbook

RRF is the merge step in [Azure AI Search](../../cloud/azure/azure-ai-search.md)'s and [OpenSearch](../../databases/search/opensearch.md)'s native [hybrid search](hybrid-search.md), and the standard recommendation for manually combining `pgvector` and `tsvector` results in [PostgreSQL](../../databases/relational/postgresql.md) — see [Hybrid Search](hybrid-search.md) for the full picture of where RRF sits in a retrieval pipeline.

## Related

- [Hybrid Search](hybrid-search.md) — the pattern RRF's merge step feeds into
- [BM25](bm25.md) — one of the two score scales RRF exists to avoid comparing directly
- [Cross-Encoder Re-Ranking](cross-encoder-reranking.md) — the more expensive, more accurate alternative/complement
- [Retrieval Metrics](../evaluation/retrieval-metrics.md) — how to actually measure whether a given `k` or fusion strategy helps
- [Azure AI Search](../../cloud/azure/azure-ai-search.md), [OpenSearch](../../databases/search/opensearch.md) — real engines that implement RRF natively
- [BM25 vs. Hybrid Search vs. RRF](../../../overviews/ai/bm25-vs-hybrid-search-vs-rrf.md) — how these three relate, with a second worked merge example
