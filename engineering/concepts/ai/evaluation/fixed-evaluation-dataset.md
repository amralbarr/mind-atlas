# Fixed Evaluation Dataset

A curated, static set of test cases with known expected outputs used to measure an AI system's quality consistently over time. "Fixed" is the critical word: the dataset does not change between runs, so any change in score reflects a real change in system behavior.

Without a fixed evaluation dataset, you cannot tell whether a change made things better or worse — you're flying blind.

---

## Why Fixed Matters

```
Without a fixed dataset:
  Run 1 — model A   → "looks good"  (informal observation)
  Run 2 — model B   → "also looks good"  (different queries)
  Question: is B better than A?  → Unknown.

With a fixed dataset:
  Run 1 — model A   → groundedness 0.91, relevance 0.88
  Run 2 — model B   → groundedness 0.87, relevance 0.90
  Question: is B better than A?  → B has higher relevance, but lower groundedness.
```

A fixed dataset turns subjective impressions into reproducible measurements.

---

## What Goes Into the Dataset

A good evaluation dataset covers the full distribution of real usage:

| Category | What it tests | Example |
|---|---|---|
| Happy path | Core use case works | "What is the leave policy?" → expects the policy text |
| Edge case | Boundary conditions | Very long query, unusual phrasing |
| Out-of-scope | Correct abstention | "What is the weather in Riyadh?" → expects refusal |
| Adversarial | Robustness | [Prompt injection](../../security/attacks/prompt-injection.md) attempt, contradictory context |
| Multi-hop | Reasoning across documents | Answer requires combining info from two sources |
| Ambiguous | Graceful handling | Query could mean two things — both interpretations handled |
| Bilingual | Language handling | Arabic query on Arabic document, mixed query |
| Permission denial | Access control enforcement | A restricted-permission user asks about a document their role must not see → expects refusal, not a leaked answer |

An enterprise [RAG](../rag/rag.md) evaluation set typically has 50–200 cases across these categories — start with 50–100 genuinely good rows a domain expert stands behind, rather than a few thousand weak ones an [LLM](../generation/llm.md) alone generated. Large enough to be statistically meaningful, small enough to run frequently.

### One Dataset Per Project, Not One Shared Across Them

A single enterprise platform running several parallel use cases needs a **separate evaluation dataset per project**, not one shared set — each project has its own documents, users, and question shapes, so a case that's a sensible "happy path" question for one project may be out-of-scope nonsense for another. Sharing one dataset across projects either dilutes coverage of each project's real failure modes or produces a set so generic it tests nothing specific well.

---

## Structure of a Test Case

```python
evaluation_case = {
    "id": "eval-042",
    "category": "happy_path",
    "question": "What is the process for capital expenditure approval above SAR 250,000?",
    
    # Ground truth: the correct answer, verified by a domain expert
    "ground_truth": "Expenditures above SAR 250,000 require approval from the CFO "
                    "and the relevant department head, with a formal business case "
                    "submitted at least 10 business days in advance.",
    
    # Which documents should be retrieved
    "expected_source_ids": ["policy-capex-2024", "finance-procedures-v3"],
    
    # What the system should NOT say
    "negative_examples": [
        "SAR 500,000",  # wrong threshold
        "CEO approver",  # wrong approver
    ],
    
    # The requesting user's access level — required for permission-denial
    # cases, where the expected behavior is a refusal, not an answer
    "permission_level": "finance_department",
    
    # Minimum quality bars
    "min_groundedness": 0.90,
    "min_relevance": 0.85,
}
```

A spreadsheet (Excel or CSV) with exactly these fields as columns — question, ground-truth answer, expected source/chunk IDs, category, permission level — is a perfectly good starting format, especially while the dataset is still 50–100 rows and domain experts are filling it in directly; the Python-dict/[JSON](../../programming/fundamentals/json.md) structure above is what a later evaluation script loads it into, not a requirement for how the dataset starts out.

---

## Building the Dataset

The dataset must be built from real domain expertise, not invented:

```
1. Collect real user queries
   → Mine from support tickets, usage logs, user interviews
   → Ask domain experts: "What questions would users actually ask?"
   → An LLM can draft additional candidate questions from the source documents
     to widen coverage faster, but every drafted question still needs a human
     to review it and verify the ground-truth answer — never auto-accept an
     LLM-drafted question-and-answer pair as-is

2. Write ground-truth answers
   → Have a domain expert (not the developer) write the correct answer
   → Reference the specific source document and section
   → Document the expected retrieved passages

3. Add edge cases deliberately
   → Every category from the table above needs at least a few examples
   → Out-of-scope questions are the most commonly missing category

4. Review by a second domain expert
   → Ground-truth answers are verified independently
   → Disagreements are resolved before the set is frozen

5. Lock the dataset
   → Version-control it. Never modify existing cases.
   → New cases can be added, but existing cases are immutable.
```

If the developer writes the ground-truth answers, you get a dataset that reflects what the developer thinks users will ask — which is usually wrong. Build it with actual users or domain experts.

---

## Running Evaluations

The fixed dataset becomes an automated regression test — run it on every significant change:

```python
results = []
for case in evaluation_dataset:
    answer, retrieved_docs = rag_pipeline.query(case["question"], user_permission=case["permission_level"])
    
    results.append({
        "id": case["id"],
        "groundedness": evaluate_groundedness(answer, retrieved_docs),
        "relevance": evaluate_relevance(case["question"], answer),
        "correctness": evaluate_correctness(answer, case["ground_truth"]),
        "retrieval_hit": case["expected_source_ids"][0] in [d.id for d in retrieved_docs],
        # For a no-answer case, correct behavior is an explicit refusal, not a guess
        "refused_correctly": case["category"] == "out_of_scope" and answer.status == "abstained",
        # For a permission-denial case, the restricted document must never appear at all
        "permission_held": case["category"] != "permission_denial" or case["expected_source_ids"][0] not in [d.id for d in retrieved_docs],
    })

# Compare against baseline
regression = [r for r in results if r["groundedness"] < baseline[r["id"]]["groundedness"] - 0.05]
if regression:
    block_deployment(f"Groundedness regression on {len(regression)} cases")
```

Run the evaluation on every:
- Prompt change
- Chunking strategy change
- Embedding model change
- [LLM](../generation/llm.md) version update
- Knowledge base restructure

---

## Evaluation Cadence

| Change type | When to run evaluation |
|---|---|
| Prompt edit | Every time, before deployment |
| Model version update | Before and after — compare scores |
| Embedding model change | Full re-index + full evaluation |
| Knowledge base content update | Spot check on affected categories |
| Production incident | Identify which cases would have caught it, add them |

When a production issue occurs, the first question is: "Do we have an evaluation case that would have caught this?" If not, add one. The dataset should grow to reflect real failure modes.

---

## Golden Set vs Full Evaluation Set

In practice, teams maintain two sets:

**Golden set (10–20 cases)** — the highest-priority, most critical queries. Run on every code change. Results in seconds. These are the queries that absolutely must work.

**Full evaluation set (100–200 cases)** — comprehensive coverage across all categories. Run before any deployment or major change. Takes minutes to run. Used for detailed quality analysis.

---

## Related

- [LLM Evaluation](llm-evaluation.md) — the metrics computed against this dataset: Recall@k, groundedness, relevance, correctness
- [Retrieval Metrics](retrieval-metrics.md) — Recall@k, Precision@k, [MRR](mrr.md): the specific [retrieval metrics](retrieval-metrics.md) measured against this dataset's chunk IDs
- [Groundedness and Correctness](groundedness-and-correctness.md) — the specific quality dimensions the dataset measures
- [RAG](../rag/rag.md) — the system the evaluation dataset is designed to validate
- [UAT](../../backend/delivery/uat.md) — fixed evaluation datasets are the automated equivalent of [UAT](../../backend/delivery/uat.md) acceptance criteria
- [Authorization](../../security/authorization/authorization.md) — what a permission-denial test case actually verifies is enforced
