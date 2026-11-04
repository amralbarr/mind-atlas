# IDF (Inverse Document Frequency)

IDF is the weight that makes [TF-IDF](tf-idf.md) and [BM25](bm25.md) both favor rare, informative terms over common ones — it's the shared building block underneath both scoring formulas, not something unique to either one. On its own it answers one question: "how much does matching this particular term actually tell you?"

## The core idea

A term that appears in almost every document in the corpus — "the", "a", "is" — tells you almost nothing about what makes one document different from another. A term that appears in only a handful of documents — a product code, a rare technical term, a proper noun — is highly informative when it does match. IDF converts "how many documents contain this term" into a weight that's large for rare terms and near-zero for common ones.

## The formula — two real variants

**Plain [TF-IDF](tf-idf.md)'s version:**

```
IDF(t) = log( N / n(t) )
```

**[BM25](bm25.md)'s smoothed version:**

```
IDF(t) = log( (N - n(t) + 0.5) / (n(t) + 0.5) + 1 )
```

In both, `N` is the total number of documents in the corpus and `n(t)` is how many of them contain term `t` at all (not how many *times* — that's term frequency, a separate factor). [BM25](bm25.md)'s version adds the `+0.5` smoothing constants specifically to avoid breaking down at the edges: the plain formula produces `log(1) = 0` for a term in every document (fine) but is undefined or can go negative in edge cases the smoothed version handles more gracefully, particularly for very common terms in a small corpus.

## Worked example

A corpus of 1,000 documents. The word "the" appears in 950 of them; the word "entitlement" appears in 12 of them.

```
IDF("the")         = log(1000 / 950)  ≈ log(1.05)  ≈ 0.05   — contributes almost nothing
IDF("entitlement") = log(1000 / 12)   ≈ log(83.3)  ≈ 4.42   — a match counts for a lot
```

A single match on "entitlement" is worth roughly 88× as much score as a single match on "the" — purely from how rare each term is across the corpus, before term frequency or document length even enter the calculation.

## Why this matters beyond the formula

IDF is *why* [BM25](bm25.md) and [TF-IDF](tf-idf.md) don't strictly need [stopword removal](analyzer-pipeline/stopword-removal.md) to behave reasonably: a term like "the" naturally scores itself down to near-irrelevance through its own IDF weight, without needing to be stripped from the index first. [Stopword removal](analyzer-pipeline/stopword-removal.md) still matters for index size and query performance, but the *relevance correctness* problem common words would otherwise cause is already substantially handled by IDF alone.

## Related

- [BM25](bm25.md) — uses the smoothed IDF variant as one of its two multiplied factors
- [TF-IDF](tf-idf.md) — uses the plain IDF variant, multiplied by term frequency
- [IDF vs. TF-IDF vs. BM25](../../../overviews/ai/idf-vs-tf-idf-vs-bm25.md) — a worked example showing IDF alone, [TF-IDF](tf-idf.md), and [BM25](bm25.md) ranking the same three documents three different ways
- [Stopword Removal](analyzer-pipeline/stopword-removal.md) — why IDF already does most of what [stopword removal](analyzer-pipeline/stopword-removal.md) does, for relevance purposes
- [Inverted Index](inverted-index.md) — stores the per-term document frequency (`n(t)`) that IDF is computed from
