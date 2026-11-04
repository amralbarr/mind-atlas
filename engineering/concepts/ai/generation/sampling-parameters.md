# Temperature & Sampling Parameters

## What is it?

An [LLM](llm.md) doesn't generate a single "correct" next token — at each step, it produces a probability distribution over its entire vocabulary (tens of thousands of candidate tokens), and something has to pick one. **Sampling parameters** are the settings that control how that pick is made: how random or deterministic it is, and which candidates are even eligible.

```
Model's raw output for the next token:
"cat"   → 42%
"dog"   → 31%
"bird"  → 12%
"fish"  → 8%
... (thousands more, tiny probabilities)
         ↓
Sampling strategy decides which token actually gets chosen
```

Getting these right matters because the same prompt, same model, sent twice with different sampling settings can produce meaningfully different output — more creative and varied, or more predictable and repeatable.

## Temperature

**Temperature** scales the probability distribution before a token is sampled from it, controlling how "confident vs. exploratory" the choice is.

| Temperature | Effect |
|---|---|
| `0` | Deterministic — always pick the single highest-probability token (greedy decoding). Same input → same output every time. |
| `~0.2–0.5` | Mostly deterministic with a little variation. Good for factual Q&A, extraction, code generation. |
| `~0.7–1.0` | Balanced — the model's typical/default range for general chat. |
| `>1.0` | Increasingly random and creative, at the cost of coherence and factual reliability. |

Mechanically, temperature divides the logits (pre-probability scores) by the temperature value before the softmax that turns them into probabilities. Low temperature sharpens the distribution toward the top candidate; high temperature flattens it, giving lower-probability tokens a real chance of being picked.

```
temperature = 0    → "The capital of France is Paris."       (every time)
temperature = 1.2  → "The capital of France is, historically
                       speaking, the beautiful city of Paris."
                      (varies across runs, more embellishment)
```

**When to use which:** temperature 0 (or near it) for tasks with one correct answer — data extraction, classification, code that must compile, [RAG](../rag/rag.md) answers that should be grounded and reproducible. Higher temperature for open-ended generation — brainstorming, creative writing, varied marketing copy — where multiple different outputs are all "good."

## Top-p (nucleus sampling)

**Top-p** restricts sampling to the smallest set of tokens whose cumulative probability adds up to at least `p`, then samples only from that set (renormalized).

```
Full distribution: cat 42%, dog 31%, bird 12%, fish 8%, ...(long tail)

top_p = 0.9 → keep tokens until cumulative probability ≥ 90%
           → {cat, dog, bird} ≈ 85%, add fish → 93% ≥ 90% → stop
           → sample only from {cat, dog, bird, fish}, everything
             else (the long, unlikely tail) is excluded entirely
```

The key advantage over temperature alone: top-p adapts to how confident the model is at a given step. When the model is very confident (one token dominates), the nucleus is small and sampling stays close to deterministic. When the model is uncertain (probability spread across many tokens), the nucleus is larger and more variety is allowed — without ever including truly implausible tokens from the tail.

## Top-k

**Top-k** is a simpler, non-adaptive version: restrict sampling to exactly the `k` highest-probability tokens, regardless of how their probabilities are actually distributed.

```
top_k = 3 → always sample from exactly the top 3 tokens,
            whether they collectively hold 95% of the
            probability mass or only 40% of it
```

Top-k is easier to reason about but less adaptive than top-p — a fixed `k` can be too restrictive when the model is genuinely uncertain (many plausible tokens) or too permissive when it's very confident (only one or two tokens are actually reasonable).

## How they combine

Most APIs let you set temperature and top-p (and sometimes top-k) together; they compose — top-p/top-k first narrow the candidate pool, then temperature reshapes the probabilities within it before the final sample is drawn. Common practical guidance from provider documentation: adjust *either* temperature *or* top-p for a given use case, not both aggressively at once, since compounding two randomness controls makes behavior harder to reason about and reproduce.

| Parameter | Controls | Typical default |
|---|---|---|
| `temperature` | How sharply peaked vs. flat the probability distribution is | ~0.7–1.0 |
| `top_p` | Cumulative probability cutoff for eligible tokens | ~0.9–1.0 |
| `top_k` | Fixed count of eligible tokens | Often unset/unbounded |

## Related

- [Large Language Models (LLMs)](llm.md) — the model these parameters configure
- [Tokenization](tokenization.md) — what a "token" being sampled actually is
- [Prompt Engineering](prompt-engineering.md) — the other main lever for controlling [LLM](llm.md) output, orthogonal to sampling settings
- [LLM Evaluation](../evaluation/llm-evaluation.md) — why reproducibility (low temperature) matters when measuring output quality
