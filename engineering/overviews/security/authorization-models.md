# Authorization Models: RBAC vs CASL vs OpenFGA

Three authorization models in increasing order of power and complexity. Each is the right answer for a different set of requirements.

## One-Line Summary

| Model | One line |
|---|---|
| **[RBAC](../../concepts/security/authorization/rbac.md)** | User has a role → role has permissions |
| **[CASL](../../concepts/security/authorization/casl.md)** | User can/cannot do action on subject — with optional record-level conditions |
| **[OpenFGA](../../concepts/security/authorization/openfga.md)** | User has a relationship to a specific object — evaluated against a graph |

## Full Comparison

|                                       | [RBAC](../../concepts/security/authorization/rbac.md)                                                         | [CASL](../../concepts/security/authorization/casl.md)                                          | [OpenFGA](../../concepts/security/authorization/openfga.md)                                                 |
| ------------------------------------- | ------------------------------------------------------------ | --------------------------------------------- | ------------------------------------------------------- |
| **Core question**                     | What role does this user have?                               | Can this user do X — on this specific record? | Does this user have relation Y to object Z?             |
| **Rules live in**                     | Code / DB role table                                         | Application code (ability factory)            | External service (tuple store)                          |
| **Record-level conditions**           | No                                                           | Yes — field conditions in code                | Yes — per-object tuples                                 |
| **User-driven sharing**               | No                                                           | No                                            | Yes                                                     |
| **Works across services**             | Via shared [JWT](../../concepts/security/auth/jwt.md) claims | No — single service                           | Yes — any service queries the store                     |
| **Permissions change without deploy** | Role assignment (yes) / rules (no)                           | No                                            | Yes — write a tuple                                     |
| **Network call per check**            | No                                                           | No                                            | Yes                                                     |
| **Complexity**                        | Low                                                          | Medium                                        | High                                                    |
| **Best for**                          | Internal tools, admin panels, clear role boundaries          | Ownership rules in a single service           | Document sharing, multi-tenant SaaS, cross-service auth |

## The Decision Flow

```
Does every user of a role get the same access to all records of a type?
    YES → RBAC is enough
    NO  ↓

Does access depend on who owns or created the record?
    YES, and rules are static in code → CASL
    NO  ↓

Do users need to share specific objects with specific other users,
or do multiple services need to check the same permissions?
    YES → OpenFGA
```

## Code Shape

**[RBAC](../../concepts/security/authorization/rbac.md) — role in [JWT](../../concepts/security/auth/jwt.md), checked in guard:**
```typescript
@Roles('admin', 'editor')
@UseGuards(JwtAuthGuard, RolesGuard)
@Patch(':id')
update() { ... }
// ANY admin or editor can update ANY record
```

**[CASL](../../concepts/security/authorization/casl.md) — ability with conditions:**
```typescript
can('update', 'Document', { ownerId: user.id });
// ...
ability.can('update', subject('Document', doc));
// Editor can only update THEIR OWN documents
```

**[OpenFGA](../../concepts/security/authorization/openfga.md) — tuple stored, queried at runtime:**
```typescript
// When Alice shares a doc with Bob:
await fga.write({ user: 'user:bob', relation: 'viewer', object: 'document:42' });

// At request time:
const { allowed } = await fga.check({
  user: `user:${req.user.id}`,
  relation: 'viewer',
  object: `document:${docId}`,
});
// Bob can view document:42 — Alice granted it at runtime, no deploy needed
```

## Real-World Examples

| Requirement | Model used | Why |
|---|---|---|
| HR managers see all leave requests; employees see only their own | **[CASL](../../concepts/security/authorization/casl.md)** | Ownership condition on a single service |
| CRM: each tenant's data isolated; users share cases across teams | **[OpenFGA](../../concepts/security/authorization/openfga.md)** | Per-object sharing + multi-tenant graph |
| [RAG](../../concepts/ai/rag/rag.md) platform: [JWT](../../concepts/security/auth/jwt.md)-authenticated API access | **[RBAC](../../concepts/security/authorization/rbac.md)** (via [JWT](../../concepts/security/auth/jwt.md) claims) | Role-level access, no record conditions needed at the API layer |
| [RAG](../../concepts/ai/rag/rag.md) retrieval: filter documents by user's permitted access level | **[RBAC](../../concepts/security/authorization/rbac.md)** (metadata filter) | `access_level` claim in [JWT](../../concepts/security/auth/jwt.md) → pre-filter before vector search |

## Using Them Together

The three models are not mutually exclusive. A production system often uses all three in layers:

```
Request
  ↓
JWT guard         — RBAC: does this role allow this action class at all?
  ↓
CASL guard        — ownership: is this the user's own record?
  ↓
OpenFGA check     — sharing: was this specific object shared with this user?
  ↓
Handler
```

Each gate is cheaper than the next. [RBAC](../../concepts/security/authorization/rbac.md) fails fast with no DB call. [CASL](../../concepts/security/authorization/casl.md) fails fast in-process. [OpenFGA](../../concepts/security/authorization/openfga.md) only runs for requests that passed the first two gates.

## The Upgrade Path

```
Start here:
  RBAC → "admins can publish; editors can draft; viewers can read"

Add when you need ownership rules:
  CASL → "editors can edit their OWN drafts"

Add when you need user-driven sharing or cross-service auth:
  OpenFGA → "Alice shared document:X with Bob as a viewer"
```

Never start with [OpenFGA](../../concepts/security/authorization/openfga.md) for a problem [RBAC](../../concepts/security/authorization/rbac.md) solves — it adds operational overhead (running a service, managing tuple storage) that is only justified when the sharing model demands it.

## Pair Overviews
- [RBAC vs CASL](rbac-vs-casl.md)
- [CASL vs OpenFGA](casl-vs-openfga.md)

## Atomic Notes
- [RBAC](../../concepts/security/authorization/rbac.md)
- [CASL](../../concepts/security/authorization/casl.md)
- [OpenFGA](../../concepts/security/authorization/openfga.md)
