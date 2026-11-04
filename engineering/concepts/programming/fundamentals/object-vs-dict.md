# Object vs Dictionary

A dictionary and an object can hold the same data, but they are fundamentally different: a dict is a data container with no fixed shape, an object is a class instance with a defined structure and behavior. The confusion is sharpest in Python (where both are common) and JavaScript (where a plain object `{}` doubles as a dict).

---

## Python

### Dictionary — untyped key-value container

```python
user = {"name": "Amr", "age": 30}

user["name"]       # access by string key
user["typo"]       # KeyError — only caught at runtime
user["anything"] = 99  # any key accepted — no schema enforced
```

No fixed shape. No behavior. No IDE autocomplete on keys. The structure is implicit — you have to read the code to know what keys exist.

### Object — class instance with defined structure

```python
class User:
    def __init__(self, name: str, age: int):
        self.name = name
        self.age = age

    def greet(self) -> str:
        return f"Hi, I'm {self.name}"

user = User("Amr", 30)

user.name        # dot access — IDE knows this attribute exists
user.greet()     # has behavior — a dict cannot have methods
user["name"]     # ❌ TypeError — objects use dot notation, not brackets
```

Fixed shape defined by `__init__`. Has methods. IDE autocompletes `.name`, `.age`, `.greet()`.

---

## The 4 Key Differences

|                   | `dict`                            | Object (class instance)                    |
| ----------------- | --------------------------------- | ------------------------------------------ |
| **Access syntax** | `d["key"]` — string key           | `obj.attribute` — dot notation             |
| **Structure**     | No fixed shape — any key accepted | Defined by the class — known at write time |
| **Behavior**      | No methods beyond built-ins       | Has methods — encapsulates logic with data |
| **IDE support**   | No autocomplete on keys           | Full autocomplete on attributes            |

---

## In JavaScript / TypeScript

JavaScript has no separate `dict` type — a plain object `{}` serves as both:

```js
// Plain object — used like a Python dict
const user = { name: "Amr", age: 30 }
user.name       // dot access
user["name"]    // bracket access — both work on plain objects

// Class instance — used like a Python object
class User {
  constructor(name, age) {
    this.name = name
    this.age = age
  }
  greet() { return `Hi, I'm ${this.name}` }
}
const user = new User("Amr", 30)
user.greet()    // has behavior
```

In TypeScript, the distinction is made explicit with types:

```typescript
// Plain object — typed as a Record or interface
const user: Record<string, unknown> = { name: "Amr", age: 30 }

// Class instance — typed as the class
const user: User = new User("Amr", 30)

// Interface — describes shape of a plain object (no class needed)
interface User {
  name: string
  age: number
}
const user: User = { name: "Amr", age: 30 }
```

**Why Python devs get confused:** In Python `{}` always means dict. In JS/TS `{}` means plain object — there is no dict keyword.

---

## Pydantic: The Best of Both

A [Pydantic](../python/pydantic.md) `BaseModel` gives you an object with the fixed structure of a class AND easy conversion to/from a dict:

```python
from pydantic import BaseModel

class User(BaseModel):
    name: str
    age: int

# Create — validates on construction
user = User(name="Amr", age=30)

# Object access
user.name          # "Amr"   — dot notation, IDE autocomplete
user.age           # 30

# Not a dict
user["name"]       # ❌ TypeError

# Convert to dict when needed
user.model_dump()  # {"name": "Amr", "age": 30}
```

Use a [Pydantic](../python/pydantic.md) model (object) when the shape matters and must be enforced.
Use a plain dict when the shape is dynamic or unknown at write time.

---

## When to Use Which

| Situation | Use |
|---|---|
| Shape is fixed and known — API response, tool call args, [LLM](../../ai/generation/llm.md) output | Object / [Pydantic](../python/pydantic.md) model |
| Shape is dynamic — arbitrary metadata, config the code doesn't own | `dict` |
| Need methods alongside data | Object |
| Passing to `json.dumps()` directly | `dict` (or call `.model_dump()` first) |
| Validating data from an untrusted source ([LLM](../../ai/generation/llm.md), user, API) | [Pydantic](../python/pydantic.md) model |
| Intermediate accumulation before structure is decided | `dict` |

---

## Related

- [Pydantic](../python/pydantic.md) — gives objects validation, schema, and dict conversion in one
- [JSON vs Dictionary](json.md) — [JSON](json.md) is the serialized text form of a dict; objects must be converted to dict first
- [Serialization](serialization.md) — objects are serialized to dict/[JSON](json.md) for storage or transmission
- [OOP](oop.md) — objects, classes, and the principles behind class-based design
