# RBAC — Role-Based Access Control

RBAC is the most common [authorization](authorization.md) pattern: assign users to **roles**, assign **permissions** to roles, check the role at runtime. A user gets permissions indirectly through their role, not directly.

```
User → Role → Permissions
amr  → admin → [read, write, delete]
sara → viewer → [read]
```

---

## Core Model

| Entity | Description |
|---|---|
| **User** | The authenticated identity |
| **Role** | A named group of permissions (`admin`, `editor`, `viewer`) |
| **Permission** | An allowed action on a resource (`read:document`, `delete:user`) |
| **Assignment** | A user has one or more roles |

---

## Implementation Patterns

### 1. Role stored in JWT (stateless)

The role is embedded in the token at login — no DB call per request:

```typescript
// JWT payload
{ "sub": "user_123", "roles": ["editor", "viewer"] }

// Guard in NestJS
@Injectable()
export class RolesGuard implements CanActivate {
  constructor(private reflector: Reflector) {}

  canActivate(context: ExecutionContext): boolean {
    const requiredRoles = this.reflector.get<string[]>('roles', context.getHandler());
    if (!requiredRoles) return true;

    const { user } = context.switchToHttp().getRequest();
    return requiredRoles.some(role => user.roles.includes(role));
  }
}

// Usage
@Roles('admin', 'editor')
@UseGuards(JwtAuthGuard, RolesGuard)
@Patch(':id')
update() { ... }
```

### 2. Role stored in DB (stateful)

Role is looked up from the database on each request — allows instant revocation and role changes without waiting for token expiry:

```prisma
model User {
  id    String @id @default(cuid())
  email String @unique
  roles UserRole[]
}

model Role {
  id          String       @id @default(cuid())
  name        String       @unique   // "admin", "editor", "viewer"
  permissions Permission[]
  users       UserRole[]
}

model UserRole {
  userId String
  roleId String
  user   User   @relation(fields: [userId], references: [id])
  role   Role   @relation(fields: [roleId], references: [id])
  @@id([userId, roleId])
}
```

### 3. Flat role check (simplest)

For simple systems with few roles — check directly in the service:

```typescript
if (!['admin', 'manager'].includes(user.role)) {
  throw new ForbiddenException();
}
```

---

## RBAC vs ABAC vs CASL vs OpenFGA

| Model | What controls access | Condition on records | Complexity | Best for |
|---|---|---|---|---|
| **RBAC** | Role (`admin`, `viewer`) | No — role only | Low | Most apps — clear role boundaries |
| **ABAC** | Attributes (user + resource + environment) | Yes — any attribute | High | Complex policy engines (OPA, [AWS](../../cloud/infrastructure/aws.md) IAM) |
| **[CASL](casl.md)** | Ability rules in code (`can/cannot` + conditions) | Yes — field-level conditions | Medium | Single-service apps with ownership rules |
| **[OpenFGA](openfga.md)** | Relationship graph (`user:X is editor of doc:Y`) | Yes — relationship-based | High | Multi-service fine-grained [authorization](authorization.md) |

**Use RBAC when:** roles map cleanly to what users can do and you do not need record-level conditions ("an editor can edit *their own* documents only" requires [CASL](casl.md) or ABAC).

**Use [CASL](casl.md) when:** you need RBAC's simplicity but also ownership conditions — "editor can update documents where `ownerId === user.id`".

**Use [OpenFGA](openfga.md) when:** you need Google-Docs-style sharing ("this specific document is shared with this specific user") across multiple services.

---

## Common Mistakes

**Checking roles in the wrong layer:**
```typescript
// WRONG — business logic deciding auth
if (user.role === 'admin' || (user.role === 'editor' && doc.ownerId === user.id)) {
  // ... scattered across service methods
}

// CORRECT — centralized in a guard or ability factory
// Business logic never checks roles directly
```

**Stale role in [JWT](../auth/jwt.md):** a role change (e.g. demoting an admin) does not take effect until the token expires. Fix with `tokenVersion` pattern or a short token TTL + refresh. See [JWT — Stale Claims](../auth/jwt.md#stale-claims-a-different-problem-from-revocation).

**Too many roles:** roles like `senior_editor_with_publish_rights` are a sign the model needs hierarchical roles or ABAC conditions, not more flat roles.

---

## Hierarchical RBAC

Roles can inherit from other roles:

```
superadmin
  └── admin
        └── editor
              └── viewer
```

A user with `editor` automatically has `viewer` permissions. Implemented in NestJS with a role hierarchy map:

```typescript
const roleHierarchy = {
  superadmin: ['admin', 'editor', 'viewer'],
  admin: ['editor', 'viewer'],
  editor: ['viewer'],
  viewer: [],
};

function hasRole(userRole: string, requiredRole: string): boolean {
  return userRole === requiredRole || roleHierarchy[userRole]?.includes(requiredRole);
}
```

---

## Related

- [CASL](casl.md) — ability-based access control: RBAC + record-level conditions
- [OpenFGA](openfga.md) — relationship-based access control for fine-grained sharing
- [JWT](../auth/jwt.md) — roles embedded in token claims
- [Access Control & IAM](access-control-iam.md)
- [Guards](../../backend/nestjs/guards.md)
- [RBAC vs CASL — overview](../../../overviews/security/rbac-vs-casl.md) — side-by-side comparison, decision rule, and upgrade path
- [Authorization Models: RBAC vs CASL vs OpenFGA](../../../overviews/security/authorization-models.md) — three-way master overview with decision flow, layered usage pattern, and upgrade path
