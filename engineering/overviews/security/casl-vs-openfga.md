# CASL vs OpenFGA

Both handle fine-grained [authorization](../../concepts/security/authorization/authorization.md) — permissions that depend on the specific record, not just the user's role. They solve the same problem with fundamentally different architectures.

## The Same Problem, Two Approaches

**Scenario:** An editor should only be able to edit documents they own. Another user shares a specific document with a third user as a viewer.

```
CASL answer:
  can('update', 'Document', { ownerId: user.id })    // rule in code
  ability.can('update', subject('Document', doc))     // checked in-process

OpenFGA answer:
  Write tuple: (user:alice, editor, document:42)      // stored in OpenFGA
  Check: Can user:alice edit document:42?             // queried at runtime
```

## Side-by-Side

| | [CASL](../../concepts/security/authorization/casl.md) | [OpenFGA](../../concepts/security/authorization/openfga.md) |
|---|---|---|
| **Where rules live** | Application code (ability factory) | External service ([OpenFGA](../../concepts/security/authorization/openfga.md) store) |
| **Where checks run** | In-process (no network call) | Network call to [OpenFGA](../../concepts/security/authorization/openfga.md) service |
| **Permissions stored** | In code (static rules) | In a database (dynamic tuples) |
| **Grant/revoke at runtime** | Redeploy the ability factory | Write/delete a tuple — instant |
| **Works across services** | No — single service only | Yes — any service queries the same store |
| **Sharing model** | Ownership conditions on fields | Explicit relationship tuples per object |
| **Complexity** | Medium | High |
| **Latency** | Zero (in-process) | Network round-trip per check |
| **Real-world usage** | HR Platform (leave requests) | AI Agent Platform (document access per tenant) |

## Decision Rule

**Use [CASL](../../concepts/security/authorization/casl.md) when:**
- [Authorization](../../concepts/security/authorization/authorization.md) logic is ownership-based: "users manage their own records"
- All checks happen within a single service
- Permissions are static (do not change without a deploy)
- You want zero latency on auth checks

**Use [OpenFGA](../../concepts/security/authorization/openfga.md) when:**
- Users can share specific objects with specific other users (Google Docs model)
- Multiple services need to check the same permissions
- Permissions change at runtime (a user grants access to a colleague without a deploy)
- You need `ListObjects` — "show me everything this user can see" — for filtering queries

## The Sharing Test

The clearest dividing line: **can a non-admin user grant another user access to a specific object?**

```
"Alice shares document:budget with Bob as viewer"
```

- [CASL](../../concepts/security/authorization/casl.md): cannot model this cleanly — rules are in code, not per-object data
- [OpenFGA](../../concepts/security/authorization/openfga.md): one tuple write: `(user:bob, viewer, document:budget)` — done

If your system needs user-driven sharing, you need [OpenFGA](../../concepts/security/authorization/openfga.md).

## They Can Be Used Together

[CASL](../../concepts/security/authorization/casl.md) handles coarse role checks (fast, in-process). [OpenFGA](../../concepts/security/authorization/openfga.md) handles fine-grained object-level sharing (dynamic, cross-service). Using both is valid:

```
Request arrives
    ↓
JWT guard — verify token, extract user + roles
    ↓
CASL guard — does this role allow this action type at all?
  (e.g. only editors and above can touch documents)
    ↓
OpenFGA check — does this user have access to THIS specific document?
  (e.g. was it shared with them, or do they own it?)
    ↓
Handler runs
```

[CASL](../../concepts/security/authorization/casl.md) is the cheap first gate. OpenFGA is the precise second gate. Only failing requests reach the OpenFGA network call.

## Upgrade Path

```
RBAC → "admins can delete, editors can edit, viewers can read"
  ↓ (ownership needed)
CASL → "editors can edit their OWN documents"
  ↓ (user-driven sharing needed, or cross-service)
OpenFGA → "Alice shared document:X with Bob as viewer"
```

Each step is a response to a real requirement, not a default starting point.

## Master Overview

- [Authorization Models: RBAC vs CASL vs OpenFGA](authorization-models.md) — three-way comparison with decision flow, layered usage, and upgrade path

## Atomic Notes

- [CASL](../../concepts/security/authorization/casl.md)
- [OpenFGA](../../concepts/security/authorization/openfga.md)
- [RBAC](../../concepts/security/authorization/rbac.md)
- [RBAC vs CASL](rbac-vs-casl.md)
