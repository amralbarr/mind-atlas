# RAGAS

RAGAS ([Retrieval-Augmented Generation](../rag/rag.md) Assessment) is a popular open-source Python library for scoring [RAG](../rag/rag.md) pipeline quality — it implements the standard [RAG](../rag/rag.md) evaluation metrics as ready-to-run [LLM](../generation/llm.md)-as-judge checks, instead of every team hand-rolling their own groundedness/relevance scoring prompts from scratch. It's a library and methodology, not a hosted service — it runs against your own evaluation set and your own [LLM](../generation/llm.md) judge of choice.

## What it measures

A [RAG](../rag/rag.md) pipeline has four distinct elements in play on any given query: the **question** (`user_input`), the **retrieved chunks** (`retrieved_contexts`), the **generated answer** (`response`), and a human-written **reference** answer (`ground truth`, when one exists). Each of RAGAS's four core metrics checks the relationship between a different pair of these four:

- **Context Recall**: chunks ↔ reference — did retrieval surface everything needed to answer completely?
- **Context Precision**: chunks ↔ question/reference — are the useful chunks at the top, not buried in noise?
- **Faithfulness**: answer ↔ chunks — did the model stick to what was retrieved, or invent things?
- **Answer Relevancy**: answer ↔ question — does the answer actually address what was asked?

Two metrics evaluate retrieval, two evaluate generation — which is exactly what makes the four of them useful together for pinpointing *where* a [RAG](../rag/rag.md) failure actually lives, not just that one exists (see [Reading the four scores together](#reading-the-four-scores-together) below).

RAGAS's metrics map directly onto the evaluation dimensions this handbook defines independently of any specific library:

| RAGAS metric          | What it checks                                                                     | Maps to                                         |
| ---------------------- | ----------------------------------------------------------------------------------- | ------------------------------------------------ |
| **Faithfulness**      | Are the claims in the answer actually supported by the retrieved context?          | [Groundedness](groundedness-and-correctness.md) |
| **Answer Relevancy**  | Does the answer actually address the question asked?                               | [Relevance](groundedness-and-correctness.md)    |
| **Context Precision** | Of the retrieved chunks, how many were actually relevant and ranked appropriately? | [Precision@k](retrieval-metrics.md)             |
| **Context Recall**    | Did retrieval surface the chunks actually needed to answer the question?           | [Recall@k](retrieval-metrics.md)                |

This is deliberate naming convergence rather than coincidence — RAGAS's "faithfulness" and "answer relevancy" (RAGAS's current docs also call the underlying metric class `ResponseRelevancy`; both names refer to the same computation) are implementations of the same groundedness/relevance concepts described generically in [Groundedness and Correctness](groundedness-and-correctness.md); RAGAS just gives them a concrete, runnable scoring implementation.

## A worked example, scored on all four metrics

**Question:** "How many days is annual leave, and what is the eligibility requirement?"
**Reference** (ground truth, human-written): "30 paid days, provided the employee has completed 12 months of service."
**Retrieved chunks** (k=4, in rank order):

1. "Working hours are 8am to 4pm" — not useful
2. "Employees are entitled to 30 paid days of annual leave" — useful
3. "Sick leave requires a medical report" — not useful
4. "Leave requests must be submitted 14 days in advance" — not useful

Note: the chunk stating the 12-month eligibility requirement was **never retrieved at all**.

**Actual generated answer:** "Employees are entitled to 30 paid days, and up to 10 days can be carried over to the next year." (The "10 days carried over" detail is a fabricated claim — it isn't stated in any retrieved chunk.)

The four subsections below score this exact example on each metric.

### Context Recall — did everything needed get retrieved?

**How it's computed:** the judge [LLM](../generation/llm.md) decomposes the **reference** answer into individual claims, then checks whether each claim is supported by/present in the retrieved chunks.

**On the example:** reference claims = `["30 days", "paid", "12-month eligibility requirement"]`. Found in the retrieved chunks: "30 days" ✅ (chunk 2), "paid" ✅ (chunk 2), "12-month eligibility requirement" ❌ (never retrieved).

```
Context Recall = 2/3 ≈ 0.67
```

**Low score means:** information genuinely needed for a complete answer was never retrieved — no generation model, however good, can compensate for this.

**Blind spot:** Context Recall only cares *whether* each needed fact showed up somewhere in the retrieved set, never *where* — a chunk at rank 1 and a chunk at rank 4 count identically. This is the [LLM](../generation/llm.md)-judged equivalent of classical [Recall@k](retrieval-metrics.md#recallk): instead of matching chunk IDs against a reference list of relevant IDs, it compares actual content via an [LLM](../generation/llm.md) judge, which is what lets it work even when no fixed relevant-chunk-ID list exists — only a reference answer.

### Context Precision — are the useful chunks at the top?

**How it's computed:** the judge [LLM](../generation/llm.md) rates each retrieved chunk as relevant or not (RAGAS has both a reference-based variant, judging against the reference answer, and a response-based variant, judging against the generated answer — either way the mechanic below is the same), then computes an Average-Precision-style score: for every rank position holding a relevant chunk, compute Precision@k at that position, then average across only the relevant positions.

**On the example:** the single useful chunk sits at position 2. Precision@2 = 1/2 = 0.5. With exactly one relevant chunk overall, Context Precision = 0.5 ÷ 1 = **0.50**.

```
Context Precision = 0.50
```

If that same useful chunk had landed at position 1 instead of 2, the score would be 1.0 instead of 0.5 — this metric is just as rank-sensitive as [MRR](mrr.md).

**Low score means:** useful chunks are buried under noise (irrelevant results ranked above them). Usual fix: [cross-encoder re-ranking](../retrieval/cross-encoder-reranking.md) or metadata filtering, not a different retriever entirely.

**Blind spot:** Context Precision says nothing about whether the retrieved set is *complete* — a pipeline that retrieves one perfect chunk at rank 1 and nothing else can score a perfect 1.0 while still missing other information the question needed (that's Context Recall's job, not this one).

### Faithfulness — did the model stick to the retrieved chunks?

**How it's computed:** the judge [LLM](../generation/llm.md) decomposes the **generated answer** (not the reference) into individual claims, then verifies whether each claim can be inferred from the retrieved chunks (not from the reference, not from the model's general training knowledge).

**On the example:** answer claims = `["30 days" ✅ supported by chunk 2, "paid" ✅ supported by chunk 2, "can carry over 10 days" ❌ unsupported by any retrieved chunk — this is a fabrication]`.

```
Faithfulness = 2/3 ≈ 0.67
```

**Low score means:** the model is hallucinating, or filling gaps with general knowledge instead of relying strictly on retrieved context. Usual fixes: [prompt engineering](../generation/prompt-engineering.md) (explicit instructions like "answer only from the provided context, and say you don't know if the information isn't there"), lowering temperature, or swapping models.

**Blind spot:** Faithfulness never checks whether a *supported* claim is actually true — it only checks whether the claim can be traced back to the retrieved text. If the retrieved chunk itself is stale or wrong, a faithful answer that repeats it scores high while still being factually incorrect (see the Groundedness-vs-Correctness distinction in [Groundedness and Correctness](groundedness-and-correctness.md)). A maximally safe "I don't know" also scores a perfect 1.0 — it contradicts nothing — while being useless.

**The key distinction from Context Recall:** Context Recall decomposes the *reference* and checks its coverage in the retrieved chunks — it tests whether retrieval was adequate. Faithfulness decomposes the *actual answer* and checks its support in the retrieved chunks — it tests whether generation was honest. Retrieval can be excellent (high Context Recall) while the model hallucinates anyway (low Faithfulness), and the reverse is equally possible.

### Answer Relevancy — does the answer address the question actually asked?

**How it's computed** (and why this is the one metric of the four that specifically needs an embedding model): (1) the judge [LLM](../generation/llm.md) reads **only the generated answer** — not the original question — and generates several synthetic questions that the answer is presumed to be answering; (2) those generated questions and the real original question are all converted to embedding vectors; (3) the metric computes the average cosine similarity between the original question's embedding and each generated question's embedding.

```
Answer Relevancy = (1/N) * Σ cosine_similarity(embed(original_question), embed(generated_question_i))
```

**On the example:** from the answer "Employees are entitled to 30 paid days, and up to 10 days can be carried over to the next year," the judge might generate questions like "How many days is annual leave?" (very close to the real question), "Can leave days be carried over?" (far from the real question — never asked), and "Is annual leave paid?" (partially close). Compared against the actual question ("How many days is annual leave, and what is the eligibility requirement?"), the average gives an illustrative score of roughly:

```
Answer Relevancy ≈ 0.7
```

**Core idea:** if an answer genuinely and precisely addresses the question asked, the questions "inferred" from reading the answer alone will closely resemble the real question. The further an answer drifts — ignoring part of the question, answering something different, or padding in unrequested information — the further the inferred questions drift from the original too.

**Low score means:** the answer is off-topic, ignores part of a multi-part question (here: it drops the eligibility requirement that was explicitly asked about), or adds information nobody asked for (here: the "carry-over" detail).

**Blind spot — the important one to flag explicitly:** Answer Relevancy **never checks factual correctness** — only how closely the answer's apparent topic and coverage match the question's. A confidently, completely wrong answer that still stays squarely on-topic can score very high on Answer Relevancy despite being entirely false. Verifying truth is Faithfulness's job (against the retrieved context) or Correctness's job (against ground truth) — not this metric's.

## Reading the four scores together

The real value of running all four together is that the *pattern* across them tells you where in the pipeline to look, which no single metric can do alone:

| Pattern | Diagnosis | Where to fix it |
| --- | --- | --- |
| Recall low | Needed information was never retrieved at all | Chunking strategy, embedding model, [hybrid search](../retrieval/hybrid-search.md), retrieved `k` — not generation |
| Recall high, Precision low | Needed information is retrieved but buried under noisier results ranked above it | [Cross-encoder re-ranking](../retrieval/cross-encoder-reranking.md), metadata filters, or [MMR](../retrieval/mmr.md) for diversity |
| Recall high, Faithfulness low | Retrieval is good and sufficient, but the generator hallucinates despite having the right information in front of it | Prompt, model choice, temperature — not retrieval |
| Faithfulness high, Relevancy low | The model is honest about what it says (no hallucination) but isn't actually answering the question asked | Prompt — explicitly require the answer to address every specific part of the question |
| Recall low, Faithfulness high | The model is honest about the (incomplete) information it had, but what it had was incomplete from the start | The problem is retrieval exclusively — don't swap the generation model to fix it |
| All four high | The system performs well on this case | Still spot-check a sample with a human reviewer — a lenient or systematically biased judge [LLM](../generation/llm.md) can inflate all four at once |

**The most important lesson this table encodes:** don't try to fix or tune the generation stage before first confirming Context Recall is good and sufficient. If the correct information never reached the model in the first place, even the best generation model that exists cannot produce a correct, complete answer.

## Comparing the four metrics

| Dimension | Context Recall | Context Precision | Faithfulness | Answer Relevancy |
| --- | --- | --- | --- | --- |
| Stage evaluated | Retrieval | Retrieval | Generation | Generation |
| Needs a human-written reference? | Yes | Reference-based variant does; a response-based variant exists that doesn't | No | No |
| Needs an embedding model specifically? | No — [LLM](../generation/llm.md)-as-judge only | No — [LLM](../generation/llm.md)-as-judge only | No — [LLM](../generation/llm.md)-as-judge only | **Yes** — the only one of the four |
| What gets decomposed into claims | The reference answer | Nothing — chunks are judged relevant/not as whole units | The generated answer | Nothing — generates reverse questions instead of claims |
| Sensitive to ranking/order | No | Yes | No | No |
| Resembles which classical metric | [Recall@k](retrieval-metrics.md#recallk), LLM-judged instead of ID-matched | [Average Precision](retrieval-metrics.md#precisionk), with ranking sensitivity like [MRR](mrr.md) | [Groundedness](groundedness-and-correctness.md) | [Relevance](groundedness-and-correctness.md) |
| What it detects | Necessary information missing from retrieval entirely | Useful chunks buried under noise | Hallucination / unsupported claims in the answer | Off-topic or incomplete answers relative to the question |
| Blind spot | Doesn't care about rank/order among what *was* retrieved | Doesn't check whether retrieval is complete, only the ranking of what's already relevant | Doesn't check whether a supported claim is actually *true* — a faithful answer can still be wrong if the source chunk is wrong | Never checks factual correctness — a confidently wrong but on-topic answer scores high |

## How it actually scores

All four metrics above are computed by an [LLM-as-judge](llm-evaluation.md) — a secondary LLM call given some combination of the question, retrieved context, generated answer, and reference, asked to produce a structured judgment (claim lists, relevance labels, or synthetic questions, depending on the metric), which RAGAS then aggregates into the numeric scores shown above. Because the judge is itself an LLM, RAGAS scores inherit the same limitation every LLM-as-judge approach has: strong but imperfect correlation with human judgment, and a tendency to under-catch subtle factual errors — which is why this handbook's own evaluation guidance (see [LLM Evaluation](llm-evaluation.md)) always calibrates automated scoring against a human-reviewed sample rather than trusting it as ground truth on its own.

## Where it fits in a pre-launch evaluation pipeline

RAGAS is typically run as the continuous, cheap scoring layer across a full [fixed evaluation dataset](fixed-evaluation-dataset.md) — every prompt change, model swap, or chunking-strategy change gets re-scored across the whole set — with a 5-10% sample routed to human review as the calibration check on top, the same hybrid pattern described in [LLM Evaluation](llm-evaluation.md). It's one option among several comparable frameworks (TruLens, DeepEval are the other commonly cited ones); the handbook doesn't treat any one as uniquely correct — pick based on what integrates cleanly with the rest of the pipeline.

## Related

- [Groundedness and Correctness](groundedness-and-correctness.md) — the concepts RAGAS's "faithfulness"/"answer relevancy" metrics implement
- [Retrieval Metrics](retrieval-metrics.md) — Recall@k/Precision@k, which RAGAS's context metrics mirror
- [MRR](mrr.md) — the classical ranking-sensitivity metric Context Precision's behavior most resembles
- [LLM Evaluation](llm-evaluation.md) — the LLM-as-judge methodology RAGAS is built on, and why human calibration still matters
- [Fixed Evaluation Dataset](fixed-evaluation-dataset.md) — what RAGAS is run against
- [Cross-Encoder Re-Ranking](../retrieval/cross-encoder-reranking.md) — the usual fix when Context Precision is low but Context Recall is fine
