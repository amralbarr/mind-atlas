# Text Analysis: Tokenization, Normalization, Stemming & Lemmatization

Before text can be scored by [BM25](bm25.md) or stored in an [inverted index](inverted-index.md), it has to be broken down and standardized into a consistent set of terms — a pipeline search engines call an **analyzer** ([Elasticsearch](../../databases/search/elasticsearch.md)/[OpenSearch](../../databases/search/opensearch.md)'s own term for it; see [Elasticsearch](../../databases/search/elasticsearch.md) and [OpenSearch](../../databases/search/opensearch.md)). The same pipeline runs at indexing time (to decide what terms get stored) and at query time (to decide what terms the query is actually searching for) — if the two don't match, exact-sounding searches silently fail to find obviously relevant documents.

```
Raw text → Tokenization → Normalization → Stemming / Lemmatization → (Stopword removal) → Terms stored in the inverted index
```

## Not to be confused with LLM tokenization

This page is about **information-retrieval tokenization** — splitting text into discrete words/terms for keyword search. It is a different concept from [LLM Tokenization](../generation/tokenization.md), which splits text into statistical subword units (e.g. `"ization"` as a BPE token fragment) so a language model can process it — the two share a name but solve unrelated problems. IR tokenization almost always produces whole words; [LLM](../generation/llm.md) tokenization frequently doesn't.

## Tokenization

Splitting text into individual terms, typically on whitespace and punctuation boundaries:

```
"The leave policy entitles employees to 30 days."
  → ["the", "leave", "policy", "entitles", "employees", "to", "30", "days"]
```

This sounds trivial for English but isn't universal — languages without whitespace between words (Chinese, Japanese) need a dedicated word-segmentation model rather than a punctuation-splitting rule, and Arabic's own tokenization interacts with the normalization step below closely enough that chunk/token budgets shift depending on the choices made (see the [Arabic text normalization question](../../../interview/interview-01/11-rag-deep-dive.md#r06--intermediate--how-would-you-normalize-arabic-text-for-retrieval) for where this matters in practice).

## Normalization

Standardizing tokens so different surface forms of "the same word" match each other:

- **Lowercasing** — `"Leave"` and `"leave"` should match the same term.
- **[Unicode normalization](analyzer-pipeline/unicode-normalization.md)** (NFC/[NFKC](analyzer-pipeline/nfkc.md)) — the same visual character can be encoded as different byte sequences; normalizing to one canonical form prevents silent mismatches.
- **Accent/diacritic folding** — `"café"` → `"cafe"`, so a query without the accent still matches.
- **Script-specific normalization** — Arabic text commonly normalizes letter variants (e.g. different forms of alef) and strips diacritics before indexing, since the same word can be written multiple visually-different-but-semantically-identical ways. This is more consequential for Arabic retrieval quality than [stemming](analyzer-pipeline/stemming.md) is, and it needs to preserve exact-match fields (IDs, proper nouns) separately rather than applying blindly everywhere. This isn't something you have to build from scratch: [Elasticsearch](../../databases/search/elasticsearch.md) ships a built-in `arabic` analyzer (letter-variant folding, diacritic stripping, Arabic [stemming](analyzer-pipeline/stemming.md)), and [Azure AI Search](../../cloud/azure/azure-ai-search.md) offers its own Arabic-specific analyzers (`ar.microsoft` and `ar.lucene`, selectable per field) — see [Azure AI Search](../../cloud/azure/azure-ai-search.md). Using the generic default analyzer on Arabic content instead of the language-specific one is a common, easy-to-miss cause of poor Arabic recall.

## Stemming vs. Lemmatization

Both reduce a word to a common base form so that searching for one form of a word finds documents containing *any* form of it — but they work differently and trade off differently:

| | [Stemming](analyzer-pipeline/stemming.md) | [Lemmatization](analyzer-pipeline/lemmatization.md) |
|---|---|---|
| **How it works** | Rule-based suffix stripping — chops off common endings | Dictionary/morphology-aware — looks up the word's actual dictionary form (lemma), often using part-of-speech context |
| **Output** | Not always a real word | Always a real dictionary word |
| **Speed** | Fast | Slower — needs a lexicon/model, sometimes POS tagging |
| **Example** | `"running"`, `"runs"`, `"ran"` → `"run"` / `"runn"` (algorithm-dependent); `"entitlement"` → `"entitl"` (not a real word, but a consistent bucket) | `"running"` → `"run"`; `"better"` → `"good"`; `"mice"` → `"mouse"` |
| **Common libraries/algorithms** | Porter stemmer, Snowball stemmer | spaCy, NLTK's `WordNetLemmatizer` |
| **Risk** | Over-[stemming](analyzer-pipeline/stemming.md) can merge unrelated words into the same bucket (false positives); under-[stemming](analyzer-pipeline/stemming.md) misses related forms (false negatives) | More accurate, but adds latency and language-model dependency to the indexing pipeline |

**Why either matters for search:** without one of these, a query for `"running"` only matches documents containing the exact string `"running"` — it won't find `"run"`, `"runs"`, or `"ran"`, which is a direct recall loss. [BM25](bm25.md) scores whatever terms actually ended up in the index; stemming/[lemmatization](analyzer-pipeline/lemmatization.md) is what decides whether morphologically related terms are even considered the same term in the first place.

## The trade-off: precision vs. recall, same shape as everywhere else in retrieval

More aggressive normalization (stemming > [lemmatization](analyzer-pipeline/lemmatization.md) > none) raises recall — more word forms collapse together, so more documents match — at some cost to precision, since unrelated words can occasionally collapse into the same stem. This is the same recall/precision tension covered in [Retrieval Metrics](../evaluation/retrieval-metrics.md), just applied one layer earlier, before [BM25](bm25.md) even runs. The practical default: start with a standard analyzer (lowercase + basic stemming) for English, measure Recall@k/Precision@k with it on your real query set, and only reach for full [lemmatization](analyzer-pipeline/lemmatization.md) or custom normalization rules (as with Arabic diacritics/letter variants) where measurement shows the default is actually losing relevant matches.

## Related

- [BM25](bm25.md) — scores whatever terms this pipeline produces
- [Inverted Index](inverted-index.md) — stores the terms this pipeline produces
- [Elasticsearch](../../databases/search/elasticsearch.md) and [OpenSearch](../../databases/search/opensearch.md) — both call this pipeline an "analyzer", and both ship a built-in `arabic` analyzer
- [Azure AI Search](../../cloud/azure/azure-ai-search.md) — offers its own Arabic-specific analyzers (`ar.microsoft`, `ar.lucene`)
- [Hybrid Search](hybrid-search.md)
- [LLM Tokenization](../generation/tokenization.md) — a different, unrelated concept with the same name
- [Retrieval Metrics](../evaluation/retrieval-metrics.md)
