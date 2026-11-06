# HELM (Holistic Evaluation of Language Models)

HELM is a multi-metric framework for evaluating language models, built by Stanford's Center for Research on Foundation Models (CRFM) and first published in 2022. Its premise is the same one [LLM Evaluation](llm-evaluation.md) raises generically about benchmarks: a single leaderboard accuracy number tells you almost nothing about *how* a model fails — whether it's confidently wrong, unstable under small input changes, biased across demographic groups, or simply expensive to run — so HELM evaluates every model it covers across many scenarios and many metrics simultaneously, under the same standardized conditions, rather than ranking models by one headline score.

## The two axes: scenarios and metrics

HELM is organized as a grid, not a single test: a set of **scenarios** (what task and dataset is being run) crossed against a set of **metrics** (what property of the output is being measured on that scenario). The original paper evaluated 30 prominent language models across 42 scenarios using 7 core metrics, computing each metric for each scenario wherever that combination made sense (not every metric applies to every scenario).

## The 7 core metrics

| Metric | What it checks | Why accuracy alone misses this |
|---|---|---|
| **Accuracy** | Is the output correct against the task's ground truth? | The traditional single-number benchmark score |
| **Calibration** | Does the model's confidence match its actual correctness rate? (measured via Expected Calibration Error and selective-classification accuracy) | A model can be accurate on average while being *overconfident* on the cases it gets wrong — dangerous in any system where a user trusts a stated confidence |
| **Robustness** | Does accuracy hold up under typos, paraphrasing, or small input perturbations? | A model that's accurate on clean benchmark inputs can degrade sharply on the messier real-world phrasing users actually type |
| **Fairness** | Does accuracy hold consistently across demographic subgroups or input variations tied to group identity? | Aggregate accuracy can hide a model performing far worse for some subgroups than others |
| **Bias** | Does the model's own generated text reproduce or amplify harmful stereotypes, independent of task correctness? | Distinct from fairness: a model can be equally *accurate* across groups while still generating *biased content* |
| **Toxicity** | Does the model produce harmful, offensive, or unsafe content? | Not captured by any correctness-based metric at all |
| **Efficiency** | What does it cost to train and run — training-time estimated energy/CO2, and inference-time latency per request | A more accurate model that's prohibitively slow or expensive isn't necessarily the better production choice |

HELM's own published results found accuracy, robustness, and fairness tend to correlate positively with each other (a more accurate model is often also more robust and fair), while calibration's relationship with accuracy is far less consistent and varies by scenario — a reminder that none of these seven metrics can be reliably inferred from any of the others; each has to actually be measured.

## Why this matters more than a single leaderboard score

The same caution raised in this handbook's [LLM Evaluation](llm-evaluation.md) note about benchmark saturation applies directly here: a model that tops a single accuracy leaderboard can still be the wrong choice if it's poorly calibrated for a system that surfaces confidence to users, fragile under the kind of messy real-world input a benchmark's clean test set never includes, or meaningfully biased in ways a pure accuracy score can't surface at all. HELM's whole design exists to make that gap visible rather than hidden behind one number — in the same spirit that [RAGAS](ragas.md) deliberately scores a [RAG](../rag/rag.md) pipeline on four separate metrics instead of one, specifically so a failure can be localized to retrieval vs. generation rather than only flagged as "something is wrong."

## How it's used in practice

```
Don't ask: "Which model has the highest HELM score?"
           (HELM intentionally has no single aggregate ranking
            the way a leaderboard-style benchmark does)

Ask instead: "Which of HELM's scenarios most resembles my actual
             task, and which of the 7 metrics matter most for
             how my system is actually used?"

e.g. a system that surfaces a confidence number to end users
     → weight Calibration heavily
e.g. a system serving users across several demographic groups
     → weight Fairness and Bias heavily
e.g. a high-volume, cost-sensitive production deployment
     → weight Efficiency heavily alongside Accuracy
```

HELM's own published leaderboard reports each model's score per scenario/metric combination rather than collapsing everything into one rank — the practical takeaway is to go to the specific slice of that grid that matches the deployment at hand, the same discipline recommended for reading [MTEB](mteb.md)'s own leaderboard rather than trusting its aggregate score.

## Related

- [LLM Evaluation](llm-evaluation.md) — the general case against trusting a single benchmark number that HELM operationalizes into a specific multi-metric methodology
- [MTEB](mteb.md) — the analogous "don't trust one leaderboard score" framework for embedding models rather than full language models
- [RAGAS](ragas.md) — a different multi-metric evaluation framework, scoped specifically to [RAG](../rag/rag.md) pipelines rather than general language-model capability
- [RAG](../rag/rag.md) — one of many system types a model evaluated via HELM's scenarios might end up powering
- [NIST AI RMF](../../security/governance/nist-ai-rmf.md) — a risk-management framework that names several of the same properties (fairness, robustness, safety) HELM measures, as governance requirements rather than benchmark metrics
