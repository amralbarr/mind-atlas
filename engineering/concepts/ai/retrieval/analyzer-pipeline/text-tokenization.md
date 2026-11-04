# Tokenization (Information Retrieval)

Tokenization, in the search-indexing sense, is the step that splits raw text into discrete terms — the first stage of the [analyzer pipeline](../text-analysis.md) that feeds an [inverted index](../inverted-index.md). It is the **first thing that happens** to text before normalization, [stemming](stemming.md), or [stopword removal](stopword-removal.md) can run on it.

## Not to be confused with LLM tokenization

This is a different concept from [LLM Tokenization](../../generation/tokenization.md), which splits text into statistical subword units via [Byte-Pair Encoding (BPE)](../../generation/tokenization.md#byte-pair-encoding-bpe) (e.g. `"ization"` as a BPE fragment) so a language model can process it. The two share a name but solve unrelated problems: IR tokenization almost always produces whole, human-readable words; [LLM](../../generation/llm.md) tokenization frequently produces word fragments that mean nothing on their own.

## How it works

The simplest approach splits on whitespace and punctuation:

```
"The leave policy entitles employees to 30 days."
  → ["The", "leave", "policy", "entitles", "employees", "to", "30", "days"]
```

Real tokenizers handle more edge cases than that one-liner suggests:

| Case | Issue | Typical handling |
|---|---|---|
| Contractions | `"don't"` → one token or two? | Engine-specific rule (e.g. `"don't"` → `["don't"]` vs `["do", "n't"]`) |
| Hyphenated words | `"state-of-the-art"` | Often split into separate tokens, sometimes kept whole depending on the tokenizer |
| Numbers, dates, URLs | `"2026-01-15"`, `"user@example.com"` | Special-cased so they aren't shredded into meaningless fragments |
| No whitespace between words | Chinese, Japanese | Requires a dedicated word-segmentation model, not a punctuation rule — splitting on whitespace alone doesn't work at all |

## Libraries and technologies

| Tool | Approach | Notes |
|---|---|---|
| **[Lucene](../../../databases/search/lucene.md) `standard` tokenizer** (used by [Elasticsearch](../../../databases/search/elasticsearch.md) / [OpenSearch](../../../databases/search/opensearch.md) by default) | Unicode-aware, rule-based | Handles most languages reasonably; the default unless a language-specific analyzer is configured |
| **[Lucene](../../../databases/search/lucene.md) `whitespace` tokenizer** | Splits only on whitespace | No punctuation handling — rarely the right default, but useful when exact token boundaries matter |
| **ICU tokenizer** ([Elasticsearch](../../../databases/search/elasticsearch.md)/[OpenSearch](../../../databases/search/opensearch.md) plugin) | Unicode Text Segmentation rules | Better multi-script and Arabic/CJK handling than the standard tokenizer |
| **NLTK `word_tokenize`** (Python) | Rule-based (Penn Treebank conventions) | Common in research/prototyping code, not typically what a search engine uses internally |
| **spaCy tokenizer** | Rule-based with per-language exception lists | Fast, production-grade; used when building a custom [NLP](../../nlp.md) pipeline rather than relying on a search engine's built-in analyzer |
| **Jieba** | Statistical word segmentation | The standard choice for Chinese, which has no whitespace between words |
| **MeCab** | Morphological analyzer | The standard choice for Japanese, for the same reason |

## Related

- [Text Analysis Pipeline](../text-analysis.md) — the overview this is the first stage of
- [Text Normalization](text-normalization.md) — the next stage
- [Inverted Index](../inverted-index.md) — what tokens ultimately get stored into
- [LLM Tokenization](../../generation/tokenization.md) — a different, unrelated concept with the same name
- [Elasticsearch](../../../databases/search/elasticsearch.md) / [OpenSearch](../../../databases/search/opensearch.md) — where these tokenizers are configured as part of an analyzer
- [Lucene](../../../databases/search/lucene.md) — the library these tokenizer implementations actually come from
