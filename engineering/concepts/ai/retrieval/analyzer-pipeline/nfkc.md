# NFKC (Unicode Normalization Form Compatibility Composition)

NFKC is the [Unicode normalization form](unicode-normalization.md) actually used throughout this handbook's search-indexing code — it's the one that shows up as `unicodedata.normalize("NFKC", text)` in [Arabic Normalization for Retrieval](arabic-normalization.md) and in [Text Normalization](text-normalization.md)'s general pipeline. This page is the deep dive on specifically *why* NFKC, as opposed to its sibling form NFC.

## What it does

NFKC does two things in sequence: **compatibility decomposition** (break every character down to its most basic form, including collapsing ligatures, presentation forms, and font/width variants into their plain equivalents) followed by **canonical composition** (recombine any base-character-plus-combining-mark sequences back into their precomposed form where one exists). The net effect: text that *looks* and *means* the same thing converges onto one single byte representation, even when the original encodings differed for presentational reasons.

## The concrete problem it solves

```
ﻻ  (U+FEFB — ARABIC LIGATURE LAM WITH ALEF ISOLATED FORM, one code point)
     ↓ NFKC
لا  (ل + ا — the canonical two-letter sequence)
```

This ligature is a **compatibility** mapping in the Unicode Character Database, not a canonical one — it exists specifically to support certain rendering/presentation contexts, and shows up constantly in text extracted from PDFs, which often preserve presentation-form glyphs straight from the original font rather than the underlying letters. Because it's a compatibility mapping rather than a canonical one, **NFC leaves it completely untouched** — only the "K" forms (NFKC or NFKD) decompose it into the ordinary letters a search index actually needs in order to match it against a normal query.

The same logic applies well beyond Arabic:

| Input | NFKC output | Why |
|---|---|---|
| `"ﬁ"` (U+FB01, the fi-ligature) | `"fi"` (two letters) | Typographic ligature, compatibility mapping |
| `"Ａ"` (U+FF21, full-width Latin A) | `"A"` (regular) | Full-width/half-width variant, compatibility mapping |
| `"²"` (superscript two) | `"2"` (regular digit) | Formatting variant, compatibility mapping |
| `"é"` (two code points: e + combining acute) | `"é"` (one precomposed code point) | Canonical equivalence — NFC alone already handles this part |

## Why this makes NFKC lossy — and what that costs you

Collapsing `"²"` to `"2"`, or a ligature to its component letters, is exactly the behavior you want for search matching — but it means NFKC-normalized text is no longer faithful to the source document's original formatting. A superscript footnote marker and a plain digit become indistinguishable after NFKC runs. This is precisely why this handbook's indexing pattern (see [Arabic Normalization for Retrieval](arabic-normalization.md)) always stores an untouched `text_original` field for display/citation purposes alongside the NFKC-normalized field used for search — NFKC is something you apply to the *copy* used for matching, never to the text a user or citation ultimately sees.

## Libraries and technologies

| Tool | How to use it |
|---|---|
| **Python `unicodedata`** (stdlib) | `unicodedata.normalize("NFKC", text)` |
| **JavaScript** (native, ES2015+) | `text.normalize("NFKC")` — built into the `String` prototype, no library needed |
| **Java / ICU4J** | `java.text.Normalizer.normalize(text, Normalizer.Form.NFKC)` |
| **[Lucene](../../../databases/search/lucene.md) `icu_normalizer` token filter** (used by [Elasticsearch](../../../databases/search/elasticsearch.md)/[OpenSearch](../../../databases/search/opensearch.md)) | Set to NFKC mode as part of a custom analyzer; bundled automatically inside each engine's built-in language analyzers |

## Related

- [Lucene](../../../databases/search/lucene.md) — the library whose `icu_normalizer` filter implements this inside [Elasticsearch](../../../databases/search/elasticsearch.md)/[OpenSearch](../../../databases/search/opensearch.md)
- [Unicode Normalization Forms (NFC, NFD, NFKC, NFKD)](unicode-normalization.md) — the overview comparing all four forms, and where NFC's narrower canonical-only behavior is explained
- [Arabic Normalization for Retrieval](arabic-normalization.md) — the concrete code and ligature example this page is built from
- [Text Normalization](text-normalization.md) — the broader pipeline stage NFKC is one technique within
- [OCR](../../ingestion/ocr.md) — presentation-form/ligature issues often originate from how a PDF or [OCR](../../ingestion/ocr.md) engine extracted the glyphs in the first place
