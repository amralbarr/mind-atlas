# LLM Evaluation

## What is it?

[LLM](../generation/llm.md) evaluation is the practice of actually measuring whether an [LLM](../generation/llm.md), a prompt, or a full AI pipeline is producing good output — as opposed to eyeballing a few responses and assuming it works. Because [LLM](../generation/llm.md) output is open-ended text rather than a single correct number, "is this good?" is harder to check than a typical software test, and none of the shortcuts (a single accuracy number, a passing unit test) fully capture it on their own. Without deliberate evaluation, prompt changes, model upgrades, and [fine-tuning](../infrastructure/fine-tuning.md) runs are all shipped on faith — evaluation is what turns "I think this got better" into a measurement.

## Why this is hard

- **Outputs are open-ended.** Many valid phrasings can all be "correct" answers to the same prompt, so exact-string matching mostly doesn't work.
- **Failure modes are subtle.** A response can be fluent, confident, and completely wrong ([hallucination](../generation/llm.md), see its "Hallucination" section) — surface quality doesn't correlate with correctness.
- **Regressions are silent.** A prompt or model change that improves one behavior can quietly break another unless it's specifically tested for.
- **"Good" is task-dependent.** Correctness matters for factual Q&A; tone and helpfulness matter more for a support bot; strict format adherence matters for a data-extraction pipeline — there's no single universal metric.

## The three main approaches

| Approach             | How it works                                                                                                                 | Strengths                                                                                                                                                                                               | Weaknesses                                                                                                                                                   |
| -------------------- | ---------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **Benchmarks**       | Run the model against a fixed, standardized dataset with known correct answers (e.g. MMLU for knowledge, HumanEval for code) | Objective, reproducible, comparable across models                                                                                                                                                       | Frontier models increasingly saturate older benchmarks; a benchmark score doesn't guarantee good performance on *your* specific task                         |
| **[LLM](../generation/llm.md)-as-judge**     | Use a second (often stronger) [LLM](../generation/llm.md) to score the first model's outputs against a rubric                                        | Fast, cheap (fractions of a cent per evaluation vs. $5–$50 per human evaluation), scales to thousands of evaluations quickly                                                                            | Correlates well but imperfectly with human judgment (roughly ~80% correlation in current studies); systematically underestimates errors in subtle edge cases |
| **Human evaluation** | People directly read and score outputs against defined criteria                                                              | Catches failure modes automated methods miss — plausible-sounding factual errors, tone that's technically fine but contextually wrong, reasoning that reaches a correct conclusion through flawed logic | Slow, expensive, doesn't scale to continuous evaluation                                                                                                      |

## LLM-as-judge in practice

A judge model is given the original prompt, the response to evaluate, and a scoring rubric, and asked to produce a score or verdict:

```
Judge prompt:
"Given this question and answer, rate the answer's factual
 accuracy from 1-5. Only use information in the provided
 context to verify correctness. Explain your score briefly."

Question: "What was Q3 revenue?"
Answer:   "Q3 revenue was 2.4M, exceeding target by 12%."
Context:  [source document excerpt]

Judge output: "Score: 5. The answer matches the figures
               stated in the source document exactly."
```

This pattern (sometimes called G-Eval) is now the default approach for teams that need evaluation throughput beyond what human review can provide — running an [LLM](../generation/llm.md) judge against every deployment candidate, every prompt variant, or a sample of live production traffic.

## Hybrid evaluation (the practical recommendation)

Because [LLM](../generation/llm.md)-as-judge alone under-catches subtle failures, and human evaluation alone doesn't scale, the standard production pattern combines them: run [LLM](../generation/llm.md)-as-judge continuously across all or most outputs for fast, cheap signal, and route a sample (commonly around 5–10%) to human review as a calibration layer that catches what the automated judge misses. Studies on this hybrid approach show meaningfully better failure detection than automated-only evaluation.

## What to actually measure

Evaluation criteria should match the failure modes that matter for the specific pipeline:

| Dimension | What it checks | Relevant to |
|---|---|---|
| **Correctness / factuality** | Is the claim actually true, and grounded in the given context? | [RAG](../rag/rag.md) systems, Q&A — see [LLM hallucination](../generation/llm.md)'s "Hallucination" section |
| **Completeness** | Does the answer cover everything the question asked? | Summarization, multi-part questions |
| **Format adherence** | Does the output match the required structure? | Anywhere consuming [structured output](../generation/structured-output.md) |
| **Robustness** | Does quality hold up on edge cases, adversarial inputs, or unusual phrasing? | Anything user-facing |
| **Consistency** | Does the same input produce a stable answer across runs? | Anything sensitive to [sampling parameters](../generation/sampling-parameters.md) |

## Building an evaluation set

A practical, minimal evaluation setup: collect a fixed set of representative test cases (including known edge cases and past failures) with either a known-correct answer or a clear rubric, run the pipeline against that set whenever a prompt/model/fine-tune changes, and compare scores before and after the change — rather than assessing quality on an ad hoc basis. This is the same "regression suite" idea from traditional software testing, applied to non-deterministic output.

## Related

- [Large Language Models (LLMs)](../generation/llm.md) — hallucination is the primary failure mode [RAG](../rag/rag.md)/LLM evaluation targets
- [Retrieval-Augmented Generation (RAG)](../rag/rag.md) — the technique most often evaluated for grounding and hallucination reduction
- [Retrieval Metrics](retrieval-metrics.md) — Recall@k, Precision@k, [MRR](mrr.md), [NDCG](ndcg.md): the metrics that measure retrieval quality specifically
- [Fine-tuning](../infrastructure/fine-tuning.md) — evaluation is how you confirm a fine-tuned model actually improved the target behavior without regressing others
- [Prompt Engineering](../generation/prompt-engineering.md) — evaluation is what tells you whether a prompt change actually helped
- [Temperature & Sampling Parameters](../generation/sampling-parameters.md) — low temperature improves reproducibility when comparing evaluation runs
