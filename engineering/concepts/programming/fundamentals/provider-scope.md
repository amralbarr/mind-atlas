# Provider Scope

**Provider scope** (also called **service lifetime**) controls *how long* a [dependency-injected](dependency-injection.md) instance lives, and whether it's shared across multiple places that inject it. Every [DI](dependency-injection.md)-first framework needs an answer to this question — get it wrong, and you either leak shared state across requests that should be isolated from each other, or pay the cost of recreating something expensive (a database connection, a config object) far more often than necessary.

## The Three Scopes

| Scope | Meaning | When to use it |
|---|---|---|
| **[Singleton](../design-patterns/singleton.md)** (the default) | One shared instance for the entire application's lifetime | Database clients, caches, configuration, [HTTP](../../networking/http.md) clients — anything expensive to create and safe to share |
| **Request** | A new instance created once per incoming request, shared by everything injected during that one request | A service that needs the current user's identity, a `request_id` for logging/tracing, or per-request tenant context |
| **Transient** | A brand-new instance every single time it's injected, never shared at all | Lightweight, stateless services with no shared state to worry about |

## Why the Default Matters

**[Singleton](../design-patterns/singleton.md) is the default in every mainstream [DI](dependency-injection.md) framework** — not because it's always correct, but because most services genuinely *should* be shared: a database connection pool, an [HTTP](../../networking/http.md) client, a cache client. Creating a fresh instance of these per-request (or per-injection) would be wasteful and could exhaust the exact resources (connections, memory) the service is managing.

The failure mode runs the other way, though: if a Singleton-scoped service accidentally holds **per-request mutable state** (storing the current user on an instance field, say), that state leaks across every concurrent request sharing that one instance — a real, hard-to-reproduce bug that only shows up under real concurrent load, not in a single-request test.

```typescript
// WRONG: a Singleton service storing per-request state on an instance field
@Injectable()
export class RequestContextService {
  currentUserId: string;  // shared across every request! A real bug under concurrency.

  setUser(id: string) { this.currentUserId = id; }
}
```

```typescript
// RIGHT: Request-scoped, so each request gets its own instance -- no leakage
@Injectable({ scope: Scope.REQUEST })
export class RequestContextService {
  currentUserId: string;  // safe -- a new instance exists per request
}
```

## The Same Concept, Different Names, Across Frameworks

The three-tier idea is identical across every major DI framework — only the names and the exact default differ:

| Scope meaning | [NestJS](../../backend/nestjs/nestjs-overview.md) | [Spring Boot](../java/spring-boot.md) | [ASP.NET Core](../csharp/asp-net.md) |
|---|---|---|---|
| One shared instance, app-wide | `Scope.DEFAULT` (implicit) | `@Scope("singleton")` (implicit default) | `AddSingleton<T>()` |
| One instance per request | `Scope.REQUEST` | `@Scope("request")` (needs `spring-web`) | `AddScoped<T>()` — **note the different name for the same idea** |
| A fresh instance every injection | `Scope.TRANSIENT` | `@Scope("prototype")` | `AddTransient<T>()` |

The naming mismatch between NestJS's `REQUEST` and ASP.NET's `Scoped` describing the exact same per-request lifetime is a common source of confusion when moving between ecosystems — they are the same concept, just named differently.

## The Real Cost of Request/Transient Scope

Singleton isn't just the default for convenience — it's also the cheapest option, since the instance is created exactly once. Request and Transient scope both mean the DI container has to construct a new instance (and resolve all of *its* dependencies) more often — Request scope once per request, Transient scope on every single injection point. In a hot path handling thousands of requests per second, defaulting everything to Request/Transient scope "just to be safe" has a real, measurable performance cost — scope should be a deliberate choice driven by whether state actually needs isolating, not a reflexive default.

## Common Questions

**If a Singleton-scoped service injects a Request-scoped one, what happens?**
> The Singleton service itself becomes effectively request-scoped for that dependency — most frameworks either throw an error at startup (a "captive dependency" check) or silently create the Request-scoped dependency once and freeze it for the Singleton's lifetime, which defeats the purpose and is almost always a bug. The dependency graph's scopes have to be considered together, not just per-service in isolation.

**Why not just make everything Request-scoped to be safe?**
> Because most services have no per-request state to protect in the first place, and Request scope means re-resolving the entire dependency chain on every request — a real performance cost for zero actual benefit when the service was stateless to begin with.

## Related

- [Dependency Injection](dependency-injection.md) — the general pattern this specializes (how long an injected instance lives)
- [NestJS Overview](../../backend/nestjs/nestjs-overview.md) — `Scope.DEFAULT`/`REQUEST`/`TRANSIENT`
- [Spring Boot](../java/spring-boot.md) — `@Scope("singleton"/"request"/"prototype")`
- [ASP.NET Core](../csharp/asp-net.md) — `AddSingleton`/`AddScoped`/`AddTransient`
- [Singleton Pattern](../design-patterns/singleton.md) — the classic design pattern a Singleton-scoped provider is a managed, framework-enforced version of
- [Idempotency and Race Conditions](idempotency-and-race-conditions.md) — the general hazard class a Singleton accidentally holding per-request state falls into
