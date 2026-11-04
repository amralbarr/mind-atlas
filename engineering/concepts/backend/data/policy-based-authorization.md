# Policy-Based Authorization

As a system grows past a handful of endpoints, scattering [authorization](../../security/authorization/authorization.md) checks (`if (user.role === 'admin' || resource.ownerId === user.id) ...`) inline across every controller/service method becomes its own source of bugs — not because any single check is wrong, but because there's no single place that guarantees every code path has one at all.

## The Scattered-Checks Failure Mode

Inline, per-endpoint [authorization](../../security/authorization/authorization.md) checks have to be remembered *every time* a new mutating or data-returning endpoint is added. The failure mode when someone forgets is **silent over-permission** — the new endpoint simply has no check, and the bug surfaces only when someone notices unauthorized access has been possible, often much later and often via an incident rather than a code review catching it.

## The Fix: One Policy Function, Called Everywhere

Centralize the decision into a single function every code path calls through — often shaped as `authorize(principal, action, resource?)` — that:

1. Normalizes "who/what is calling" into one consistent shape (a **principal**) regardless of *how* they authenticated (session login, [API key](../../security/auth/api-key.md), a scoped third-party token) — so the policy logic doesn't need to know or care which auth method produced this caller.
2. Encodes every permission rule as an explicit, named check inside that one function.
3. **Defaults to deny** — every branch must explicitly grant; nothing falls through to "allowed" by omission. This single property is what turns "someone forgot to add a check" from a silent security hole into a request that simply fails (safe direction) rather than one that silently succeeds (unsafe direction).

## Defense in Depth: A Structural Layer on Top of the Function

Centralizing the *logic* into one function doesn't yet guarantee every code path actually *calls* it — that still relies on the discipline of whoever writes the next endpoint. A second, structural layer closes that gap: a route-level guard or [middleware](../middleware.md) that **refuses to serve any route that hasn't explicitly declared what permission it requires** (often via a decorator or route metadata). A new endpoint added without that declaration becomes unreachable — a build-time or request-time failure — rather than silently unprotected. This is the same "default deny" principle applied one layer higher: the object-level policy function still runs for the fine-grained ownership/resource check once data is loaded, but the route-level guard is what guarantees that function was even in the call path to begin with.

| Layer | Catches |
|---|---|
| Route-level guard (default-deny) | "This endpoint has no declared permission requirement at all" |
| Policy function (`authorize()`) | "This specific caller isn't allowed to do this specific thing to this specific resource" |

The two layers are complementary, not redundant — one is a structural safety net, the other is the actual business logic of who can do what.

## Real-World Example

A real third-party embeddable-widget design replaces a design that had proposed per-endpoint `if (authMethod === 'embed' && ...)` branches with exactly this pattern: a normalized `Principal` type computed once per request regardless of auth method, a single `authorize(principal, action, resource)` function every service method calls as its first line, and — added after a security review pointed out that centralizing the logic alone doesn't force every future endpoint to call it — a route-level guard that rejects any route missing its declared action metadata, making a forgotten check unreachable instead of silently unrestricted.

## Common Questions

**Isn't a single policy function a performance bottleneck or a "god function" code smell?**
> Not in practice — the function itself can be a short dispatch over a handful of named rules, and the alternative (the same rules duplicated across every call site) is worse for both correctness and maintainability. This is the same "one seam, not scattered checks" principle behind [centralized multi-tenant query filtering](../architecture/multi-tenancy.md).

**Does default-deny mean every new feature needs an explicit rule written before it works at all?**
> Yes, deliberately — that friction is the point. It converts "I forgot to add an [authorization](../../security/authorization/authorization.md) check" from a silent vulnerability into a feature that visibly doesn't work until someone adds the rule, which gets caught in normal testing rather than discovered as an incident.

## Related

- [Multi-Tenancy & Tenant Isolation](../architecture/multi-tenancy.md)
- [Guards](../nestjs/guards.md)
- [Access Control & IAM](../../security/authorization/access-control-iam.md)
- [OAuth Scopes & Least-Privilege Tokens](../../security/auth/oauth-scopes.md)
