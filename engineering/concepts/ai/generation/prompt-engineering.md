# Prompt Engineering

## What is it?

Prompt engineering is the practice of structuring the input to an [LLM](llm.md) — the instructions, examples, and framing you give it — to reliably get the output quality you want, without changing the model itself. The same underlying model can produce dramatically different results depending on how a request is phrased, structured, and supported with examples; prompt engineering is the discipline of controlling that variance deliberately instead of by accident.

It sits at the cheap end of the "how do I make this model do what I want" spectrum: it's free, immediate, and reversible, compared to [fine-tuning](../infrastructure/fine-tuning.md) (retraining) or [RAG](../rag/rag.md) (building a retrieval pipeline). In 2026's common decision framework, prompt engineering is the first thing to try, [RAG](../rag/rag.md) is reached for when the model needs knowledge it doesn't have, and [fine-tuning](../infrastructure/fine-tuning.md) is reserved for when both of those fail to produce consistent behavior — see [Fine-tuning](../infrastructure/fine-tuning.md) for the full comparison.

## System prompt vs. user prompt

Most chat-style [LLM](llm.md) APIs separate the conversation into roles — a persistent [system prompt](system-prompt.md) setting context/rules for the whole conversation, a user prompt for the current turn, and prior assistant responses for memory. See [System Prompt](system-prompt.md) for the full role breakdown, a concrete example, why keeping instructions there is more reliable and cheaper than repeating them per turn, and its role as the primary defense against [prompt injection](../../security/attacks/prompt-injection.md).

## Core techniques

**Zero-shot** — just ask, with no examples:
```
"Classify this review as positive, negative, or neutral: 'The battery life is terrible.'"
```
Works well for tasks the model has clearly seen a lot of during training.

**Few-shot** — show the model 2-5 examples of the [input/output](../../programming/fundamentals/io.md) pattern before the real request:
```
Review: "Fast shipping, great quality!" → positive
Review: "Broke after one day." → negative
Review: "It's fine, does the job." → neutral
Review: "The battery life is terrible." → ?
```
Few-shot examples are often more effective than a paragraph of instructions describing the same pattern, especially for tasks with a specific output format or an unusual classification scheme the model wouldn't infer on its own.

**Chain-of-thought (CoT)** — ask the model to reason step by step before answering, instead of jumping straight to a final answer:
```
"Solve this step by step, then give the final answer:
 A store has 120 apples. It sells 45% in the morning
 and 30 more in the afternoon. How many are left?"
```
This measurably improves accuracy on multi-step reasoning, arithmetic, and logic tasks, because it gives the model room to work through intermediate steps as generated tokens rather than trying to jump to a correct answer in a single forward pass. Modern reasoning-focused models do a version of this internally, but explicitly prompting for it still helps with non-reasoning models and makes the model's logic auditable.

**Role/persona framing** — telling the model to act as a specific kind of expert ("You are a senior security engineer reviewing this code for vulnerabilities") tends to bias its output toward the vocabulary, priorities, and thoroughness associated with that role.

**Output format constraints** — explicitly specifying the shape of the response ("respond with exactly one word", "return a [JSON](../../programming/fundamentals/json.md) object with these keys") reduces variance in the response and makes downstream parsing reliable. For guarantees stronger than a well-worded instruction, see [Structured Output](structured-output.md).

## Why prompt structure affects output quality

[LLMs](llm.md) generate text one token at a time, conditioned on everything before it. That means:
- **Position matters** — instructions placed at the very start or very end of a long prompt tend to be followed more reliably than instructions buried in the middle (the same "lost in the middle" effect discussed in [Context Window](context-window.md)).
- **Ambiguity gets resolved arbitrarily** — an underspecified prompt doesn't fail, it just gets answered according to whatever pattern the model's training data suggests is most likely, which may not match what you meant.
- **Examples anchor format more strongly than descriptions** — telling a model "respond in this format" is weaker than showing it one example of that exact format.
- **Contradictory instructions degrade output** — if the [system prompt](system-prompt.md) and user prompt conflict, or if a prompt makes competing demands (be concise AND be exhaustive), the model has to pick a resolution, and that resolution isn't always the one intended.

## Practical example: turning a vague prompt into a controlled one

```
Vague:     "Summarize this document."

Engineered:
System:    "You are a summarization assistant. Always produce
            exactly 3 bullet points, each under 20 words.
            Do not include information not present in the source."
User:      "Summarize this document: [document text]"
```

The second version constrains length, format, and grounding — three things left to chance in the first.

## Related

- [System Prompt](system-prompt.md) — its own atomic file now; the role breakdown, caching/reliability rationale, and its role as the primary defense against [prompt injection](../../security/attacks/prompt-injection.md)
- [Large Language Models (LLMs)](llm.md) — see its prompt template section for a concrete system/user prompt used in a [RAG](../rag/rag.md) pipeline
- [Structured Output / JSON Mode](structured-output.md) — enforcing format guarantees stronger than prompt instructions alone
- [Context Window](context-window.md) — why prompt position and length affect how reliably instructions are followed
- [Fine-tuning](../infrastructure/fine-tuning.md) — the next step up when prompt engineering alone can't produce consistent behavior
- [LLM Evaluation](../evaluation/llm-evaluation.md) — how to actually measure whether a prompt change improved output quality
