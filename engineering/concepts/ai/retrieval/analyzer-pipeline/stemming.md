# Stemming

Stemming is a rule-based technique for reducing a word to a common base form (a "stem") by stripping suffixes — so that searching for one form of a word matches documents containing related forms, without needing a dictionary lookup. It's the faster, cruder sibling of [lemmatization](lemmatization.md) in the [analyzer pipeline](../text-analysis.md).

## How it works

Stemmers apply a fixed set of suffix-stripping rules, typically in ordered passes (strip plurals, then strip common verb/adjective endings, then clean up the result):

```
"running"     → "run"
"runs"        → "run"
"entitlement" → "entitl"      ← not a real word, but a consistent bucket
"universal"   → "univers"
"university"  → "univers"     ← different word, same stem — a false match ("over-stemming")
```

The stem doesn't need to be a real word — it only needs to be **consistent**, so that every related form of a word collapses to the same bucket and matches each other in search.

## The Porter stemmer family

The **Porter stemmer** (1980) is the original and most widely referenced English stemming algorithm — a fixed sequence of rule phases (strip plurals, strip `-ed`/`-ing`, clean up doubled consonants, etc.), each applied in order. **Snowball** (also called "Porter2") is Martin Porter's own refinement of the original algorithm, with more consistent rules and a framework that extends to many other languages, not just English. **Lancaster** is a more aggressive, iterative stemmer that produces shorter stems than Porter/Snowball — higher recall, more risk of over-stemming unrelated words together.

## The trade-off: over-stemming vs. under-stemming

| Failure mode | What happens | Effect |
|---|---|---|
| **Over-stemming** | Unrelated words collapse to the same stem (`"university"`/`"universal"` → `"univers"`) | False-positive matches — a search returns irrelevant results |
| **Under-stemming** | Related words don't collapse to the same stem | False-negative matches — a search misses relevant results (the same recall loss as not stemming at all) |

There's no universally correct setting — a more aggressive stemmer (Lancaster) trades precision for recall compared to a conservative one (Porter), the same [precision/recall tension](../../evaluation/retrieval-metrics.md) that shows up everywhere else in retrieval.

## Libraries and technologies

| Tool | What it provides |
|---|---|
| **NLTK** (`PorterStemmer`, `SnowballStemmer`, `LancasterStemmer`) | Python implementations of all three algorithms above, for custom pipelines outside a search engine |
| **[Lucene](../../../databases/search/lucene.md) stemmer filters** (used by [Elasticsearch](../../../databases/search/elasticsearch.md)/[OpenSearch](../../../databases/search/opensearch.md)) | Per-language stemmer token filters (e.g. `arabic_stem`, `english` via the Snowball-based `PorterStemFilter`), applied automatically by each engine's built-in language analyzers |
| **[Azure AI Search](../../../cloud/azure/azure-ai-search.md)** | Stemming is bundled inside its per-language analyzers (`ar.microsoft`, `ar.lucene`, etc.) rather than configured as a separate step — see [Azure AI Search](../../../cloud/azure/azure-ai-search.md) |

Note: **spaCy does not implement stemming at all** — it only does [lemmatization](lemmatization.md). If you're using spaCy and expecting a Porter-style stemmer, you won't find one; that's a deliberate design choice by the library, not a missing feature.

## Related

- [Lemmatization](lemmatization.md) — the dictionary-based alternative, with a direct comparison
- [Text Analysis Pipeline](../text-analysis.md) — the overview this is a stage of
- [Text Normalization](text-normalization.md) — the stage before this one
- [BM25](../bm25.md) — scores whatever terms stemming ultimately produces
- [Lucene](../../../databases/search/lucene.md) — the library whose stemmer filters implement this stage inside [Elasticsearch](../../../databases/search/elasticsearch.md)/[OpenSearch](../../../databases/search/opensearch.md)
- [Retrieval Metrics](../../evaluation/retrieval-metrics.md) — where the precision/recall effect of stemming choices is actually measured
