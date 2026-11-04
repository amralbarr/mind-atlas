# Groundedness and Correctness

Two distinct quality dimensions for AI-generated answers. They are often conflated but measure completely different failure modes.

- **Groundedness** — is every claim in the answer supported by the retrieved evidence?
- **Correctness** — is the answer actually true?

An answer can be grounded but wrong. An answer can be correct but ungrounded. Both matter, and they require different evaluation strategies.

---

## The Core Distinction

```
Retrieved context:
  "The project budget is SAR 500,000 as of Q3 2024."

Answer A: "The project budget is SAR 500,000."
  → Grounded: YES  (directly stated in context)
  → Correct: YES   (matches ground truth)

Answer B: "The project budget is SAR 600,000."
  → Grounded: NO   (contradicts retrieved context — hallucination)
  → Correct: NO    (wrong value)

Answer C: "The project budget is SAR 500,000, which was increased from SAR 400,000 last year."
  → Grounded: NO   (second claim not in retrieved context — fabrication)
  → Correct: UNKNOWN (context doesn't say what the previous budget was)
```

Answer C is the dangerous failure mode: the first clause is correct and grounded, but the model adds an extra claim that has no support in the retrieved evidence. Users trust the whole answer because the first part sounds authoritative.

---

## Groundedness

Groundedness asks: "Could a reader verify every claim by looking only at the retrieved documents?"

A grounded answer:
- Uses only information present in the context
- Does not extend, infer, or extrapolate beyond what is stated
- Does not add external knowledge the model has from training
- Either answers from context or explicitly abstains

An ungrounded answer (hallucination) invents plausible-sounding information not supported by the source documents.

### Measuring Groundedness

```python
# Conceptual evaluation prompt (used by LLM-as-judge):
"""
Context: {retrieved_passages}
Answer: {model_answer}

For each factual claim in the answer, identify whether it is:
- SUPPORTED: directly stated or clearly implied by the context
- UNSUPPORTED: not present in the context
- CONTRADICTED: contradicts the context

Groundedness score = SUPPORTED_claims / TOTAL_claims
"""
```

A groundedness score below 0.9 in a production [RAG](../rag/rag.md) system typically warrants investigation — it means 1 in 10 claims the model makes isn't supported by what was retrieved.

---

## Correctness

Correctness asks: "Is the answer actually true, independent of what was retrieved?"

This requires a ground-truth answer to compare against — either a human-verified reference answer or a known fact.

Correctness can fail two ways:
1. The retrieved context was wrong (knowledge base has stale or incorrect data)
2. The model correctly retrieved the right context but still generated a wrong answer

For enterprise knowledge bases, (1) is more common — a policy document gets updated but the old version stays in the index.

### Measuring Correctness

Correctness evaluation requires a [fixed evaluation dataset](fixed-evaluation-dataset.md) with known ground truth:

```python
evaluation_set = [
    {
        "question": "What is the capital expenditure approval threshold?",
        "ground_truth": "SAR 250,000",  # verified correct answer
    },
    ...
]

for item in evaluation_set:
    answer = rag_pipeline.query(item["question"])
    score = evaluate_correctness(answer, item["ground_truth"])
```

Automated correctness scoring uses:
- **Exact match** — for numeric facts, codes, dates
- **F1 token overlap** — for prose answers (common in QA benchmarks)
- **[LLM](../generation/llm.md)-as-judge** — semantic similarity scored by a separate [LLM](../generation/llm.md) ("does this answer say the same thing as the reference answer?")

---

## Groundedness vs Relevance vs Faithfulness

These three terms are used interchangeably in many papers and tools — they mean slightly different things:

| Metric | Question it asks |
|---|---|
| **Groundedness** | Are all claims supported by the retrieved context? |
| **Faithfulness** | Does the answer avoid contradicting the retrieved context? (no hallucinations) |
| **Relevance** | Does the answer address what the user actually asked? |
| **Correctness** | Is the answer factually true? (needs ground truth) |

Faithfulness and groundedness are closely related — faithfulness is the absence of contradiction, groundedness is the presence of support. A maximally safe answer like "I don't know" is faithful (it contradicts nothing) but contributes zero groundedness.

In practice: [RAGAS](ragas.md) (a popular [RAG](../rag/rag.md) evaluation library) uses "faithfulness" for what this document calls groundedness.

---

## Relevance

An answer can be grounded and correct but not relevant:

```
Question: "What is the document approval process?"

Answer: "The approval threshold is SAR 250,000."
  → Grounded: YES  (in the context)
  → Correct: YES   (true fact)
  → Relevant: NO   (doesn't answer the question about the process)
```

Relevance is evaluated by checking whether the answer addresses the specific question asked. In [RAGAS](ragas.md), this is "answer relevance."

---

## The Failure Matrix

| Grounded | Correct | Relevant | Failure type |
|---|---|---|---|
| YES | YES | YES | No failure — ideal answer |
| NO | YES | YES | Correct but unsupported — model used training knowledge instead of context |
| YES | NO | YES | Knowledge base has wrong information |
| YES | YES | NO | Answer is accurate but off-topic |
| NO | NO | YES | Hallucination |
| YES | NO | NO | Wrong and off-topic |

The most dangerous quadrant is **grounded:NO, correct:YES** — the answer happens to be right, but it came from model training, not from the retrieved documents. In a regulated environment, this is still a compliance failure because the answer is unverifiable from the system's own sources.

---

## In Production Systems

In a production [RAG](../rag/rag.md) system, track groundedness per query as an ongoing metric:

```python
# After each response, log a groundedness check
result = {
    "query_id": query_id,
    "answer": answer,
    "groundedness_score": evaluate_groundedness(answer, retrieved_context),
    "relevance_score": evaluate_relevance(question, answer),
}

# Alert if groundedness drops below threshold
if result["groundedness_score"] < 0.85:
    alert("Groundedness regression detected")
```

A spike in low groundedness scores signals:
- The retrieval step is returning irrelevant context
- The model prompt isn't instructing the model to stay grounded
- A model version update changed the model's behavior

---

## Related

- [LLM Evaluation](llm-evaluation.md) — the full metric landscape: Recall@k, [MRR](mrr.md), groundedness, abstention rate
- [Claim Verification](claim-verification.md) — the request-time mechanism that *enforces* groundedness per answer, as opposed to this file's offline/aggregate scoring of it
- [NLI Model](nli-model.md) — a lightweight classifier implementing the same SUPPORTED/UNSUPPORTED/CONTRADICTED judgment this file's groundedness scoring uses
- [RAGAS](ragas.md) — the library that implements "faithfulness"/"answer relevance" as runnable scores
- [RAG](../rag/rag.md) — the [retrieval-augmented generation](../rag/rag.md) architecture this metric applies to
- [Fixed Evaluation Dataset](fixed-evaluation-dataset.md) — building the ground-truth test set used to measure correctness
- [Structured Output](../generation/structured-output.md) — constraining model output to reduce hallucination
