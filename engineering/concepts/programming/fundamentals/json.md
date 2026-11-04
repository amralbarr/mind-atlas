# JSON vs Dictionary

JSON and dictionaries look almost identical in Python — `{"name": "Amr", "age": 30}` — which causes persistent confusion. They are fundamentally different things: one is a **text format** for transmission and storage, the other is a **data structure** living in memory.

---

## The Core Difference

| | JSON | Dictionary (Python `dict` / JS Object) |
|---|---|---|
| **What it is** | A string — plain text | A data structure in memory |
| **Lives in** | Files, [HTTP](../../networking/http.md) bodies, databases, API responses | RAM — gone when the process ends |
| **Language** | Language-agnostic standard (RFC 8259) | Language-specific (`dict` in Python, `object` in JS) |
| **Type** | `str` in Python, `string` in JS | `dict` in Python, `object` / `Record` in JS |
| **Purpose** | Transmit or store structured data | Work with structured data in code |

```python
import json

# Dictionary — in memory, Python type
data = {"name": "Amr", "age": 30}
type(data)   # <class 'dict'>

# JSON — a string, text format
json_string = json.dumps(data)
type(json_string)   # <class 'str'>
print(json_string)  # '{"name": "Amr", "age": 30}'

# Back to dict
restored = json.loads(json_string)
type(restored)   # <class 'dict'>
```

`json.dumps()` = dict → JSON string (serialize)
`json.loads()` = JSON string → dict (deserialize / parse)

---

## Key Restrictions JSON Has That Dicts Don't

### 1. Keys must be strings (double-quoted)

```python
# Valid Python dict — any hashable key
data = {1: "one", (0, 1): "tuple key"}

# JSON requires string keys
json.dumps({1: "one"})        # → '{"1": "one"}' — silently converts int key to string
json.dumps({(0,1): "value"})  # → TypeError — tuple keys can't be serialized
```

### 2. Limited value types

JSON supports only: `string`, `number`, `boolean`, `null`, `array`, `object`

```python
import json
from datetime import datetime

data = {
    "name": "Amr",
    "created": datetime.now(),   # ❌ TypeError — datetime is not JSON-serializable
    "tags": {"a", "b"},          # ❌ TypeError — set is not JSON-serializable
    "score": float("inf"),       # ❌ ValueError — Infinity is not valid JSON
}

json.dumps(data)  # raises TypeError
```

Python types with no direct JSON equivalent:

| Python type | JSON equivalent | What `json.dumps` does |
|---|---|---|
| `int`, `float` | `number` | Serializes fine |
| `str` | `string` | Serializes fine |
| `True` / `False` | `true` / `false` | Serializes fine |
| `None` | `null` | Serializes fine |
| `list`, `tuple` | `array` | Both → `[]` (tuple loses type) |
| `dict` | `object` | Serializes fine (string keys only) |
| `datetime` | ❌ no equivalent | `TypeError` — must convert to `.isoformat()` first |
| `set` | ❌ no equivalent | `TypeError` — must convert to `list` first |
| `bytes` | ❌ no equivalent | `TypeError` — must encode (e.g. base64) first |

### 3. JSON is always a string — dict is an object

```python
response_body = '{"status": "ok"}'   # this is JSON — a string from an HTTP response

# You cannot do this:
response_body["status"]   # TypeError: string indices must be integers

# You must parse it first:
data = json.loads(response_body)
data["status"]   # "ok"
```

This is one of the most common bugs when working with APIs — receiving a JSON string and trying to access it like a dict without parsing.

---

## In JavaScript / TypeScript

The same distinction applies, but the syntax is identical for both:

```typescript
// Object (in-memory, equivalent of Python dict)
const user = { name: "Amr", age: 30 };
typeof user;   // "object"

// JSON (a string)
const jsonString = JSON.stringify(user);
typeof jsonString;   // "string"  →  '{"name":"Amr","age":30}'

// Parse back
const parsed = JSON.parse(jsonString);
typeof parsed;   // "object"
```

JS objects do not have the same key restrictions as Python dicts — keys are always strings or Symbols. JSON.stringify silently drops `undefined` values and functions, which is a common gotcha.

---

## In AI Engineering — Why This Matters

[LLMs](../../ai/generation/llm.md) return text, not data structures. When a model produces a "JSON response", what it has produced is a **string that looks like JSON**. You must parse it before you can use it.

```python
# What the LLM actually returned
llm_response = '{"tool": "search", "query": "leave policy"}'
type(llm_response)   # str — this is JSON, not a dict

# Wrong — treating a string as a dict
llm_response["tool"]   # TypeError

# Right — parse first, then use
import json
data = json.loads(llm_response)
data["tool"]   # "search"

# Better — parse + validate with Pydantic in one step
from pydantic import BaseModel

class ToolCall(BaseModel):
    tool: str
    query: str

action = ToolCall.model_validate_json(llm_response)  # parses JSON AND validates
action.tool   # "search"
```

`model_validate_json()` in [Pydantic](../python/pydantic.md) does `json.loads()` + schema validation in one call — this is the standard pattern in production AI code.

---

## Quick Mental Model

```
LLM / API / file / database
        │
        │  text (JSON string)
        ▼
    json.loads()  /  model_validate_json()
        │
        │  Python dict or Pydantic model (in memory)
        ▼
    your application logic
        │
        │  need to store or transmit?
        ▼
    json.dumps()  /  model_dump_json()
        │
        │  text (JSON string) again
        ▼
 database / HTTP response / file
```

---

## Related

- [Object vs Dictionary](object-vs-dict.md) — a dict is the in-memory Python structure; an object is a class instance — both serialize to JSON the same way
- [Serialization](serialization.md) — JSON is one [serialization](serialization.md) format; this explains the broader concept of converting objects to portable formats
- [Pydantic](../python/pydantic.md) — `model_validate_json()` parses JSON and validates schema in one step
- [Zod](../typescript/zod.md) — TypeScript equivalent: `JSON.parse()` + `.parse()` or `.safeParse()`
- [Structured Output](../../ai/generation/structured-output.md) — [LLMs](../../ai/generation/llm.md) constrained to produce valid JSON by the provider
- [REST](../../backend/api/rest.md) — [HTTP](../../networking/http.md) APIs exchange data as JSON strings in request/response bodies
