# Structured Output / JSON Mode

## What is it?

Structured output is a feature that forces an [LLM](llm.md)'s response to conform to a predefined schema — typically [JSON](../../programming/fundamentals/json.md) Schema — rather than returning free-form text that a downstream system then has to hopefully parse correctly. Instead of prompting a model to "please respond in [JSON](../../programming/fundamentals/json.md)" and hoping it complies, structured output makes schema conformance a guarantee enforced by the model provider, not a request the model might ignore, truncate, or get subtly wrong (trailing commas, missing quotes, an extra sentence before the [JSON](../../programming/fundamentals/json.md)).

```
Without structured output:
Prompt: "Extract the name and age as JSON."
Response: "Sure! Here's the JSON you asked for:
           {name: 'Alice', age: 30}"   ← invalid JSON, has commentary,
                                          uses single quotes
```

```
With structured output (schema enforced):
Prompt + schema: { name: string, age: integer }
Response: {"name": "Alice", "age": 30}   ← guaranteed valid, guaranteed
                                            to match exactly this shape
```

## Why it matters for real integrations

Any time an [LLM](llm.md)'s output needs to be consumed by code rather than read by a human — populating a database record, calling another API, triggering a workflow branch, filling a UI form — the output has to be reliably parseable. Free-text generation, even when instructed to "return [JSON](../../programming/fundamentals/json.md)," is probabilistic: it can add explanatory text, use the wrong field names, omit a required field, or produce syntactically invalid [JSON](../../programming/fundamentals/json.md) under some fraction of requests. At scale, even a small failure rate turns into constant parsing errors and defensive retry logic. Structured output eliminates that class of failure at the source, which is why it's become standard for [tool/function calling](../agents/tool-calling.md) (the arguments a model provides for a tool call are themselves a structured-output problem), data extraction pipelines, and any agent step that hands off to non-[LLM](llm.md) code.

## How it actually works: constrained decoding

The mechanism underneath is **constrained decoding**: the provider compiles the target JSON Schema into a grammar — commonly represented as a finite-state automaton — that defines exactly which tokens are valid at each position in the output. During generation, the sampling step (see [Temperature & Sampling Parameters](sampling-parameters.md)) is restricted to only the tokens that keep the output on a valid path through that grammar. This is a structural guarantee enforced at the token-generation level, not a matter of the model "trying harder" to follow instructions — it's mechanically impossible for the model to emit a token that would produce invalid or off-schema output.

```
Schema: { "name": string, "age": integer }
         ↓ compiled into a grammar/finite-state machine
At each generation step, only tokens that keep the output on a
valid path through that grammar are allowed to be sampled —
e.g. after `{"name": "Alice", "age":` only a number token
(not a letter, not a closing brace) is a legal next token.
```

## Current provider support (2026)

As of 2026, structured output has become table stakes across major providers, though implementations differ in strictness:

| Provider | Support | Notes |
|---|---|---|
| **OpenAI** | Native, strict mode | Constrained decoding, effectively 100% schema validity when strict mode is enabled |
| **Anthropic** | Native | High schema validity; the exact slice of JSON Schema fully supported is worth checking against current docs for edge cases |
| **Google Gemini** | Native | Constrained decoding, high schema validity |

The practical takeaway: which specific JSON Schema features (nested objects, unions, regex patterns, etc.) each provider fully honors varies, so schema design should stay within the commonly-supported subset (basic object/array/string/number/enum types) for the most portable results across providers.

## Structured output vs. tool calling

These overlap conceptually but are used differently:

| | Structured output / JSON mode | Tool/function calling |
|---|---|---|
| **Purpose** | Shape a final answer to a fixed schema | Request that an external function be executed |
| **What happens next** | The caller consumes the structured data directly (e.g. inserts into a database) | The caller executes real code and feeds a result back to the model |
| **Underlying mechanism** | Same constrained decoding technique | Also relies on constrained decoding for argument validity |

In practice, [tool calling](../agents/tool-calling.md) *is* a structured-output problem for the arguments — see [Function / Tool Calling](../agents/tool-calling.md).

## Practical pattern: schema-first extraction

A common production pattern (often via libraries like [Pydantic](../../programming/python/pydantic.md) in Python or [Zod](../../programming/typescript/zod.md) in TypeScript) is to define the target schema in code, generate the JSON Schema from it automatically, pass that to the model with structured output enabled, and then parse the guaranteed-valid response directly into a typed object — removing manual JSON parsing and validation code from the pipeline entirely.

```python
from pydantic import BaseModel

class Extraction(BaseModel):
    name: str
    age: int

# schema derived from Extraction is sent to the model;
# the response is guaranteed to validate against it
result = Extraction.model_validate_json(model_response)
```

## Related

- [Function / Tool Calling](../agents/tool-calling.md) — tool-call arguments rely on the same schema-conformance guarantee
- [Temperature & Sampling Parameters](sampling-parameters.md) — constrained decoding operates at the same token-sampling step these parameters affect
- [Pipeline Orchestration](../infrastructure/pipeline-orchestration.md) — pipelines that consume structured [LLM](llm.md) output as an input to the next stage
