# RBAC vs CASL

Both handle [authorization](../../concepts/security/authorization/authorization.md) — deciding what a user is allowed to do. [RBAC](../../concepts/security/authorization/rbac.md) checks the user's role. [CASL](../../concepts/security/authorization/casl.md) checks the role **plus conditions on the specific record being accessed**.

## The Key Difference

**[RBAC](../../concepts/security/authorization/rbac.md)** asks: *does this user's role allow this action?*
**[CASL](../../concepts/security/authorization/casl.md)** asks: *does this user's role allow this action on this specific record?*

```typescript
// RBAC — role check only
if (!user.roles.includes('editor')) throw new ForbiddenException();
// Result: ANY editor can edit ANY document

// CASL — role + record condition
can('update', 'Document', { ownerId: user.id });
ability.can('update', subject('Document', doc));
// Result: editor can only edit documents they own
```

## Side-by-Side

| | [RBAC](../../concepts/security/authorization/rbac.md) | [CASL](../../concepts/security/authorization/casl.md) |
|---|---|---|
| **Checks** | User's role | Role + conditions on the record |
| **Record context needed** | No | Yes — fetches the record to check conditions |
| **Logic lives in** | Guard / [middleware](../../concepts/backend/middleware.md) | Ability factory (centralized rule set) |
| **Complexity** | Low | Medium |
| **Best for** | Clear role boundaries | Ownership rules, field-level access |
| **NestJS integration** | `RolesGuard` + `@Roles()` decorator | `PoliciesGuard` + `AbilityFactory` |

## Decision Rule

Start with [RBAC](../../concepts/security/authorization/rbac.md). Reach for [CASL](../../concepts/security/authorization/casl.md) when you find yourself writing:

```typescript
// This is the smell — role check PLUS a record ownership check in business logic
if (user.role !== 'admin' && doc.ownerId !== user.id) {
  throw new ForbiddenException();
}
```

That condition belongs in a [CASL](../../concepts/security/authorization/casl.md) ability rule, not scattered across service methods.

## The Upgrade Path

[RBAC](../../concepts/security/authorization/rbac.md) and [CASL](../../concepts/security/authorization/casl.md) are not mutually exclusive — [CASL](../../concepts/security/authorization/casl.md) **extends** [RBAC](../../concepts/security/authorization/rbac.md) with conditions:

```typescript
// RBAC shape inside CASL — no conditions, just roles
if (user.role === 'admin') {
  can('manage', 'all');
}

// CASL addition — same role, but with a condition
if (user.role === 'editor') {
  can('read', 'Document');
  can('update', 'Document', { ownerId: user.id });   // condition added
  cannot('delete', 'Document');
}
```

You can introduce CASL into a codebase that was using plain [RBAC](../../concepts/security/authorization/rbac.md) and migrate rules incrementally.

## Common Patterns by Use Case

| Use case | Use |
|---|---|
| "Admins can delete any user" | RBAC |
| "Users can edit their own profile" | CASL with `{ userId: user.id }` condition |
| "Editors can publish documents in their department" | CASL with `{ department: user.department }` condition |
| "HR managers can see all leave requests; employees only their own" | CASL |
| "Viewers can read everything; writers can write everything" | RBAC |
| "Google-Docs-style: share a specific doc with a specific user" | [OpenFGA](../../concepts/security/authorization/openfga.md) |

## What CASL Does NOT Replace

CASL is a single-service library — rules are defined in application code and evaluated in-process. It does not work across services. If service A needs to check a permission that service B owns, you need an external [authorization](../../concepts/security/authorization/authorization.md) service like [OpenFGA](../../concepts/security/authorization/openfga.md).

## Master Overview

- [Authorization Models: RBAC vs CASL vs OpenFGA](authorization-models.md) — three-way comparison with decision flow, layered usage, and upgrade path

## Atomic Notes

- [RBAC](../../concepts/security/authorization/rbac.md) — role-based access control: assign permissions to roles, check the role at runtime
- [CASL](../../concepts/security/authorization/casl.md) — ability-based access control: RBAC + field-level conditions on records
- [OpenFGA](../../concepts/security/authorization/openfga.md) — relationship-based, cross-service fine-grained [authorization](../../concepts/security/authorization/authorization.md)
