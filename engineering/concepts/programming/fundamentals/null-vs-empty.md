# Null vs Empty

`null` and empty look similar — both feel like "nothing" — but they mean different things. `null` means the value does not exist. Empty means the value exists but contains nothing. Treating them as the same loses information and causes bugs.

---

## The Core Difference

```python
name = None   # null  — no name was provided, unknown, not applicable
name = ""     # empty — a name was provided, and it's a blank string

items = None  # null  — the list hasn't been loaded or set yet
items = []    # empty — the list was loaded, and it has zero items
```

---

## The 3 States to Distinguish

```python
user_bio = None    # never set — user hasn't filled in their bio yet
user_bio = ""      # set to blank — user opened the form and saved nothing
user_bio = "AI engineer based in Riyadh"   # set with content
```

These mean different things in a real system:

| Value | Meaning | What to show |
|---|---|---|
| `None` | Bio never provided | "Bio not yet added" |
| `""` | Bio explicitly cleared | Blank bio field |
| `"AI engineer..."` | Bio has content | Display the bio |

Collapsing `None` and `""` into one case loses the distinction between "never set" and "explicitly cleared" — important for UI, auditing, and partial update logic.

---

## By Type

| Type | Null / None | Empty |
|---|---|---|
| `str` | `None` | `""` |
| `list` | `None` | `[]` |
| `dict` | `None` | `{}` |
| `int` | `None` | `0` — a valid value, not truly "empty" |
| `bool` | `None` | `False` — a valid value, not truly "empty" |

`0` and `False` are not empty — they are valid values that happen to be falsy. This distinction matters.

---

## The Falsy Trap

Python treats `None`, `""`, `[]`, `{}`, `0`, and `False` all as falsy — `if not x` passes for all of them:

```python
score = 0

if not score:           # ❌ treats 0 the same as None — both are falsy
    print("no score")   # prints — but 0 IS a meaningful score

if score is None:       # ✅ only True when genuinely missing
    print("no score")
```

```python
active = False

if not active:                    # ❌ could be None or False — ambiguous
    print("no active value set")

if active is None:                # ✅ explicitly missing
    print("no active value set")
```

**Rule:** use `is None` / `is not None` to check for null. Never use `if not x` when `0`, `False`, or `""` are valid values.

---

## In Databases (SQL)

```sql
-- NULL — the value is unknown or not applicable
-- Empty string — the value is known and is a blank string

SELECT * FROM users WHERE bio IS NULL;     -- never filled in
SELECT * FROM users WHERE bio = '';        -- filled in with nothing
SELECT * FROM users WHERE bio IS NOT NULL; -- has any value, including ''
```

[SQL](../../databases/relational/sql.md) `NULL` is not equal to anything — not even itself:

```sql
NULL = NULL    -- evaluates to NULL (not TRUE) — use IS NULL
NULL != NULL   -- also NULL
```

This is why `WHERE column = NULL` never matches any rows — always write `WHERE column IS NULL`.

---

## In JSON

```json
{ "name": null }   // null — key exists, value is null
{ "name": "" }     // empty string — key exists, value is blank
{  }               // key absent — different from null in many APIs
```

Three distinct states. Many [REST](../../backend/api/rest.md) APIs differentiate:
- **Absent key** → don't update this field (PATCH semantics)
- **`null`** → explicitly clear this field
- **`""`** → set this field to a blank string

---

## In Python — `None` and `Optional`

```python
from typing import Optional

def greet(name: Optional[str] = None) -> str:
    if name is None:
        return "Hello, guest"
    if name == "":
        return "Hello,"          # name provided but blank — different case
    return f"Hello, {name}"
```

`Optional[str]` is shorthand for `str | None` — the field can be a string or absent entirely.

---

## In Pydantic

```python
from pydantic import BaseModel
from typing import Optional

class Profile(BaseModel):
    bio: Optional[str] = None    # None = not provided, "" = provided but blank

Profile(bio=None)   # null  — bio not set
Profile(bio="")     # empty — bio set to blank
Profile()           # defaults to bio=None
```

[Pydantic](../python/pydantic.md) preserves the distinction — it will not coerce `None` to `""` or vice versa unless you explicitly write a validator to do so.

---

## In JavaScript / TypeScript

JS adds a third case — `undefined`:

| Value | Meaning |
|---|---|
| `null` | Explicitly set to nothing |
| `undefined` | Never assigned — variable declared but not set |
| `""` | Empty string — a value that is blank |

```typescript
let name: string | null | undefined;

name = undefined;   // never set
name = null;        // explicitly cleared
name = "";          // set to blank
name = "Amr";       // set with content

// Null-safe check
if (name == null) { ... }   // catches both null and undefined (loose equality)
if (name === null) { ... }  // catches only null (strict equality)
if (name === undefined) { ... }  // catches only undefined
```

TypeScript's optional field syntax (`name?:`) produces `undefined` when the field is absent, not `null`.

---

## Related

- [Object vs Dictionary](object-vs-dict.md) — null values in objects vs missing keys in dicts
- [Pydantic](../python/pydantic.md) — `Optional[str]` and how [Pydantic](../python/pydantic.md) handles null vs empty in validation
- [JSON vs Dictionary](json.md) — [JSON](json.md) `null`, absent keys, and empty strings as three distinct states
- [SQL](../../databases/relational/sql.md) — NULL behavior in [SQL](../../databases/relational/sql.md): IS NULL, NOT NULL constraints, NULL in aggregates
