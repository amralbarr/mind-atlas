# Bi-Encoder

A **bi-encoder** (also called a **dual encoder** or **two-tower model**) encodes two inputs — typically a query and a document — **independently**, each through its own forward pass into a fixed-size vector, with no visibility into the other input. The two vectors are then compared with a cheap similarity function, almost always cosine similarity or dot product.

```
Query    → encoder → query vector    ─┐
                                        ├─► cosine similarity → 0.82
Document → encoder → document vector ─┘
           (each one encoded completely independently)
```

## This Is What an Embedding Model *Is*

A bi-encoder is the architecture behind every [embedding](../ingestion/embeddings.md) model used for semantic search — "bi-encoder" is the architectural name; "embedding model" is the product/role name for the same thing. The query and document sides can even share the same underlying encoder (a *symmetric* bi-encoder, common for search) or use two distinct encoders trained together (an *asymmetric* bi-encoder — e.g. a short-query tower and a longer-document tower trained for that specific length mismatch).

## Why It's Fast: Precomputable Vectors

The defining practical consequence of encoding independently is that document vectors can be computed **once, ahead of time**, completely decoupled from any future query:

```
Ingestion time:  embed every document  →  store vectors in a vector index
Query time:      embed only the query  →  compare against millions of precomputed vectors
```

This is the entire reason a [vector database](vector-database.md) and [ANN search](approximate-nearest-neighbor.md) are possible at the scale they operate at — a bi-encoder is what makes "search a million documents in milliseconds" tractable in the first place. A [cross-encoder](cross-encoder.md) cannot do this: it needs the query and a specific document together before it can produce a score, so nothing about it can be precomputed per-document.

## The Trade-off: No Direct Interaction

Because the two texts are never compared token-by-token — only as two already-compressed, independent vectors — a bi-encoder structurally cannot tell "this document mentions the same topic" apart from "this document actually answers the specific question asked." See [Bi-Encoder vs. Cross-Encoder](../../../overviews/ai/bi-encoder-vs-cross-encoder.md) for a fully worked example of exactly this failure mode, and why the standard fix is layering a [cross-encoder](cross-encoder.md) re-ranking pass on top of bi-encoder retrieval rather than trying to fix it within the bi-encoder itself.

## Where Else Bi-Encoders Show Up

The same two-tower pattern appears well beyond text search:

- **Recommendation systems** — a "user tower" and an "item tower," trained so a user's vector lands close to items they'd engage with
- **Image-text alignment** (e.g. CLIP) — an image tower and a text tower trained so matching image/caption pairs land close together, enabling text-to-image search
- **Face recognition** — comparing a face embedding against a database of known face [embeddings](../ingestion/embeddings.md), computed once per enrolled face

In every case, the shared idea is the same: whatever needs to be searched at scale gets encoded once, ahead of time, so the only per-query cost is encoding the query itself.

## Common Questions

**If a bi-encoder is "worse" at relevance, why not just always use a [cross-encoder](cross-encoder.md)?**
> Compute cost scales with the number of documents being scored, not just the query — a [cross-encoder](cross-encoder.md) would need one full model forward pass *per candidate document*, which is intractable over a million-document corpus. A bi-encoder's precomputed vectors are what make the first retrieval pass affordable at all; see [Cross-Encoder](cross-encoder.md) for the cost comparison in full.

**Can the same bi-encoder be reused for a completely different corpus without retraining?**
> Generally yes for the architecture, but quality depends on how close the new corpus is to what the model was trained on — a bi-encoder trained on general web text may underperform on narrow technical or legal language compared to one fine-tuned for that domain. The encoder itself doesn't need per-corpus retraining to function; it just may not be optimally tuned for it.

## Related

- [Cross-Encoder](cross-encoder.md) — the architectural counterpart that reads both inputs jointly instead of separately
- [Bi-Encoder vs. Cross-Encoder](../../../overviews/ai/bi-encoder-vs-cross-encoder.md) — the full comparison, including a worked example of what a bi-encoder misses
- [Embeddings](../ingestion/embeddings.md) — the practical, product-level name for what a bi-encoder produces
- [Vector Database](vector-database.md) — what bi-encoder-precomputed vectors make possible at scale
- [Approximate Nearest Neighbor Search (ANN)](approximate-nearest-neighbor.md) — the search structure built on top of bi-encoder vectors
