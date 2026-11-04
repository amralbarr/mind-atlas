# Lemmatization

Lemmatization reduces a word to its actual dictionary form (its **lemma**) by looking it up against a lexicon — often using the word's part of speech for context — rather than mechanically stripping suffixes the way [stemming](stemming.md) does. It's the slower, more accurate sibling of [stemming](stemming.md) in the [analyzer pipeline](../text-analysis.md).

## How it works

```
"running" → "run"       (verb, present participle → base form)
"better"  → "good"      (irregular comparative → base adjective — a stemmer cannot do this)
"mice"    → "mouse"     (irregular plural → singular — a stemmer cannot do this either)
"saw"     → "see"       (if used as a verb) or "saw"  (if used as a noun — requires POS context)
```

The last example is the key difference from [stemming](stemming.md): lemmatization can require knowing a word's **part of speech** to pick the correct lemma, since the same surface form can map to different base words depending on how it's used in the sentence. This is why a real lemmatizer is a small [NLP](../../nlp.md) pipeline (tokenize → POS-tag → look up lemma), not a single fast rule pass — it's inherently more expensive than [stemming](stemming.md).

## Stemming vs. lemmatization, directly compared

| | [Stemming](stemming.md) | Lemmatization |
|---|---|---|
| **Method** | Rule-based suffix stripping | Dictionary/morphology lookup, often POS-aware |
| **Output** | Not always a real word (`"entitl"`) | Always a real dictionary word |
| **Handles irregular forms** | No (`"better"` stays `"better"`, `"mice"` stays `"mice"`) | Yes |
| **Speed** | Fast — a fixed rule pass | Slower — needs a lexicon, often POS tagging |
| **Dependency** | None beyond the algorithm itself | A language model/lexicon (e.g. WordNet, or a trained pipeline) |

Neither is strictly better — the choice is a direct trade of indexing-time cost against accuracy, and the practical default is to start with the cheaper option ([stemming](stemming.md) or none) and only add lemmatization where measurement on real queries shows it's actually needed. See [Retrieval Metrics](../../evaluation/retrieval-metrics.md) for how to measure that rather than guess.

## Libraries and technologies

| Tool | What it provides |
|---|---|
| **spaCy** | Production-grade lemmatization built into its standard pipeline (`token.lemma_`) — includes POS tagging automatically, so it resolves the `"saw"`-as-verb-vs-noun ambiguity correctly out of the box. This is spaCy's answer to word-form reduction; it does not offer [stemming](stemming.md) at all. |
| **NLTK `WordNetLemmatizer`** | Looks words up against the WordNet lexical database; needs the POS tag passed in explicitly for correct results (it defaults to treating every word as a noun otherwise, which silently produces wrong lemmas for verbs/adjectives) |
| **Stanza** (Stanford [NLP](../../nlp.md)) | Neural pipeline including lemmatization, stronger multilingual support than NLTK's WordNet-based approach |
| **[Elasticsearch](../../../databases/search/elasticsearch.md) / [OpenSearch](../../../databases/search/opensearch.md)** | No true lemmatizer is built in by default — their language analyzers rely on [stemming](stemming.md) (see [Elasticsearch](../../../databases/search/elasticsearch.md), [OpenSearch](../../../databases/search/opensearch.md)); a real lemmatizer would be run as a custom pre-processing step before indexing if the use case specifically needs it |

## Related

- [Stemming](stemming.md) — the faster, rule-based alternative, with a direct comparison
- [Text Analysis Pipeline](../text-analysis.md) — the overview this is a stage of
- [Text Normalization](text-normalization.md) — the stage before this one
- [BM25](../bm25.md) — scores whatever terms lemmatization ultimately produces
