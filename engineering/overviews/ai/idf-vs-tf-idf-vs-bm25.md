# IDF vs. TF-IDF vs. BM25

These three aren't three separate algorithms — they're a **gradual evolution**, each one building directly on the one before it:

```
IDF          ← one component: "how rare is this word?"
  ↓
TF-IDF       ← IDF × how often the word appears
  ↓
BM25         ← TF-IDF + saturation on repetition + a length penalty
```

## At a glance

| | **[IDF](../../concepts/ai/retrieval/idf.md)** | **[TF-IDF](../../concepts/ai/retrieval/tf-idf.md)** | **[BM25](../../concepts/ai/retrieval/bm25.md)** |
|---|---|---|---|
| **What is it?** | A component (part of a formula) | A scoring function | A scoring function |
| **Measures** | How rare a word is across the whole corpus | Rarity × frequency in a document | Rarity × *saturated* frequency, adjusted for length |
| **Depends on the document?** | ❌ No — one fixed value per word, corpus-wide | ✅ Yes | ✅ Yes |
| **Effect of repetition** | Doesn't care | **Linear**: 10 occurrences = 10× | **Diminishing**: has a ceiling |
| **Effect of document length** | Doesn't care | Not built into the base formula | **Built in**, via the `b` parameter |
| **Tunable parameters** | None | None | `k1` and `b` |
| **Resistance to keyword stuffing** | — | ❌ Weak | ✅ Strong |

---

## 1. IDF: word rarity, and nothing else

```
IDF(word) = log( N / n )
```
- `N` = total number of documents
- `n` = number of documents containing the word

**One fixed value per word** across the whole corpus — it never changes from one document to the next. "the" scores close to zero; "maternity" scores high.

On its own, **it isn't enough to rank anything** — it knows how important a word is, but nothing about the document itself.

## 2. TF-IDF: rarity × repetition

```
TF-IDF(word, doc) = TF × IDF
```
- `TF` = how many times the word appears in this document

The idea: a word matters to a document if it **repeats in it** (high TF) **and is rare elsewhere** (high [IDF](../../concepts/ai/retrieval/idf.md)).

**The problem:** the relationship is **linear**. 10 occurrences means 10× the score, and a long document racks up more occurrences purely by chance.

## 3. BM25: fixing TF-IDF

It keeps the same TF × [IDF](../../concepts/ai/retrieval/idf.md) idea, but adds:
- **Saturation (`k1`):** the first occurrence matters most; every one after that adds diminishing value.
- **Length penalty (`b`):** appearing in a short document counts for more than the same appearance in a long one.

---

## Example: same documents, three scoring methods

1,000 documents, average length 100 words, query: **"maternity leave"**.

| Word | Appears in | [IDF](../../concepts/ai/retrieval/idf.md) |
|---|---|---|
| leave | 200 documents | ln(1000/200) = **1.61** |
| maternity | 10 documents | ln(1000/10) = **4.61** |

| Document | Length | "leave" | "maternity" |
|---|---|---|---|
| **A** | 50 | 1 | 1 |
| **B** | 400 | 5 | 1 |
| **C** | 100 | 10 | 0 |

**The logically best match is A** — short, and specifically about maternity leave. C doesn't mention "maternity" at all.

### By IDF alone (sum of the IDF of the words present)

| Document | Calculation | Score |
|---|---|---|
| A | 1.61 + 4.61 | **6.22** |
| B | 1.61 + 4.61 | **6.22** |
| C | 1.61 | **1.61** |

❌ **Can't tell A and B apart** — both contain the same two words, and that's all [IDF](../../concepts/ai/retrieval/idf.md) alone knows.

### By plain TF-IDF

| Document | Calculation | Score |
|---|---|---|
| A | 1×1.61 + 1×4.61 | **6.22** 🥉 |
| B | 5×1.61 + 1×4.61 | **12.66** 🥈 |
| C | 10×1.61 + 0 | **16.10** 🥇 |

❌ **The ranking is completely backwards.** C wins despite never mentioning "maternity" at all, purely because it repeats "leave" 10 times. Linear repetition overpowered the rare word.

### By BM25 (`k1 = 1.2`, `b = 0.75`, `avgdl = 100`)

| Document | Score |
|---|---|
| A | **7.75** 🥇 |
| B | **4.03** 🥈 |
| C | **3.16** 🥉 |

✅ **The correct ranking.** Saturation stopped C from winning on repetition alone, and the length penalty brought B down.

### Visual summary

| | 1st place | 2nd place | 3rd place |
|---|---|---|---|
| [IDF](../../concepts/ai/retrieval/idf.md) alone | A = B (tie) | | C |
| [TF-IDF](../../concepts/ai/retrieval/tf-idf.md) | C ❌ | B | A |
| **[BM25](../../concepts/ai/retrieval/bm25.md)** | **A ✅** | B | C |

---

## In fairness to TF-IDF

In practice, raw [TF-IDF](../../concepts/ai/retrieval/tf-idf.md) is rarely used in its bare form. Common improvements:
- **Sublinear TF:** use `1 + log(TF)` instead of the raw count — this produces a form of saturation on its own.
- **Length normalization:** divide the vector by its length (cosine normalization).

With these improvements, [TF-IDF](../../concepts/ai/retrieval/tf-idf.md) gets close to [BM25](../../concepts/ai/retrieval/bm25.md) — but [BM25](../../concepts/ai/retrieval/bm25.md) combines both into one formula **with tunable parameters**, and has been empirically shown to perform better on real search tasks.

---

## Where each one is actually used today

| | Common use |
|---|---|
| **[IDF](../../concepts/ai/retrieval/idf.md)** | A component inside both [TF-IDF](../../concepts/ai/retrieval/tf-idf.md) and [BM25](../../concepts/ai/retrieval/bm25.md); also used to identify common, low-value words (stop words), or to weight terms in other techniques |
| **[TF-IDF](../../concepts/ai/retrieval/tf-idf.md)** | Turning text into **features** for classical machine learning models (e.g. scikit-learn's `TfidfVectorizer`), keyword extraction, text classification |
| **[BM25](../../concepts/ai/retrieval/bm25.md)** | **Search engines** — the default in [Elasticsearch](../../concepts/databases/search/elasticsearch.md), [OpenSearch](../../concepts/databases/search/opensearch.md), [Solr](../../concepts/databases/search/solr.md), and [Azure AI Search](../../concepts/cloud/azure/azure-ai-search.md). [Lucene](../../concepts/databases/search/lucene.md) itself used [TF-IDF](../../concepts/ai/retrieval/tf-idf.md) as its default before switching to [BM25](../../concepts/ai/retrieval/bm25.md) (in [Elasticsearch](../../concepts/databases/search/elasticsearch.md), this happened with version 5.0) |

---

## The one-line summary

**IDF** says "this word matters." **TF-IDF** adds "and it repeated a lot in this document." **BM25** corrects that with "but repetition has a ceiling, and a long document doesn't get rewarded just for being long."

## Related

- [IDF](../../concepts/ai/retrieval/idf.md)
- [TF-IDF](../../concepts/ai/retrieval/tf-idf.md)
- [BM25](../../concepts/ai/retrieval/bm25.md)
- [BM25 vs. Hybrid Search vs. RRF](bm25-vs-hybrid-search-vs-rrf.md) — the next layer up: how BM25 itself fits into a hybrid retrieval pipeline
- [Inverted Index](../../concepts/ai/retrieval/inverted-index.md) — the structure all three are scored against
- [Stopword Removal](../../concepts/ai/retrieval/analyzer-pipeline/stopword-removal.md) — why IDF already does most of what [stopword removal](../../concepts/ai/retrieval/analyzer-pipeline/stopword-removal.md) does, for relevance purposes
