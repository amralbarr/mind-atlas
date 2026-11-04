# Serialization

Serialization is the process of converting a data structure or object in memory into a format that can be stored or transmitted — a file, a database, an [HTTP](../../networking/http.md) body, a message queue. Deserialization is the reverse: reading that format back into a live, usable data structure. The two always come as a pair.

```
In memory (object / dict / model)
        │
        │  serialize  (json.dumps, model_dump_json, pickle.dumps...)
        ▼
Portable format (JSON string, bytes, XML, binary...)
        │
        │  deserialize  (json.loads, model_validate_json, pickle.loads...)
        ▼
In memory again (object / dict / model)
```

---

## Why It Exists

A Python object lives in your process's RAM at a specific memory address. You cannot send a memory address over a network or save it to a file — the other machine has different memory, and files have no concept of RAM. Serialization converts the **meaning** of the object (its structure and values) into a portable text or binary format any machine can reconstruct.

---

## Concrete Example

```python
import json

# In memory — exists only in this process
user = {"name": "Amr", "age": 30}

# Serialize → portable text (can be sent over HTTP, saved to file, stored in DB)
text = json.dumps(user)
# '{"name": "Amr", "age": 30}'   ← this is a string, not a dict

# Deserialize → back to a usable dict in memory
restored = json.loads(text)
# {"name": "Amr", "age": 30}     ← this is a dict again
```

---

## Common Serialization Formats

| Format | Type | Used for |
|---|---|---|
| **[JSON](json.md)** | Text | [REST](../../backend/api/rest.md) APIs, config, [LLM](../../ai/generation/llm.md) [input/output](io.md), databases |
| **[YAML](../../devops/yaml.md)** | Text | Config files ([Docker](../../containers/docker.md), [Kubernetes](../../distributed-systems/kubernetes/ingress.md), [CI/CD](../../devops/ci-cd.md)) |
| **XML** | Text | Legacy enterprise APIs, SOAP |
| **CSV** | Text | Tabular data, spreadsheet exports |
| **Protobuf** | Binary | [gRPC](../../backend/api/grpc.md), high-performance inter-service communication |
| **MessagePack** | Binary | Binary [JSON](json.md) alternative — smaller and faster |
| **Pickle** | Binary | Python-only object persistence (not safe for untrusted input) |

[JSON](json.md) is the default for web and AI work. Protobuf is preferred when bandwidth or latency matters at scale.

---

## Serialization in Pydantic

[Pydantic](../python/pydantic.md) model instances live in memory. To send one over [HTTP](../../networking/http.md) or store it, you serialize it. To receive one from an [LLM](../../ai/generation/llm.md) or API, you deserialize it.

```python
from pydantic import BaseModel

class User(BaseModel):
    name: str
    age: int

# In memory
user = User(name="Amr", age=30)

# Serialize
user.model_dump()          # → {"name": "Amr", "age": 30}   (Python dict)
user.model_dump_json()     # → '{"name": "Amr", "age": 30}' (JSON string)

# Deserialize
User.model_validate({"name": "Amr", "age": 30})        # dict → model instance
User.model_validate_json('{"name": "Amr", "age": 30}') # JSON string → model instance
```

`model_validate_json()` = deserialize + validate in one step. If the [JSON](json.md) doesn't match the schema, it raises `ValidationError` before the bad data enters your application.

---

## What Can and Cannot Be Serialized to JSON

Not every Python value has a [JSON](json.md) equivalent — see [JSON vs Dictionary](json.md) for the full breakdown. The common surprises:

```python
import json

json.dumps({"date": datetime.now()})   # ❌ TypeError — datetime has no JSON type
json.dumps({"items": {1, 2, 3}})       # ❌ TypeError — set has no JSON type
json.dumps({"value": float("inf")})    # ❌ ValueError — Infinity is not valid JSON
```

[Pydantic](../python/pydantic.md) handles these automatically when you use `model_dump_json()` — it knows how to serialize `datetime` to an ISO string, `UUID` to a string, etc.

---

## Serialization vs Encoding vs Marshalling

These terms overlap but have distinct meanings:

| Term | Meaning |
|---|---|
| **Serialization** | Converting an object to a storable/transmittable format |
| **Encoding** | Converting data to a specific byte representation (UTF-8, base64, gzip) — often a step inside serialization |
| **Marshalling** | Preparing data for transmission across a process or language boundary — includes serialization + type mapping |

In practice, "serialization" is used loosely to mean all three in most codebases.

---

## In AI Engineering

[LLMs](../../ai/generation/llm.md) produce text, not objects. Every interaction involves serialization in both directions:

```
Your code (dict / model)
    │  serialize → JSON string
    ▼
HTTP request to LLM API
    │  LLM processes, returns JSON string
    ▼
Response body (JSON string)
    │  deserialize + validate → Pydantic model
    ▼
Your code works with a typed, validated object
```

The serialization step before the [LLM](../../ai/generation/llm.md) call constructs the prompt or tool schema. The deserialization step after parses and validates the [LLM](../../ai/generation/llm.md)'s output. This is why [Pydantic](../python/pydantic.md)'s `model_validate_json()` is so central to AI engineering — it is the deserialization + validation layer at the boundary where untrusted [LLM](../../ai/generation/llm.md) output enters your typed application code.

---

## Related

- [JSON vs Dictionary](json.md) — [JSON](json.md) is one serialization format; a dict is the in-memory structure before/after
- [Pydantic](../python/pydantic.md) — `model_dump()` / `model_validate()` are [Pydantic](../python/pydantic.md)'s serialize/deserialize methods
- [Zod](../typescript/zod.md) — TypeScript equivalent: `JSON.stringify()` / `JSON.parse()` + `.parse()`
- [REST](../../backend/api/rest.md) — [HTTP](../../networking/http.md) APIs serialize request/response bodies as [JSON](json.md)
- [gRPC](../../backend/api/grpc.md) — uses Protobuf binary serialization instead of [JSON](json.md)
