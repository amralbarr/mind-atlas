# OpenFGA

An open-source Fine-Grained [Authorization](authorization.md) (FGA) system originally built by Auth0 (now Okta). Implements the Google Zanzibar [authorization](authorization.md) model — the same model that powers Google Drive's sharing permissions — and exposes it as a service your application queries at runtime to answer: "Is user X allowed to perform action Y on object Z?"

OpenFGA separates [authorization](authorization.md) logic from application code entirely. Instead of `if user.role == "admin"` scattered across your codebase, all permission decisions go through one place.

---

## The Core Question

Every [authorization](authorization.md) check answers the same question:

```
Can <user> perform <relation> on <object>?

Examples:
  Can user:alice   read    document:budget-2024?
  Can user:bob     edit    folder:hr-policies?
  Can user:carol   delete  tenant:acme-corp?
```

OpenFGA answers this question by evaluating a **relationship tuple graph** — a set of stored facts about who has what relationship to what object, combined with an **authorization model** that defines how relationships compose.

---

## Key Concepts

### Authorization Model

Defines the types of objects in your system and the relationships between them. Written in DSL:

```
model
  schema 1.1

type user

type document
  relations
    define owner: [user]
    define editor: [user] or owner
    define viewer: [user] or editor

type folder
  relations
    define owner: [user]
    define editor: [user] or owner
    define viewer: [user] or editor or viewer from parent
    define parent: [folder]
```

This model says:
- A document has `owner`, `editor`, and `viewer` relationships
- An `editor` can do anything a `viewer` can (implicit inheritance)
- A `viewer` on a folder inherits `viewer` on everything inside it (via `parent`)

---

### Relationship Tuples

Stored facts — the actual permission data. Written as `(user, relation, object)`:

```
user:alice   owner   document:budget-2024
user:bob     viewer  document:budget-2024
user:carol   editor  folder:finance
folder:finance  parent  folder:company-docs
```

These are stored in OpenFGA's own database. Your application writes tuples when permissions are granted and deletes them when revoked.

---

### Check

The runtime query: "Does this tuple hold, directly or through the model's composition rules?"

```python
# Python SDK
response = fga_client.check(
    user="user:alice",
    relation="editor",
    object="document:budget-2024",
)
# response.allowed → True (alice is owner → owner implies editor)
```

OpenFGA resolves the check by traversing the tuple graph according to the model:
- Is `user:alice editor document:budget-2024` stored directly? No.
- Is `user:alice owner document:budget-2024` stored? Yes.
- Does the model say `editor includes owner`? Yes.
- Result: `allowed: true`.

---

### ListObjects

Returns all objects of a given type a user has a specific relation to:

```python
# What documents can alice view?
response = fga_client.list_objects(
    user="user:alice",
    relation="viewer",
    type="document",
)
# response.objects → ["document:budget-2024", "document:q3-report", ...]
```

This is the complement to Check. Used for building filtered lists — "show me all documents this user can see" — without fetching everything and checking each item individually.

---

### Contextual Tuples

Temporary tuples passed with a check request rather than stored. Used for attribute-based conditions that only exist at request time:

```python
# Check if alice can approve, given that it's a working day
response = fga_client.check(
    user="user:alice",
    relation="approver",
    object="request:expense-1234",
    contextual_tuples=[
        {"user": "time:working-hours", "relation": "active", "object": "policy:approval"},
    ]
)
```

Contextual tuples allow time-based, location-based, or attribute-based access without baking that logic into the stored model.

---

## OpenFGA vs RBAC vs ABAC

| | [RBAC](rbac.md) | ABAC | OpenFGA (ReBAC) |
|---|---|---|---|
| Model | Roles assigned to users | Attributes on users/objects/environment | Relationships between users and objects |
| Example | user has role "editor" | user.department == doc.department | user is editor of this specific document |
| Granularity | Coarse (all docs or none) | Fine (attribute rules) | Fine (per-object) |
| Sharing | Hard | Complex policy expressions | Natural (tuple: user, relation, object) |
| Performance | Fast | Slow (evaluate rules per request) | Fast (indexed graph traversal) |
| Fits well | Internal tools, admin panels | Compliance/regulatory rules | Document sharing, multi-tenant SaaS |

ReBAC (Relationship-Based Access Control) is what OpenFGA implements. It models permissions the same way humans think about sharing: "Alice shared this document with Bob as a viewer."

---

## Multi-Tenant Usage

OpenFGA natively supports multi-tenancy through **stores** — each store is an isolated permission graph with its own tuples and model:

```python
# Each tenant gets its own store
acme_store_id = "01H9ZQCK5YJ9MKRKX9G8V01K0P"
globex_store_id = "01H9ZQCK5YJ9MKRKX9G8V01K0Q"

# Checks are always scoped to a store — no cross-tenant bleed
fga_client.check(
    store_id=acme_store_id,
    user="user:alice",
    relation="viewer",
    object="document:contract-2024",
)
```

On the AI Agent Platform, each enterprise tenant had its own OpenFGA store. The [RAG](../../ai/rag/rag.md) retrieval step ran a `ListObjects` check before querying the [vector database](../../ai/retrieval/vector-database.md) — ensuring the model only retrieved documents the requesting user was actually allowed to see, regardless of semantic similarity.

---

## Integration Pattern

A typical [FastAPI](../../programming/python/fastapi.md) + OpenFGA [middleware](../../backend/middleware.md):

```python
from openfga_sdk import OpenFgaClient, CheckRequest

async def check_permission(
    user_id: str,
    relation: str,
    object_id: str,
    store_id: str,
) -> bool:
    response = await fga_client.check(
        store_id=store_id,
        body=CheckRequest(
            tuple_key={"user": f"user:{user_id}", "relation": relation, "object": object_id}
        )
    )
    return response.allowed

# FastAPI dependency
async def require_viewer(
    doc_id: str,
    current_user: User = Depends(get_current_user),
):
    allowed = await check_permission(
        user_id=current_user.id,
        relation="viewer",
        object_id=f"document:{doc_id}",
        store_id=current_user.tenant_store_id,
    )
    if not allowed:
        raise HTTPException(status_code=403)
```

---

## Writing Tuples — Grant and Revoke

```python
from openfga_sdk import WriteRequest, TupleKey

# Grant: bob becomes a viewer of the document
await fga_client.write(
    store_id=store_id,
    body=WriteRequest(
        writes={"tuple_keys": [
            TupleKey(user="user:bob", relation="viewer", object="document:budget-2024")
        ]}
    )
)

# Revoke: remove bob's viewer access
await fga_client.write(
    store_id=store_id,
    body=WriteRequest(
        deletes={"tuple_keys": [
            TupleKey(user="user:bob", relation="viewer", object="document:budget-2024")
        ]}
    )
)
```

Write operations are synchronous — a subsequent Check will immediately reflect the change.

---

## OpenFGA in RAG Systems

The critical integration point is at retrieval time, not generation time. Filtering happens before documents enter the [context window](../../ai/generation/context-window.md):

```
User query
    ↓
ListObjects("viewer", "document", user=alice, store=tenant_store)
    → ["document:a", "document:b", "document:c"]  ← only what alice can see
    ↓
Vector similarity search filtered to that document set
    ↓
Top-k chunks retrieved
    ↓
LLM generates answer from those chunks only
```

If you filter after retrieval — generate an answer from all documents, then check permissions — the model may have already incorporated information from documents the user isn't allowed to see. The check must happen before retrieval.

---

## Related

- [RBAC](rbac.md) — the simpler baseline: role-only checks with no relationship graph; start here before reaching for OpenFGA
- [CASL](casl.md) — in-process ability-based authorization for single-service apps; often used alongside OpenFGA for coarse role rules
- [JWT](../auth/jwt.md) — carries the user identity that OpenFGA checks are performed against
- [Multi-Tenancy](../../backend/architecture/multi-tenancy.md) — OpenFGA stores are the per-tenant permission isolation mechanism
- [RAG](../../ai/rag/rag.md) — retrieval must be permission-filtered before documents enter the [context window](../../ai/generation/context-window.md)
- [Policy-Based Authorization](../../backend/data/policy-based-authorization.md) — the broader pattern OpenFGA implements
- [CASL vs OpenFGA — overview](../../../overviews/security/casl-vs-openfga.md) — side-by-side decision guide: in-process ownership rules vs dynamic cross-service tuple graph
- [Authorization Models: RBAC vs CASL vs OpenFGA](../../../overviews/security/authorization-models.md) — three-way master overview with decision flow, layered usage pattern, and upgrade path
