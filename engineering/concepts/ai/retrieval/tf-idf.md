# TF-IDF (Term Frequency–Inverse Document Frequency)

TF-[IDF](idf.md) is the classical statistic behind lexical/keyword relevance scoring — the direct predecessor [BM25](bm25.md) builds on and improves. It answers the same basic question [BM25](bm25.md) does ("how relevant is this document to this query term") with a simpler, older formula that [BM25](bm25.md) was specifically designed to fix the weaknesses of.

## The formula

```
TF-IDF(t, d) = TF(t, d) × IDF(t)
```

Two independent factors multiplied together:

- **TF (Term Frequency)** — how often term `t` appears in document `d`. The simplest version is just the raw count; variants normalize it (e.g. divide by total words in the document) to avoid unfairly favoring longer documents.
- **[IDF (Inverse Document Frequency)](idf.md)** — how rare term `t` is across the whole corpus; see [IDF](idf.md) for the full formula and a worked example.

## Why TF-IDF alone falls short — and what BM25 fixes

TF-IDF has two problems that a raw document search with it will run into immediately:

1. **Term frequency scales linearly, with no saturation.** A document mentioning "leave policy" 20 times scores roughly 20× higher on that term than one mentioning it once — even though a document isn't meaningfully 20× more "about" a topic just because of repetition. This makes raw TF-IDF easy to game with keyword stuffing.
2. **No length normalization.** A long document has more raw opportunities for a term to appear by coincidence, so it can out-score a short, genuinely on-topic document purely by virtue of being longer.

[BM25](bm25.md) is TF-IDF's direct answer to both: it adds a **saturation parameter (`k1`)** so additional term occurrences contribute diminishing returns, and a **length normalization parameter (`b`)** so document length doesn't unfairly dominate the score. [BM25](bm25.md)'s [IDF](idf.md) term is also a refined version of TF-IDF's — see [BM25](bm25.md) for the full formula and both parameters in detail.

## Where TF-IDF still shows up today

Despite [BM25](bm25.md) being the standard in real search engines now — [Elasticsearch](../../databases/search/elasticsearch.md), [OpenSearch](../../databases/search/opensearch.md), and most other engines moved to [BM25](bm25.md) as their default scorer years ago — TF-IDF hasn't disappeared. It's still common as:

- **A simple baseline** in classical ML text pipelines, via `scikit-learn`'s `TfidfVectorizer` — turning a corpus of documents into a sparse term-weighted feature matrix for tasks like document clustering, classification, or similarity search that don't need a full search-engine stack.
- **A teaching/interview reference point** — understanding TF-IDF's two weaknesses is the fastest way to actually understand *why* BM25's two extra parameters exist, rather than just memorizing BM25's formula.

## Related

- [BM25](bm25.md) — the production-grade successor that fixes TF-IDF's saturation and length-normalization problems
- [IDF](idf.md) — the rarity-weighting factor shared by both TF-IDF and BM25, explained on its own
- [IDF vs. TF-IDF vs. BM25](../../../overviews/ai/idf-vs-tf-idf-vs-bm25.md) — a worked example showing all three ranking the same documents three different ways
- [Inverted Index](inverted-index.md) — the data structure both TF-IDF and BM25 score against
- [Hybrid Search](hybrid-search.md) — where lexical scoring (TF-IDF/BM25) is combined with vector search
- [Text Analysis Pipeline](text-analysis.md) — the tokenization/normalization/stopword-removal steps that happen before any TF-IDF or BM25 score is computed
