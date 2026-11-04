# Multi-Tenancy & Tenant Isolation

A **multi-tenant** system serves multiple distinct customers ("tenants") from shared infrastructure and often a shared database, while guaranteeing that one tenant's data is never visible to another. Getting isolation wrong is one of the most damaging classes of bug a SaaS product can ship — it's a data breach, not just a functional defect.

## Common Isolation Strategies

| Strategy | Isolation level | Trade-off |
|---|---|---|
| **Separate database per tenant** | Strongest — physically separate storage | Simple security story, but expensive to operate and migrate at scale (N databases to patch/monitor) |
| **Separate schema per tenant, shared database** | Strong — same DB engine, isolated namespaces | Middle ground; still N schemas to migrate |
| **Shared tables, tenant-id column** | Weakest by default — relies entirely on every query filtering correctly | Cheapest to operate, but a single missed filter leaks data across tenants |

Most products default to the shared-table model for cost and operational simplicity, which makes the *query-filtering discipline* below the entire security boundary — there's no physical wall backstopping a mistake.

## Centralize the Filter, Don't Repeat It

The core practice for the shared-table model: build **one function** that every tenant-scoped query goes through to construct its `WHERE` clause, rather than writing `WHERE tenant_id = ?` inline at every call site. A missed filter in one of N inline query-builders is a silent, easy-to-introduce leak; a bug in one centralized filter function is found once and fixed once, and — more importantly — a *new* query added later automatically inherits the isolation instead of requiring someone to remember to add it.

## A Second, Easy-to-Miss Boundary: Existing Cross-Tenant Features

Retrofitting multi-tenancy onto a system that previously had a single-tenant notion of "shared/public" data is a common source of leaks that isn't about missing a `WHERE` clause at all — it's a *feature* that predates tenancy and was never designed with it in mind. A "this item is visible to everyone" flag that made sense before multiple tenants existed can, left unchanged, mean tenant A's "public" items become visible to tenant B's users once both share the same database — the fix isn't a query filter bug fix, it's recognizing the feature's original semantics no longer hold and deciding explicitly whether it should be scoped per-tenant, disabled entirely for tenant-scoped access, or reworked.

## Real-World Example

A real third-party embeddable-widget design hits exactly this second case: a pre-existing "PUBLIC visibility" feature was platform-wide, meaning an embedded, tenant-scoped session would otherwise see every other tenant's public items *and* the main product's own public library — a real cross-tenant leak introduced not by a missing filter, but by a feature whose old semantics didn't survive the addition of tenancy. The fix was a single `buildAccessFilter()`-style function every listing/access code path is required to call, which excludes the public-visibility branch entirely for a tenant-scoped caller — plus closing a related gap where a session scoped to *one specific record* could still call a list endpoint and see every record the underlying account owned, because the single-record pin had only been enforced on single-object actions, not baked into the list query's own filter.

## Common Questions

**Is row-level security (RLS) at the database layer a substitute for application-level filtering?**
> RLS (a database feature that enforces per-row visibility rules server-side, e.g. in [PostgreSQL](../../databases/relational/postgresql.md)) is a strong complementary layer — defense-in-depth against an application-layer bug — but most teams still centralize application-level filtering too, since RLS policies aren't always straightforward to keep in sync with evolving application logic, and RLS support/tooling varies by database engine.

**Does adding a tenant-id column and a `WHERE` clause fully solve multi-tenancy?**
> Only for straightforward CRUD. Aggregate queries, background jobs, caching keys, search indexes, and file-storage paths all need the same tenant-scoping discipline applied — any place data is read, cached, or indexed without going through the centralized filter is a potential leak, not just the primary query paths.

## Related

- [Policy-Based Authorization](../data/policy-based-authorization.md)
- [Access Control & IAM](../../security/authorization/access-control-iam.md)
- [OAuth Scopes & Least-Privilege Tokens](../../security/auth/oauth-scopes.md)
- [LLM API Quota Management](../../ai/infrastructure/llm-api-quota-management.md) — per-tenant quota caps as a defense against one tenant exhausting shared [LLM](../../ai/generation/llm.md) provider capacity
