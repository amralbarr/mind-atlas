# NLI Model (Natural Language Inference)

A **Natural Language Inference (NLI)** model takes two pieces of text — a **premise** and a **hypothesis** — and classifies their relationship into one of three labels:

| Label | Meaning | Example (premise: *"The project budget is SAR 500,000 as of Q3 2024."*) |
|---|---|---|
| **Entailment** | The hypothesis follows from the premise | Hypothesis: *"The budget is SAR 500,000."* |
| **Contradiction** | The hypothesis conflicts with the premise | Hypothesis: *"The budget is SAR 600,000."* |
| **Neutral** | The hypothesis is neither confirmed nor denied by the premise | Hypothesis: *"The budget was increased this year."* |

This is a small, well-defined, 3-class classification task — not open-ended generation — which is exactly what makes NLI models cheap, fast, and deterministic compared to an [LLM](../generation/llm.md)-as-judge doing the same job via a free-text prompt. Architecturally, an NLI model is a [cross-encoder](../retrieval/cross-encoder.md): premise and hypothesis are read together in one forward pass, the same mechanism [cross-encoder re-ranking](../retrieval/cross-encoder-reranking.md) uses for query-document relevance, just fine-tuned for a different output space.

## Why This Matters for RAG: Entailment ≠ Similarity

A common mistake is assuming a high embedding-similarity score between a claim and a retrieved chunk means the chunk *supports* the claim. It doesn't:

```
Chunk:  "The project budget is SAR 500,000."
Claim:  "The project budget is SAR 600,000."

Cosine similarity: high  — both sentences are about "the project budget," same topic/phrasing
NLI verdict: CONTRADICTION — the actual numbers disagree
```

Similarity measures *topical closeness*; NLI measures *logical relationship*. A retriever can correctly find the most similar chunk to a claim and an NLI check can still correctly flag that chunk as contradicting the claim — these are two different, complementary signals, and conflating them is a real production bug, not just an academic distinction.

## NLI as the Lightweight Alternative to LLM-as-Judge

[Claim Verification](claim-verification.md)'s Layer 2 check ("does the cited chunk's text actually support this claim?") needs exactly a premise→hypothesis classification — the chunk is the premise, the claim is the hypothesis. That check can be implemented two ways:

| Approach | How | Trade-off |
|---|---|---|
| **[LLM](../generation/llm.md)-as-judge** | Prompt a general-purpose [LLM](../generation/llm.md) to classify SUPPORTED/UNSUPPORTED/CONTRADICTED | Flexible, handles nuanced/implicit support well, but slower, costs a full model call per claim, and output can vary slightly between runs |
| **Dedicated NLI model** | A small model (e.g. `roberta-large-mnli`, a `deberta-v3`-based NLI checkpoint) fine-tuned specifically on entailment datasets (MNLI, SNLI) | Much faster and cheaper — runs as a local classifier, not an API call — fully deterministic for the same input, but less flexible on claims requiring real-world reasoning beyond pure textual entailment |

```python
from transformers import pipeline

nli = pipeline("text-classification", model="roberta-large-mnli")

def check_claim_supported(claim: str, cited_chunk_text: str) -> bool:
    result = nli(f"{cited_chunk_text} [SEP] {claim}")[0]
    return result["label"] == "ENTAILMENT"
```

A system under real request volume often runs the NLI model as the default per-claim check (cheap enough to run on every answer) and escalates to an [LLM](../generation/llm.md)-as-judge only for borderline or low-confidence NLI scores — the same two-tier pattern [reranking](../retrieval/cross-encoder-reranking.md) uses (a cheap first pass, an expensive second pass only where it's worth the cost).

## Common Questions

**Can an NLI model replace a full [groundedness](groundedness-and-correctness.md) evaluation?**
> It covers the core per-claim entailment check but not the whole picture — groundedness evaluation also needs to split an answer into individual claims first (NLI alone doesn't do sentence segmentation), aggregate per-claim results into one score, and handle claims that combine multiple premises. NLI is the classifier at the center of that pipeline, not the whole pipeline.

**Why not just use keyword/string matching instead of NLI?**
> String matching only catches claims that are near-verbatim copies of the source text. NLI catches paraphrases, numeric restatement, and logical restructuring — "the deadline is in 30 days" entailing "the deadline is next month" — that string matching would incorrectly flag as unsupported.

**Is "neutral" the same as "unsupported" for [claim verification](claim-verification.md) purposes?**
> Functionally yes in most pipelines — both NEUTRAL and CONTRADICTION should block a claim from being treated as verified, since neither confirms the claim is actually backed by the source. The distinction mainly matters for diagnostics: a CONTRADICTION is a much more serious finding (the model stated something the source actively disagrees with) than a NEUTRAL result (the source simply didn't address it), even though both fail the same verification gate.

## Related

- [Claim Verification](claim-verification.md) — the pipeline mechanism this model type implements the per-claim check for
- [Groundedness and Correctness](groundedness-and-correctness.md) — the metric an NLI-based per-claim check ultimately feeds into
- [Embeddings](../ingestion/embeddings.md) / [RAG](../rag/rag.md) — the retrieval step that finds topically similar chunks, which this file distinguishes from logically-entailing chunks
- [Cross-Encoder](../retrieval/cross-encoder.md) — the general architecture an NLI model is one fine-tuned application of
- [Cross-Encoder Reranking](../retrieval/cross-encoder-reranking.md) — the other major [cross-encoder](../retrieval/cross-encoder.md) application: query-document relevance instead of premise-hypothesis entailment
- [LLM Evaluation](llm-evaluation.md) — the [LLM](../generation/llm.md)-as-judge alternative for the same entailment classification task, when flexibility matters more than latency/cost
