# Data Validation

**Data validation** is the practice of checking that incoming data matches an expected shape, type, and set of constraints *before* application logic ever touches it — rejecting malformed input early with a structured error, instead of letting a bad value silently propagate deeper into the system where it's harder to trace and more expensive to fail on.

## Why Validate at the Boundary

```
Request arrives
    ↓
Validation layer  ← reject here: cheap, clear error, nothing downstream has run yet
    ↓
Business logic    ← assumes the data is already well-formed from this point on
    ↓
Database / external calls
```

Validating at the system's entry point (an API request body, a function's public parameters, a message consumed from a queue) means every layer behind it can simply **trust** the data's shape instead of re-checking it defensively at every step — validate once, at the edge, then stop worrying about it internally.

## What a Validation Failure Should Produce

A good validation failure is specific and structured, not a generic "bad request":

```json
{
  "error": "validation_failed",
  "details": [
    {"field": "max_tokens", "message": "must be >= 1, got -5"},
    {"field": "query", "message": "required field missing"}
  ]
}
```

This lets a client (or a developer debugging an integration) fix the actual problem immediately, rather than guessing which of several fields was wrong from a single opaque error message.

## Type Coercion vs. Strict Validation

[Validation libraries](../../../overviews/programming/validation-libraries.md) differ in whether they coerce a value into the expected type or reject anything that isn't already exactly that type:

| | Coercion | Strict |
|---|---|---|
| **Behavior** | `"42"` → `42` (string coerced to int) | `"42"` rejected — must already be an `int` |
| **Common for** | Query strings, environment variables, form data — everything arrives as text | Internal service-to-service calls, where the sender controls the exact type |
| **Risk** | Silently accepting a near-miss value that wasn't actually intended as that type | More boilerplate when the input genuinely is always a string that needs converting |

Neither is universally correct — the right choice depends on where the data is coming from and how much you trust the sender to have sent the right type already.

## Schema Validation vs. Business-Rule Validation

These are two different layers, often conflated:

| | Schema validation | Business-rule validation |
|---|---|---|
| **Checks** | Shape and type: is `email` a string, is `age` a non-negative integer | Domain logic: does this email already exist, is this user allowed to book this date |
| **Where it runs** | Immediately, before any logic runs — a [Pydantic](../python/pydantic.md)/[class-validator](../../backend/api/class-validator.md)/[Zod](../typescript/zod.md) layer | After schema validation passes, inside application/service logic, often requiring a database lookup |
| **Failure means** | The request itself is malformed | The request is well-formed but not allowed for this specific case |

A request can pass schema validation (every field is the right type) and still fail business-rule validation (that type is correct, but the specific value conflicts with existing state) — these are genuinely different failure modes and usually deserve different error codes (400 vs. 409/422).

## Client-Side vs. Server-Side Validation

Client-side validation (disabling a submit button, inline form errors) is a **UX improvement**, not a security boundary — it runs in code the user fully controls and can bypass entirely (a direct API call, browser dev tools, a modified request). Server-side validation is the only validation that actually protects the system; client-side validation exists purely to give the user fast feedback before a round-trip, and must never be trusted as the sole gate.

## Concrete Implementations in This Handbook

The general principle above is the same regardless of language — these are the concrete libraries that implement it:

| Library | Language | Style |
|---|---|---|
| **[Pydantic](../python/pydantic.md)** | Python | Class + type hints (`BaseModel`), used standalone or built into [FastAPI](../python/fastapi.md) |
| **[class-validator](../../backend/api/class-validator.md)** | TypeScript | Decorators on a class, the NestJS convention via `ValidationPipe` |
| **[Zod](../typescript/zod.md)** | TypeScript | Schema object with automatic type inference, framework-agnostic |

See the [Validation Libraries overview](../../../overviews/programming/validation-libraries.md) for the full side-by-side comparison, code examples for each, and guidance on which to choose per scenario.

## Where Validation Matters Beyond Web APIs

- **[Structured Output](../../ai/generation/structured-output.md)** — [Pydantic](../python/pydantic.md)/[Zod](../typescript/zod.md) schemas are also how an [LLM](../../ai/generation/llm.md)'s free-text output gets validated and coerced into a reliable, typed structure, not just how [HTTP](../../networking/http.md) request bodies are checked.
- **[Idempotency](../../backend/api/idempotency.md)** — a validated, well-formed request is a prerequisite for [idempotency](../../backend/api/idempotency.md) keys and retry logic to behave predictably; validating a malformed retry the same way as the original request avoids subtle divergence.
- **[OpenAPI](../../backend/api/openapi.md)** — [Pydantic](../python/pydantic.md) models and NestJS DTOs both double as the source of truth [OpenAPI](../../backend/api/openapi.md) schema generation reads from, so the validation layer and the API documentation never drift out of sync.

## Related

- [Validation Libraries](../../../overviews/programming/validation-libraries.md) — the full [Pydantic](../python/pydantic.md) vs. [class-validator](../../backend/api/class-validator.md) vs. [Zod](../typescript/zod.md) comparison with code
- [Pydantic](../python/pydantic.md)
- [class-validator](../../backend/api/class-validator.md)
- [Zod](../typescript/zod.md)
- [FastAPI](../python/fastapi.md) — Pydantic is its built-in validation layer
- [Structured Output](../../ai/generation/structured-output.md) — the same validation principle applied to [LLM](../../ai/generation/llm.md) output
- [JSON](json.md) — the format most validated request bodies arrive as
- [Idempotency & Double-Submit Prevention](../../backend/api/idempotency.md)
