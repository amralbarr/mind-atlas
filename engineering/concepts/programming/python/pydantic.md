# Pydantic

Pydantic is a Python [data validation](../fundamentals/data-validation.md) and [serialization](../fundamentals/serialization.md) library built on standard type hints. You define a class that inherits from `BaseModel`, annotate its fields with Python types, and Pydantic validates every value at construction time — raising a detailed error if the data doesn't match. It is used throughout AI engineering as the standard way to enforce the shape of [LLM](../../ai/generation/llm.md) outputs, tool call arguments, and API request/response bodies. See [FastAPI](fastapi.md) for its most common web-framework integration, and [Structured Output](../../ai/generation/structured-output.md) for how it connects to [LLM](../../ai/generation/llm.md) schema-constrained generation.

---

## Core Concepts

| Term                    | Meaning                                                                                                                       |
| ----------------------- | ----------------------------------------------------------------------------------------------------------------------------- |
| `BaseModel`             | The base class every Pydantic model inherits from — gives it automatic validation, parsing, and [serialization](../fundamentals/serialization.md)                 |
| **Field**               | A class attribute with a type annotation; Pydantic infers the validation rule from the type (`str`, `int`, `list[str]`, etc.) |
| `model_validate()`      | Parses and validates a dict into a model instance; replaces the old `parse_obj()` in Pydantic v2                              |
| `model_validate_json()` | Same as above but accepts a raw [JSON](../fundamentals/json.md) string — the standard entry point when consuming [LLM](../../ai/generation/llm.md) output   |
| `model_dump()`          | Serializes a model instance back to a plain dict                                                                              |
| `model_json_schema()`   | Returns the [JSON](../fundamentals/json.md) Schema for the model — used to tell an [LLM](../../ai/generation/llm.md) exactly what shape to produce          |
| `Field(...)`            | Optional per-field config: default values, descriptions, aliases, constraints (min/max length, regex)                         |
| `@field_validator`      | A method that runs custom validation logic on a specific field after type coercion                                            |
| `@model_validator`      | A method that runs validation across the entire model (cross-field checks)                                                    |

---

## Basic Model

```python
from pydantic import BaseModel

class User(BaseModel):
    name: str
    age: int
    email: str

# Valid
user = User(name="Amr", age=30, email="amr@example.com")
print(user.name)       # "Amr"
print(user.model_dump())  # {'name': 'Amr', 'age': 30, 'email': 'amr@example.com'}

# Invalid — raises ValidationError with a detailed message
User(name="Amr", age="not-a-number", email="amr@example.com")
```

Pydantic coerces where safe (`"30"` → `30` for an `int` field) and raises for genuinely invalid values.

---

## Optional Fields and Defaults

```python
from pydantic import BaseModel, Field
from typing import Optional

class Article(BaseModel):
    title: str
    body: str
    tags: list[str] = []                   # default empty list
    author: Optional[str] = None           # nullable, defaults to None
    word_count: int = Field(default=0, ge=0, description="Must be non-negative")
```

`Field()` adds validation constraints (`ge` = greater-than-or-equal) and a `description` that ends up in the [JSON](../fundamentals/json.md) Schema — useful when the schema is passed to an [LLM](../../ai/generation/llm.md) as a tool definition, because the model reads those descriptions to understand what each field means.

---

## Missing Required Fields vs. Extra Fields — Two Independent Behaviors

Pydantic handles these two situations completely differently by default, and they are **independent** of each other — neither setting affects the other:

| | **Missing required field** | **Extra (unknown) field** |
|---|---|---|
| **Default behavior** | ❌ **Rejects** the input with a `ValidationError` | **Silently drops it** (no error) |
| **How to change it** | Give the field a default value to make it optional | `extra="forbid"` or `extra="allow"` (see below) |

```python
from pydantic import BaseModel

class User(BaseModel):
    name: str                      # required
    age: int                       # required
    city: str = "Riyadh"           # optional — has a default

User(name="Amr")
# ❌ ValidationError: age — Field required

User(name="Amr", age=30)
# ✅ name='Amr' age=30 city='Riyadh' — missing optional field filled from the default

User(name="Amr", age=30, is_admin=True)
# ✅ name='Amr' age=30 city='Riyadh'
#    ← is_admin was silently dropped, no error

User(name="Amr", is_admin=True)
# ❌ ValidationError: age — Field required
# (the extra field never would have caused an error on its own — the missing
# required field is the only reason this one fails)
```

A missing required field is never "filled in" with a guessed value — Pydantic rejects the whole input. An extra field is simply discarded unless you explicitly configure it otherwise.

### Controlling Extra-Field Behavior: `extra=`

```python
from pydantic import BaseModel, ConfigDict

class User(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str
    age: int

User(name="Amr", age=30, is_admin=True)
# ❌ ValidationError: is_admin — Extra inputs are not permitted
```

| `extra=` setting | Behavior |
|---|---|
| `"ignore"` (default) | Silently dropped |
| `"forbid"` | ❌ `ValidationError` |
| `"allow"` | Kept on the model instance |

**Why this matters for tool calls and untrusted input:** if an [LLM](../../ai/generation/llm.md) or a client sends an extra field like `skip_approval` or `is_admin`, the default `"ignore"` behavior means you never find out it tried — that attempted field can be a sign of a [prompt injection](../../security/attacks/prompt-injection.md) or a client bug probing for a privilege-escalation path. For anything parsing untrusted input ([LLM](../../ai/generation/llm.md) tool-call arguments, external API payloads), prefer `extra="forbid"` so an unexpected field becomes a visible error instead of a silent no-op.

---

## Strict Mode and Type Coercion

By default Pydantic runs in **lax mode** and actively tries to *coerce* values into the annotated type:

```python
class Payment(BaseModel):
    amount: int
    confirmed: bool

Payment(amount="500", confirmed="true")
# ✅ succeeds! amount=500 (int), confirmed=True (bool)
```

The string `"500"` is coerced to an `int`, and `"true"` to `True`. This is convenient for data that naturally arrives as text (HTML form fields, query strings), but it can be dangerous if you expected the caller to already send the correct type — a silently-coerced value can mask a bug in the client or in an [LLM](../../ai/generation/llm.md)'s output.

**The fix: `strict=True`**

```python
from pydantic import BaseModel, ConfigDict

class Payment(BaseModel):
    model_config = ConfigDict(strict=True)
    amount: int
    confirmed: bool

Payment(amount="500", confirmed="true")
# ❌ ValidationError: Input should be a valid integer
```

A single field can also be made strict on its own: `amount: int = Field(strict=True)`.

For untrusted input, the two settings are usually combined:

```python
model_config = ConfigDict(strict=True, extra="forbid")
```

### Other Defaults That Catch People Off Guard

| Situation | Default behavior | Fix |
|---|---|---|
| **Mutating an attribute after construction** | `payment.amount = "abc"` — **not validated** | `ConfigDict(validate_assignment=True)` |
| **Default values** | Never validated against the field's constraints | `ConfigDict(validate_default=True)` |
| **`Model.model_construct(...)`** | **Skips validation entirely** | Never use it on untrusted data |

### The `Optional` Trap in Pydantic v2

```python
class User(BaseModel):
    phone: str | None        # ← still REQUIRED! accepts None as a value, but the field itself can't be omitted

User()
# ❌ ValidationError: phone — Field required

User(phone=None)
# ✅ accepted
```

`str | None` means "the **value** may be `None`," not "the **field** may be absent." To make a field genuinely optional, it still needs a default:

```python
phone: str | None = None       # ← now actually optional
```

In Pydantic v1, `Optional[str]` implicitly defaulted to `None` on its own — that implicit behavior was removed in v2, which is a common upgrade trap.

---

## Nested Models

```python
class Address(BaseModel):
    city: str
    country: str

class Employee(BaseModel):
    name: str
    address: Address          # nested model — validated recursively

emp = Employee(name="Amr", address={"city": "Riyadh", "country": "SA"})
print(emp.address.city)       # "Riyadh"
```

Pydantic recursively validates nested models. This is the standard pattern for representing structured [LLM](../../ai/generation/llm.md) output with sub-objects.

---

## Custom Validators

```python
from pydantic import BaseModel, field_validator

class ToolCall(BaseModel):
    tool_name: str
    arguments: dict

    @field_validator("tool_name")
    @classmethod
    def tool_must_be_allowed(cls, v: str) -> str:
        allowed = {"search", "get_document", "send_message"}
        if v not in allowed:
            raise ValueError(f"tool '{v}' is not in the allowed list")
        return v
```

`@field_validator` runs after type coercion. Use it to enforce business rules that can't be expressed as a type alone — like restricting which tools an agent is permitted to call.

---

## Parsing LLM Output (the AI engineering use case)

When an [LLM](../../ai/generation/llm.md) returns [JSON](../fundamentals/json.md) and you need to parse it into a typed object:

```python
from pydantic import BaseModel

class ExtractedEntity(BaseModel):
    company: str
    location: str
    employee_count: int | None = None

# model_response is the raw JSON string from the LLM API
raw = '{"company": "Acme Corp", "location": "Riyadh", "employee_count": 200}'
entity = ExtractedEntity.model_validate_json(raw)

print(entity.company)   # "Acme Corp"
print(entity.location)  # "Riyadh"
```

`model_validate_json()` parses and validates in one step. If the [LLM](../../ai/generation/llm.md) returned the wrong type for a field, you get a `ValidationError` immediately rather than a silent bad value flowing downstream.

---

## Generating JSON Schema for Tool Definitions

When you define a tool for an [LLM](../../ai/generation/llm.md) agent, you need to describe its parameters as a [JSON](../fundamentals/json.md) Schema. Pydantic generates this automatically:

```python
from pydantic import BaseModel, Field

class SearchArgs(BaseModel):
    query: str = Field(description="The search query to execute")
    max_results: int = Field(default=5, ge=1, le=20, description="Number of results to return")
    filter_date: str | None = Field(default=None, description="ISO date string to filter results after")

print(SearchArgs.model_json_schema())
# {
#   "properties": {
#     "query": {"description": "The search query to execute", "title": "Query", "type": "string"},
#     "max_results": {"default": 5, "description": "Number of results to return", ...},
#     ...
#   },
#   "required": ["query"],
#   "title": "SearchArgs",
#   "type": "object"
# }
```

This schema is passed to the [LLM](../../ai/generation/llm.md) with the tool definition. The model reads the descriptions, understands the constraints, and (with [structured output](../../ai/generation/structured-output.md) / constrained decoding) generates arguments guaranteed to validate against it.

---

## Enforcing Agent Output Schema (interview pattern)

The Q14 pattern in the interview prep — enforcing structured outputs and blocking invalid tool calls:

```python
from pydantic import BaseModel, field_validator
from typing import Literal

ALLOWED_TOOLS = {"search_documents", "get_policy", "send_summary"}

class AgentAction(BaseModel):
    action: Literal["tool_call", "final_answer"]
    tool_name: str | None = None
    tool_args: dict = {}
    answer: str | None = None

    @field_validator("tool_name")
    @classmethod
    def validate_tool_name(cls, v: str | None) -> str | None:
        if v is not None and v not in ALLOWED_TOOLS:
            raise ValueError(f"Tool '{v}' is not permitted")
        return v

# Parse LLM response
raw_llm_output = '{"action": "tool_call", "tool_name": "search_documents", "tool_args": {"query": "leave policy"}}'
action = AgentAction.model_validate_json(raw_llm_output)
# If tool_name is not in ALLOWED_TOOLS → ValidationError raised before any execution
```

This is the concrete implementation of "explicit tool permission lists" — the agent harness parses every [LLM](../../ai/generation/llm.md) action through this model before executing anything.

---

## What Pydantic Does NOT Validate

Pydantic guarantees that data has the *right shape* — correct types, satisfied constraints, a value from an allowed set. It says nothing about whether that well-shaped request is actually **permitted**, **correct**, or **safe to execute**:

```
well-formed JSON  ≠  permitted request  ≠  correct request  ≠  safe to execute
    ↑ Pydantic           ↑ you                ↑ you              ↑ you
```

A tool call can pass every Pydantic check and still be a disaster — the right order ID but the wrong customer, an amount within range but larger than what's actually refundable, a request the user never made because a poisoned document told the model to issue it. None of that is a shape problem, so none of it is something a `BaseModel` can catch. [Authentication](../../security/auth/authentication.md), [authorization](../../security/authorization/authorization.md), business-rule checks, destination allowlists, and safe/idempotent execution all have to be enforced separately, in application code — critically, the requester's identity should come from a verified [token](../../security/auth/jwt.md), never from a field inside the same payload Pydantic just validated, since that field is exactly as forgeable as the rest of the tool call.

See **[Deep Dive — What Doesn't Pydantic Validate?](../../../interview/interview-01/21-pydantic-validation-boundaries-deep-dive.md)** for the full layered example (a refund tool with [authorization](../../security/authorization/authorization.md), business-rule, and idempotent-execution checks stacked after Pydantic), plus why a structured [LLM](../../ai/generation/llm.md) extraction passing validation is a shape guarantee, not proof the extracted values are actually correct.

---

## Pydantic v1 vs v2 (Quick Reference)

The codebase ecosystem is split between Pydantic v1 and v2. Pydantic v2 is the current version (rewritten in Rust, ~5–50x faster validation).

| v1 | v2 equivalent |
|---|---|
| `.dict()` | `.model_dump()` |
| `.json()` | `.model_dump_json()` |
| `.parse_obj(d)` | `.model_validate(d)` |
| `.parse_raw(s)` | `.model_validate_json(s)` |
| `.schema()` | `.model_json_schema()` |
| `@validator` | `@field_validator` |
| `@root_validator` | `@model_validator` |

[FastAPI](fastapi.md) supports both. [LangChain](../../ai/agents/langchain.md) migrated to v2. When reading older code, expect v1 method names.

---

## Common Questions

**Why use Pydantic instead of just `dict` + manual checks?**
> Type safety, automatic coercion, detailed validation errors with field paths, and automatic [JSON](../fundamentals/json.md) Schema generation. A `dict` has no schema; Pydantic makes the schema the source of truth and enforces it at runtime.

**Does Pydantic validation happen at runtime or compile time?**
> Runtime — at the moment you call `Model(...)` or `model_validate()`. Python's type hints alone are not enforced at runtime; Pydantic is what makes them load-bearing constraints rather than documentation.

**What happens when validation fails?**
> A `ValidationError` is raised containing a list of all validation errors with field path, expected type, and actual value. Never silently passes bad data through.

---

## Related

- [Data Validation](../fundamentals/data-validation.md) — the general concept Pydantic implements for Python
- [Object vs Dictionary](../fundamentals/object-vs-dict.md) — a Pydantic instance is an object (dot access, methods, schema); `.model_dump()` converts it to a plain dict
- [Serialization](../fundamentals/serialization.md) — `model_dump()` / `model_dump_json()` serialize; `model_validate()` / `model_validate_json()` deserialize
- [JSON vs Dictionary](../fundamentals/json.md) — `model_validate_json()` is the bridge: it takes a [JSON](../fundamentals/json.md) string (text) and returns a typed model instance (memory object)
- [FastAPI](fastapi.md) — built on Pydantic; every request/response body is a Pydantic model
- [Structured Output](../../ai/generation/structured-output.md) — [LLM](../../ai/generation/llm.md)-side schema enforcement that complements Pydantic's application-side enforcement
- [Validation Libraries Overview](../../../overviews/programming/validation-libraries.md) — Pydantic vs [class-validator](../../backend/api/class-validator.md) vs [Zod](../typescript/zod.md): when to choose each
- [Tool Calling](../../ai/agents/tool-calling.md) — tool argument schemas are derived from Pydantic models
- [Pydantic AI](../../ai/agents/pydantic-ai.md) — the agent framework built on top of Pydantic for type-safe LLM agent construction
- [Deep Dive — What Doesn't Pydantic Validate?](../../../interview/interview-01/21-pydantic-validation-boundaries-deep-dive.md) — the full layered-validation story: business rules, identity, [authorization](../../security/authorization/authorization.md), allowlists, and safe execution, none of which a `BaseModel` enforces
- [Authentication](../../security/auth/authentication.md) / [Authorization](../../security/authorization/authorization.md) — identity and permission checks that must run independently of, and after, Pydantic's shape validation
- [Idempotency & Double-Submit Prevention](../../backend/api/idempotency.md) — why a validated refund/payment tool call still needs an [idempotency](../../backend/api/idempotency.md) key before execution
- [Prompt Injection](../../security/attacks/prompt-injection.md) — an unexpected extra field on a tool call can be a symptom of this, which `extra="forbid"` surfaces instead of silently dropping
