# Unicode Normalization Forms (NFC, NFD, NFKC, NFKD)

Unicode allows the same visually identical character to be represented by more than one sequence of code points — which means two strings that *look* identical and *mean* the same thing can fail an exact string comparison, or fail to match each other in search, simply because they're different bytes under the hood. Unicode normalization (defined in [Unicode Standard Annex #15](https://unicode.org/reports/tr15/)) is the process of converting text to one canonical representation so this stops happening. It's one specific technique inside the broader [text normalization](text-normalization.md) stage of the [analyzer pipeline](../text-analysis.md).

## The problem, concretely

```
"é" can be encoded two different ways:
  1. One code point:  U+00E9 (LATIN SMALL LETTER E WITH ACUTE)
  2. Two code points:  U+0065 (e) + U+0301 (COMBINING ACUTE ACCENT)
```

Both render as `é` on screen. Both are "correct" Unicode. But `"é" == "é"` can be `False` if one came from form 1 and the other from form 2 — and the same risk applies to an inverted-index lookup: a document indexed with one encoding won't match a query typed with the other, even though a human reading both would call them identical.

## The four forms

| Form | What it does | Lossy? |
|---|---|---|
| **NFC** (Canonical Composition) | Decomposes, then recomposes into the shortest precomposed form where one exists | No — fully reversible in meaning |
| **NFD** (Canonical Decomposition) | Decomposes into base character + combining marks, doesn't recompose | No |
| **[NFKC](nfkc.md)** (Compatibility Composition) | Like NFC, but *also* collapses "compatibility" variants — ligatures, presentation forms, full-width/half-width characters, font variants — into their standard form, then recomposes | **Yes** — can discard formatting/presentation distinctions |
| **NFKD** (Compatibility Decomposition) | Like [NFKC](nfkc.md)'s compatibility collapsing, but doesn't recompose | **Yes** |

The distinction that actually matters in practice: **NFC/NFD only handle *canonical* equivalence** (different encodings of what Unicode considers the literal same character — accented letters being the classic case). **[NFKC](nfkc.md)/NFKD additionally handle *compatibility* equivalence** — characters that are different Unicode code points by design (a ligature, a presentation form, a full-width digit) but represent the same underlying text for most practical purposes.

## NFKC in practice

Of the four forms, **[NFKC](nfkc.md)** is the one this handbook's own search-indexing code actually calls (`unicodedata.normalize("NFKC", text)` in [Arabic Normalization for Retrieval](arabic-normalization.md)) — because it's the only form that fixes presentation-form/ligature artifacts common in PDF-extracted text (e.g. the Arabic ligature `ﻻ` → `لا`), which NFC alone leaves untouched. See [NFKC](nfkc.md) for the full explanation of why, the lossiness trade-off this implies, and library usage across Python/JavaScript/Java/[Lucene](../../../databases/search/lucene.md).

## Libraries and technologies

| Tool | How to use it |
|---|---|
| **Python `unicodedata`** (stdlib) | `unicodedata.normalize(form, text)` — forms passed as the strings `"NFC"`, `"NFD"`, `"NFKC"`, `"NFKD"` |
| **JavaScript** (native, ES2015+) | `text.normalize(form)` — built into the `String` prototype, no library needed |
| **Java / ICU4J** | `java.text.Normalizer.normalize(text, Normalizer.Form.X)` |
| **[Lucene](../../../databases/search/lucene.md) `icu_normalizer` token filter** (used by [Elasticsearch](../../../databases/search/elasticsearch.md)/[OpenSearch](../../../databases/search/opensearch.md)) | Configurable to NFC or [NFKC](nfkc.md) mode as part of a custom analyzer; bundled automatically inside each engine's built-in language analyzers |

## Related

- [NFKC](nfkc.md) — the specific form this handbook's own code uses, and why
- [Lucene](../../../databases/search/lucene.md) — the library whose `icu_normalizer` filter implements this inside [Elasticsearch](../../../databases/search/elasticsearch.md)/[OpenSearch](../../../databases/search/opensearch.md)
- [Text Normalization](text-normalization.md) — the broader stage this is one technique within
- [Arabic Normalization for Retrieval](arabic-normalization.md) — the concrete case the [NFKC](nfkc.md) example is drawn from
- [OCR](../../ingestion/ocr.md) — presentation-form/ligature issues often originate from how a PDF or [OCR](../../ingestion/ocr.md) engine extracted the glyphs in the first place
- [Tokenization](text-tokenization.md) — the stage before this one in the pipeline
