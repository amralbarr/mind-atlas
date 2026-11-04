# Cross-Encoder

A **cross-encoder** encodes two inputs **together**, in a single forward pass — concatenating or pairing them so the model can attend directly between every token of the first input and every token of the second — and outputs a single score or classification for the pair, rather than two separate vectors to compare afterward.

```
[Input A + Input B] → model (joint attention across both) → one score/label
```

This is the architectural counterpart to the [bi-encoder](bi-encoder.md), which encodes the two inputs **independently** and compares the resulting vectors afterward. See [Bi-Encoder vs. Cross-Encoder](../../../overviews/ai/bi-encoder-vs-cross-encoder.md) for the full side-by-side comparison and a worked example of what a cross-encoder catches that a [bi-encoder](bi-encoder.md) misses.

## Why It's More Accurate — and Why It's Slower

Letting the model see both inputs together, token-by-token, recovers relevance/relationship signals that are invisible when the two sides are encoded separately and compressed into fixed vectors first — a cross-encoder can notice that a specific phrase in one input directly answers or contradicts a specific clause in the other, not just that the two are generally on the same topic. The cost of that joint attention is that **nothing about a cross-encoder's output can be precomputed per-input ahead of time**: the model needs both specific inputs present together before it can produce anything, so scoring N pairs always costs N full forward passes.

```
Scoring 1 query against 1,000,000 documents:
  Bi-encoder:              1 forward pass  (query only — documents were embedded once, ahead of time)
  Cross-encoder (full):    1,000,000 forward passes  ❌ not practical
  Cross-encoder (top-20):  20 forward passes  ✅ affordable
```

This is why a cross-encoder is always run on an already-narrowed candidate set, never as the first pass over a full corpus — see [Cross-Encoder Re-Ranking](cross-encoder-reranking.md) for the full cost table and the retrieve-then-rerank pipeline this makes necessary.

## Not Just Reranking — Two Distinct Applications in This Handbook

"Cross-encoder" is often introduced purely as "the [re-ranker](cross-encoder-reranking.md) model," but that names one *application* of the architecture, not the architecture itself. The same joint-attention, single-score pattern underlies two genuinely different tasks covered elsewhere in this handbook:

| Application | Input pair | Output |
|---|---|---|
| **[Re-ranking](cross-encoder-reranking.md)** | A query and a candidate document | A relevance score — how well this document answers this query |
| **[NLI / entailment classification](../evaluation/nli-model.md)** | A premise and a hypothesis | A 3-class label — ENTAILMENT, CONTRADICTION, or NEUTRAL |

Both are the identical underlying mechanism — a BERT-style (or similar) model reading a concatenated pair and producing one output from that joint representation — fine-tuned on different training data for different output spaces. Recognizing this is what lets [claim verification](../evaluation/claim-verification.md) reuse "a cross-encoder" as the shared technique for both candidate reranking and claim-to-evidence entailment checking, rather than treating them as unrelated tools.

## Common Questions

**Is `sentence-transformers`' `CrossEncoder` class the only way to run one?**
> It's the standard open-source entry point, but any model that takes a concatenated pair as input and produces one output — including a plain fine-tuned BERT/RoBERTa/DeBERTa classification head — is architecturally a cross-encoder, whether or not it's loaded through that specific library class.

**Can a cross-encoder be used for retrieval directly, skipping the bi-encoder stage entirely?**
> Only at a scale small enough to score every candidate — a few dozen to low hundreds of documents, depending on latency budget. Past that, a [bi-encoder](bi-encoder.md) first pass is required to narrow the field down to something a cross-encoder can afford to fully score.

## Related

- [Bi-Encoder](bi-encoder.md) — the architectural counterpart that encodes inputs independently instead of jointly
- [Bi-Encoder vs. Cross-Encoder](../../../overviews/ai/bi-encoder-vs-cross-encoder.md) — the full comparison and worked relevance example
- [Cross-Encoder Re-Ranking](cross-encoder-reranking.md) — the retrieval application: scoring query-document relevance on a narrowed candidate set
- [NLI Model](../evaluation/nli-model.md) — the entailment-classification application: scoring premise-hypothesis logical relationship
- [Claim Verification](../evaluation/claim-verification.md) — where both applications combine in one pipeline
- [Vector Database](vector-database.md) — the bi-encoder-built index a cross-encoder's input candidate set is drawn from
