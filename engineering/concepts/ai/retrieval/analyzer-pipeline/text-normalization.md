# Text Normalization (Search Indexing)

Normalization is the stage of the [analyzer pipeline](../text-analysis.md) that standardizes tokens so different surface forms of "the same word" are treated as identical terms — it runs right after [tokenization](text-tokenization.md) and before [stemming](stemming.md)/[lemmatization](lemmatization.md).

## How it works

| Technique | What it does | Example |
|---|---|---|
| **Lowercasing** | Removes case as a distinguishing factor | `"Leave"` and `"leave"` → both `"leave"` |
| **[Unicode normalization](unicode-normalization.md)** (NFC/[NFKC](nfkc.md)) | Collapses different byte-level encodings of the visually identical character into one canonical form | A combining-character sequence and its precomposed equivalent both become one form, preventing silent mismatches |
| **Accent/diacritic folding** (ASCII folding) | Strips accents so a query without them still matches | `"café"` → `"cafe"` |
| **Script-specific normalization** | Collapses visually-different-but-semantically-identical forms specific to a writing system | Arabic: different forms of alef folded to one; diacritics stripped. German: `"ö"` ↔ `"oe"` equivalence |

Script-specific normalization matters more for some languages than others. For Arabic specifically, this step is more consequential for retrieval quality than [stemming](stemming.md) is — the same word can legitimately be written several different ways depending on diacritic/letter-variant conventions, and failing to normalize means those forms never match each other at all. It needs to preserve exact-match fields (IDs, proper nouns) separately rather than applying blindly everywhere — see [Arabic Normalization for Retrieval](arabic-normalization.md) for the full reference (a per-step risk table, a working implementation, and per-dialect evaluation) and the [interview question](../../../../interview/interview-01/11-rag-deep-dive.md#r06--intermediate--how-would-you-normalize-arabic-text-for-retrieval) this backs.

## Libraries and technologies

| Tool | What it provides |
|---|---|
| **[Lucene](../../../databases/search/lucene.md) `lowercase` filter** | Case normalization, used by [Elasticsearch](../../../databases/search/elasticsearch.md)/[OpenSearch](../../../databases/search/opensearch.md) |
| **[Lucene](../../../databases/search/lucene.md) `asciifolding` filter** | Accent/diacritic stripping for Latin scripts |
| **[Lucene](../../../databases/search/lucene.md) `arabic_normalization` filter** | Arabic letter-variant and diacritic normalization — part of both engines' built-in `arabic` analyzer |
| **ICU normalization filter** | General [Unicode NFC/NFKC normalization](unicode-normalization.md), available as a plugin in both engines |
| **[Azure AI Search](../../../cloud/azure/azure-ai-search.md) language analyzers** (`ar.microsoft`, `ar.lucene`, and other per-language options) | Equivalent built-in normalization, selectable per field — see [Azure AI Search](../../../cloud/azure/azure-ai-search.md) |
| **Python `unicodedata.normalize()`** | Standard-library [Unicode normalization](unicode-normalization.md) (NFC/NFD/[NFKC](nfkc.md)/NFKD) for custom pipelines |
| **Python `unidecode` package** | Aggressive transliteration to ASCII — useful outside a search engine's own analyzer, e.g. for generating URL slugs |

## Related

- [Text Analysis Pipeline](../text-analysis.md) — the overview this is a stage of
- [Unicode Normalization Forms (NFC, NFD, NFKC, NFKD)](unicode-normalization.md) — the mechanics behind this table's first row
- [Arabic Normalization for Retrieval](arabic-normalization.md) — the full Arabic-specific deep dive
- [Tokenization](text-tokenization.md) — the stage before this one
- [Stemming](stemming.md) / [Lemmatization](lemmatization.md) — the stages after this one
- [Elasticsearch](../../../databases/search/elasticsearch.md), [OpenSearch](../../../databases/search/opensearch.md), [Azure AI Search](../../../cloud/azure/azure-ai-search.md) — where these normalizers are configured as part of an analyzer
- [Lucene](../../../databases/search/lucene.md) — the library most of these filters actually come from
