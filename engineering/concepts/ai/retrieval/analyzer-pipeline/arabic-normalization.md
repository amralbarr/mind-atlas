# Arabic Normalization for Retrieval

## The core idea

An interviewer asking "how do you normalize Arabic text for retrieval" isn't looking for a memorized rule list — they're checking whether you understand that **normalization is a trade-off**: every normalization step raises [Recall](../../evaluation/retrieval-metrics.md) (it finds more surface forms of the same word) but can lower Precision (it can merge words that are actually different). A good answer rests on three principles:

1. **Measure every decision** against your real documents and real queries — don't apply rules blindly.
2. **Keep the original text** for display and citation; the normalized text is for indexing only.
3. **Never merge what must stay distinct** — especially names and identifiers (IDs).

This page is the Arabic-specific deep dive behind the [general text normalization](text-normalization.md) stage of the [analyzer pipeline](../text-analysis.md), and the reference material behind [the Arabic normalization interview question](../../../../interview/interview-01/11-rag-deep-dive.md#r06--intermediate--how-would-you-normalize-arabic-text-for-retrieval).

## Common normalization steps and the risk of each

| Step | Before → After | Benefit | Risk |
|---|---|---|---|
| **Diacritic removal** | مُحَمَّد → محمد | Usually safe — most queries are written without diacritics | Rare: religious or legal texts where diacritics change meaning |
| **Tatweel (kashida) removal** | الســلام → السلام | Essentially always safe | Essentially none |
| **Alef unification** | أ إ آ ٱ → ا | Fixes "الاجازة" vs. "الإجازة" — a very common real-world mismatch | Low |
| **Alef maqsura unification** | ى → ي | Fixes spelling-variant mismatches | ⚠️ **"على" (the preposition "on") becomes "علي" (the proper name "Ali")** |
| **Taa marbuta unification** | ة → ه | Fixes "مدرسه" in informal writing | Merges a small number of genuinely different words |
| **Digit unification** | ٢٠٢٦ or ۲۰۲۶ → 2026 | Essential — an invoice number in Arabic-Indic digits won't otherwise match a query typed in Latin digits | Low, but verify it doesn't corrupt identifiers |
| **Invisible character removal** | RTL/LTR direction marks, ZWJ/ZWNJ, non-breaking spaces → removed or normalized to a plain space | Prevents "visually identical but digitally different" word mismatches | Essentially none |
| **[Unicode NFKC normalization](nfkc.md)** | Presentation-form glyphs like ﻻ (one code point) → لا (two code points) | Very common in text extracted from PDFs | Low |
| **[Stemming](stemming.md)** | كاتب، مكتب، كتاب → كتب | Groups related word forms together | ⚠️ **High risk: merges "writer," "office," and "book" — genuinely unrelated meanings that share a root** |

**The two highest-risk steps are alef maqsura unification and [stemming](stemming.md)** — both can silently merge words with completely different meanings. Never enable either without a measured Recall/Precision check on real queries.

## OCR and PDF extraction problems (often the most damaging issue in practice)

Before worrying about diacritics or alef variants, check the quality of the extracted text itself — see [OCR](../../ingestion/ocr.md) for the general version of this problem. Arabic-specific manifestations include:

- **Reversed text direction** — some PDF/[OCR](../../ingestion/ocr.md) extraction tools output "ةزاجإلا" instead of "الإجازة" (the characters extracted in the wrong visual order).
- **Letters extracted as separate characters** — "ا ل إ ج ا ز ة" with spaces between every letter.
- **Words run together with no space** — "سياسةالإجازات".
- **Presentation-form glyph mixing** — the same [NFKC](nfkc.md) issue noted in the table above, caused by how the source PDF encoded its glyphs.

**No amount of normalization fixes incorrectly extracted text.** Pull a random sample of extracted chunks and actually read them before doing anything else.

## Implementation: two fields, original and normalized

```python
import re
import unicodedata

DIACRITICS = re.compile(r"[ؐ-ًؚ-ٰٟۖ-ۭ]")
TATWEEL    = "ـ"
INVISIBLE  = re.compile(r"[​-‏‪-‮⁦-⁩﻿]")
DIGITS     = str.maketrans("٠١٢٣٤٥٦٧٨٩۰۱۲۳۴۵۶۷۸۹", "01234567890123456789")

def normalize_ar(text: str,
                 alef=True,
                 alef_maqsura=False,      # off by default: على ≠ علي
                 taa_marbuta=False,       # only enable if evaluation proves it helps
                 ) -> str:
    text = unicodedata.normalize("NFKC", text)    # ﻻ → لا
    text = INVISIBLE.sub("", text)
    text = DIACRITICS.sub("", text)
    text = text.replace(TATWEEL, "")
    text = text.translate(DIGITS)
    if alef:
        text = re.sub("[أإآٱ]", "ا", text)
    if alef_maqsura:
        text = text.replace("ى", "ي")
    if taa_marbuta:
        text = text.replace("ة", "ه")
    text = re.sub(r"\s+", " ", text).strip()
    return text
```

**Index schema:** every chunk is stored in three distinct forms, each serving a different purpose — the same `text_original`/derived-field pattern this handbook uses elsewhere for [metadata stored at indexing time](../vector-database.md#metadata-moves-through-two-separate-phases):

```python
chunk = {
    "id": "doc_42_chunk_3",
    "text_original":   "يحقُّ للموظَّف ٣٠ يومًا إجازة سنوية...",   # for display/citation — never touched
    "text_normalized": normalize_ar(raw_text),                 # for full-text search and embeddings
    "exact_ids":       ["HR-POL-2026-07", "عقد رقم ٤٥٨٢"],      # a keyword field with NO normalization applied
}
```

**The golden rule:** apply the exact same normalization function to the query at search time. If documents are normalized but the query isn't, search quality gets *worse* than doing nothing at all, because now a normalized document term can never match an unnormalized query term.

## Exact-match fields

Contract numbers, product codes, national IDs, and personal names in legal contexts belong in a **separate field with zero normalization applied**. Two concrete reasons:

- Two different families' names might differ by a single letter — normalization could incorrectly merge them.
- A code like `INV-٢٠٢٦-٠٠٤` needs to match exactly, or both its Arabic-digit and Latin-digit forms need to be stored explicitly as two separate values rather than relying on digit unification to bridge them silently.

## Evaluate every query category separately

An overall average hides real problems — overall Recall can rise 3% while a specific category's Recall collapses. Measure each category on its own:

| Category | Example query | What it actually tests |
|---|---|---|
| **Modern Standard Arabic (MSA)** | "ما هي سياسة الإجازات السنوية؟" | The baseline |
| **Dialect** | "وش نظام الإجازات؟" / "ابي اطلب اجازة" | Does the system handle "وش" (what) and "ابي" (I want) as dialectal variants? |
| **Code-switching** | "كيف اسوي reset للباسورد؟" | English words embedded mid-Arabic-sentence, and English words transliterated into Arabic letters |
| **English query → Arabic document** | "What is the annual leave policy?" | Requires a genuinely multilingual embedding model — keyword matching alone can't bridge this at all |

Example comparison report (illustrative numbers):

| Setting | MSA | Dialect | Code-switching | English→Arabic |
|---|---|---|---|---|
| No normalization | 0.71 | 0.48 | 0.52 | 0.61 |
| + diacritics + alef + digits | 0.84 | 0.59 | 0.58 | 0.62 |
| + alef maqsura + taa marbuta | 0.86 | 0.63 | 0.58 | 0.62 |
| + aggressive [stemming](stemming.md) | 0.88 | 0.66 | 0.55 | 0.62 |

**Reading it:** [stemming](stemming.md) raised Recall slightly, but Precision and identifier accuracy must be measured alongside it before adopting it. The English→Arabic category didn't improve under *any* normalization setting, because its bottleneck is the embedding model's cross-lingual capability (see [Embedding Model Selection](../../../../overviews/ai/embedding-model-selection.md)), not the text pipeline.

## Tokenization affects chunk budgets

Language models split text into tokens, and Arabic frequently consumes **more tokens per word** than English does in many tokenizers (see [Tokenization (IR)](text-tokenization.md) for the search-indexing sense of this word, and [LLM Tokenization](../../generation/tokenization.md) for the subword-unit sense that actually drives this cost) — diacritics increase the token count further.

The practical consequence:
- A "500-token" Arabic chunk holds **less actual content** than a 500-token English chunk.
- Chunking by character count instead of actual token count risks silently exceeding the embedding model's limit, truncating text without warning.
- **Fix:** chunk by token count computed with the real tokenizer of the model being used, and review Arabic chunk sizes separately from English ones — see [Chunking Strategies & Libraries](../../../../overviews/ai/chunking-strategies.md).

## Follow-up: should every name be transliterated to Latin script?

**No.** A single name has many valid Latin spellings — محمد → Mohammed / Muhammad / Mohamed / Mohamad — and replacing the original with just one of them loses matches against the others and can introduce new errors.

**The correct approach:** treat transliteration as an **additional retrieval path**, never a replacement:
- Keep the original Arabic name.
- Add a `name_aliases` field containing plausible Latin-script spellings.
- **Measure** whether this path actually raises Recall for English queries about Arabic names, without hurting Precision by introducing false matches.

## The common mistake

**Applying aggressive normalization without checking identifier accuracy.** Concrete failure examples:
- Alef maqsura unification makes "على" (on) equal "علي" (Ali) — a query about an employee named Ali now returns every document containing the preposition "على."
- [Stemming](stemming.md) makes "كاتب" (writer) = "مكتب" (office) = "كتاب" (book).
- Digit unification or symbol stripping can break codes like `HR-POL-07`.

**The guard:** put **identifier- and name-specific questions** into the evaluation set (e.g. "What is the status of contract 4582?"), and confirm every normalization change doesn't break them.

## Spoken interview answer

> "I treat normalization as a measured decision, not a fixed rule list. I start with the safe steps: [NFKC](nfkc.md) normalization, removing diacritics, tatweel, and invisible characters, and unifying alef forms and digits. Riskier steps like alef maqsura unification or stemming I only enable if evaluation actually proves they help. I store the original text for display and citation, the normalized text for indexing, and identifiers in a separate exact-match field with no normalization applied. I apply the exact same function to the query. Then I evaluate MSA, dialects, code-switching, and English queries separately, because the overall average hides real problems."

## Related

- [Text Normalization](text-normalization.md) — the general, non-Arabic-specific version of this stage
- [NFKC](nfkc.md) — why [NFKC](nfkc.md) specifically is what the `normalize_ar()` code above calls, and why NFC alone wouldn't work
- [Unicode Normalization Forms (NFC, NFD, NFKC, NFKD)](unicode-normalization.md) — the overview comparing all four forms
- [Tokenization (IR)](text-tokenization.md)
- [Stemming](stemming.md) — the general mechanics behind the Arabic stemming risk noted above
- [OCR](../../ingestion/ocr.md) — the extraction-quality problem that normalization cannot fix
- [Embedding Model Selection](../../../../overviews/ai/embedding-model-selection.md) — the cross-lingual retrieval gap normalization cannot close
- [Chunking Strategies & Libraries](../../../../overviews/ai/chunking-strategies.md)
- [Retrieval Metrics](../../evaluation/retrieval-metrics.md)
- [RAG Deep Dive — R06](../../../../interview/interview-01/11-rag-deep-dive.md#r06--intermediate--how-would-you-normalize-arabic-text-for-retrieval)
