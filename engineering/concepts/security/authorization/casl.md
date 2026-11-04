# CASL

CASL (pronounced "castle") is an isomorphic [authorization](authorization.md) library for JavaScript and TypeScript that implements **ability-based access control** — it defines what a user *can* and *cannot* do, rather than what *role* they hold. "Isomorphic" means the same permission rules run on both the server (Node.js) and the client (browser) — so your UI can hide a button and your API can enforce the same rule independently.

CASL defines what a user **can** do, expressed as abilities: `can(action, subject)`. The rules are built once per user and evaluated locally — no network call per check.

A real-world use case, an HR platform: ability-based access control where different user types (HR manager, employee, approver) had different permissions over the same resources (leave requests, assessments, profiles). HR managers got `manage all`; approvers could update only pending leave requests; employees could only read and draft their own.

---

## Core Concepts

### Ability

The central object — a compiled rule set for one user. You build it once (typically after [JWT](../auth/jwt.md) verification) and pass it through your request context.

```typescript
import { AbilityBuilder, createMongoAbility } from "@casl/ability";

function defineAbilityFor(user: User) {
  const { can, cannot, build } = new AbilityBuilder(createMongoAbility);

  if (user.role === "admin") {
    can("manage", "all");               // admin can do everything
  } else if (user.role === "editor") {
    can("read", "Document");
    can("update", "Document", { tenantId: user.tenantId }); // own tenant only
    cannot("delete", "Document");
  } else {
    can("read", "Document", { tenantId: user.tenantId });   // read-only, own tenant
  }

  return build();
}
```

---

### can / cannot

The two rule primitives. `cannot` always overrides `can` — it is not order-dependent:

```typescript
can("read", "Document");           // allow reading all documents
cannot("read", "Document", { confidential: true }); // except confidential ones
```

The `cannot` rule wins even if it is defined before `can`.

---

### Subject

The resource type being accessed. Can be a string (`"Document"`) or a class constructor (`Document`). Using a class enables type-safe checks:

```typescript
import { subject } from "@casl/ability";

const doc = await db.document.findUnique({ where: { id } });
ability.can("update", subject("Document", doc));
// CASL evaluates conditions (e.g. tenantId match) against the real doc object
```

Passing the actual object (not just the type string) lets CASL evaluate field-level conditions — "can update this specific document" rather than "can update documents in general."

---

### Conditions

Field-level constraints on when a rule applies. Uses [MongoDB](../../databases/nosql/mongodb.md) query syntax:

```typescript
can("read", "Document", { tenantId: user.tenantId });
// User can only read documents where document.tenantId === user.tenantId

can("update", "Document", { authorId: user.id, status: { $in: ["draft", "review"] } });
// User can only update their own documents that are in draft or review status
```

Conditions are evaluated locally against the object passed to `ability.can()`. They can also be translated to database WHERE clauses using `@casl/prisma` or `@casl/mongoose`.

---

## Checking Permissions

```typescript
// Simple type-level check (no conditions evaluated)
ability.can("read", "Document");          // true/false

// Object-level check (conditions evaluated against real object)
ability.can("update", subject("Document", doc));  // checks tenantId, status, etc.

// Throw if not allowed
import { ForbiddenError } from "@casl/ability";
ForbiddenError.from(ability).throwUnlessCan("delete", subject("Document", doc));
// throws ForbiddenError if not allowed
```

---

## NestJS Integration

CASL integrates cleanly with NestJS via a custom guard:

```typescript
// ability.factory.ts — build the ability from the JWT user
@Injectable()
export class AbilityFactory {
  createForUser(user: JwtUser): AppAbility {
    const { can, cannot, build } = new AbilityBuilder<AppAbility>(createMongoAbility);

    if (user.role === "admin") {
      can("manage", "all");
    } else {
      can("read", "Document", { tenantId: user.tenantId });
      can("create", "Document", { tenantId: user.tenantId });
      can("update", "Document", { tenantId: user.tenantId, authorId: user.id });
    }

    return build({ detectSubjectType: (item) => item.__caslSubjectType__ });
  }
}

// policies.guard.ts — enforce policies on routes
@Injectable()
export class PoliciesGuard implements CanActivate {
  constructor(
    private reflector: Reflector,
    private abilityFactory: AbilityFactory,
  ) {}

  canActivate(context: ExecutionContext): boolean {
    const policyHandlers = this.reflector.get<PolicyHandler[]>(
      CHECK_POLICIES_KEY,
      context.getHandler(),
    );
    const { user } = context.switchToHttp().getRequest();
    const ability = this.abilityFactory.createForUser(user);

    return policyHandlers.every((handler) => handler(ability));
  }
}

// Usage on a controller
@UseGuards(JwtAuthGuard, PoliciesGuard)
@CheckPolicies((ability) => ability.can("delete", "Document"))
@Delete(":id")
async deleteDocument(@Param("id") id: string) { ... }
```

---

## Isomorphic Use — Frontend

The same ability definition runs in the browser. Build the ability from the user's [JWT](../auth/jwt.md) claims (never trust client-side permissions for server enforcement — this is purely UI gating):

```typescript
// React hook
function useAbility(user: User) {
  return useMemo(() => defineAbilityFor(user), [user]);
}

// Component
function DocumentActions({ doc }: { doc: Document }) {
  const ability = useAbility(useCurrentUser());

  return (
    <div>
      {ability.can("update", subject("Document", doc)) && <EditButton />}
      {ability.can("delete", subject("Document", doc)) && <DeleteButton />}
    </div>
  );
}
```

The API must enforce the same rules independently — the client-side check is a UX convenience, not a security boundary.

---

## CASL vs Plain RBAC vs OpenFGA

| | CASL | Plain [RBAC](rbac.md) | [OpenFGA](openfga.md) |
|---|---|---|---|
| Where logic lives | Application code (ability factory) | DB roles table + [middleware](../../backend/middleware.md) | External [authorization](authorization.md) service |
| Conditions on records | Yes (field-level, [MongoDB](../../databases/nosql/mongodb.md) query syntax) | No | Yes (relationship-based) |
| Evaluation | In-process, no network call | In-process | Network call per check (~5–20ms) |
| Rule complexity | Code — flexible but coupled to deploy | Low | DSL model — decoupled, runtime-updateable |
| Sharing / delegation | Hard (requires a deploy to change rules) | Hard | Natural (write a tuple: user, relation, object) |
| Audit trail | No built-in | No built-in | Full tuple history |
| Scale | Per-service, per-language | Per-service | Centralized across services |
| Complexity | Medium | Low | High |
| Best for | Single-service apps with complex ownership rules | Simple role checks | Multi-service, fine-grained relationship graphs |
| Real-world usage | HR platform | — | CRM ([OpenFGA](openfga.md)) |

In practice, CASL and [OpenFGA](openfga.md) are often used together: CASL enforces coarse role-based rules in the NestJS API, while [OpenFGA](openfga.md) handles fine-grained document-level sharing that changes at runtime.

---

## Database Integration — @casl/prisma

CASL conditions can be translated to Prisma WHERE clauses, so permission filtering happens at the database query, not in-memory:

```typescript
import { accessibleBy } from "@casl/prisma";

// Instead of fetching all docs and filtering in code:
const docs = await prisma.document.findMany({
  where: accessibleBy(ability).Document,
  // Generates: WHERE tenantId = 'acme-corp' (from the ability's conditions)
});
```

This is important for performance and correctness — never fetch more data than the user is allowed to see.

---

## Common Mistake: Skipping `subject()` on Instance Checks

When you define a rule with field-level conditions — `can('update', 'LeaveRequest', { userId: user.id })` — those conditions are only evaluated if you pass the actual record wrapped in `subject()`. Passing just the string type name silently ignores the conditions:

```typescript
// WRONG — condition { userId: user.id } is ignored, always passes the type check
ability.can('update', 'LeaveRequest')

// CORRECT — fetches the record first, then checks the actual userId field
const leaveRequest = await this.leaveRequestService.findById(id);
ability.can('update', subject('LeaveRequest', leaveRequest))
```

This is the single most common CASL bug: the type-level check passes, access is granted, but the ownership condition was never enforced. Always use `subject()` when field-level conditions matter.

---

## Related

- [RBAC](rbac.md) — the simpler baseline: role checks only, no record-level conditions; start here before reaching for CASL
- [OpenFGA](openfga.md) — the complementary system for dynamic, relationship-based permissions (runtime-updateable, multi-service)
- [JWT](../auth/jwt.md) — carries the user claims that `defineAbilityFor()` reads to build the ability
- [Multi-Tenancy](../../backend/architecture/multi-tenancy.md) — CASL conditions enforce tenant isolation at the query level
- [Policy-Based Authorization](../../backend/data/policy-based-authorization.md) — the broader pattern both CASL and [OpenFGA](openfga.md) implement
- [RBAC vs CASL — overview](../../../overviews/security/rbac-vs-casl.md) — side-by-side comparison, decision rule, and upgrade path
- [CASL vs OpenFGA — overview](../../../overviews/security/casl-vs-openfga.md) — when in-process ownership rules are enough vs when you need a dynamic, cross-service permission graph
- [Authorization Models: RBAC vs CASL vs OpenFGA](../../../overviews/security/authorization-models.md) — three-way master overview with decision flow, layered usage pattern, and upgrade path
