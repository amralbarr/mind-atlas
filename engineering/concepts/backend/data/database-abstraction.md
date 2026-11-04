# Database Abstraction

**Database abstraction** is the practice of hiding the specific database engine ([PostgreSQL](../../databases/relational/postgresql.md), [MySQL](../../databases/relational/mysql.md), [MongoDB](../../databases/nosql/mongodb.md), [SQLite](../../databases/relational/sqlite.md)) behind an interface that application code depends on instead — so business logic calls a generic method (`find`, `save`, `query`) rather than writing engine-specific [SQL](../../databases/relational/sql.md) or driver calls directly. It's a specific application of [abstraction](../../programming/fundamentals/abstraction.md) focused on one particular dependency: the data store.

## Why Abstract the Database At All

```
Application code
    ↓
Database abstraction layer   ← the engine-specific details live here, and ONLY here
    ↓
Actual database (Postgres today, maybe something else later)
```

Without this layer, every part of the codebase that touches data has to know the exact [SQL](../../databases/relational/sql.md) dialect, connection details, and quirks of one specific database. With it, only one layer needs to change if the underlying database ever changes — the rest of the application never notices, because it was never written against the specific engine to begin with.

## The Levels of Database Abstraction

These aren't competing options — they're increasing levels of [abstraction](../../programming/fundamentals/abstraction.md), each built on the one below it:

| Level | What it hides | Example |
|---|---|---|
| **Driver** | The wire protocol, connection handling | `pg` (Node.js Postgres driver), `psycopg2` (Python) |
| **Query Builder** | [SQL](../../databases/relational/sql.md) syntax differences between engines | Knex.js, SQLAlchemy Core |
| **[ORM](orm.md)** | The relational model itself — rows become objects | Prisma, TypeORM, Drizzle, SQLAlchemy [ORM](orm.md) |
| **Repository Pattern** | The [ORM](orm.md)/query-builder choice itself, behind a domain-specific interface | `UserRepository.findActiveUsers()` instead of `prisma.user.findMany({ where: { active: true } })` |

Each level trades some control and performance transparency for less engine-specific code — see [ORM vs. Query Builder vs. Raw SQL](orm.md#orm-vs-query-builder-vs-raw-sql) for the direct trade-off at the [ORM](orm.md) layer specifically.

## The Repository Pattern — Abstracting the ORM Itself

Even with an [ORM](orm.md) in place, application/business logic can still end up directly importing and calling the [ORM](orm.md) client everywhere (`prisma.user.findMany(...)` scattered across dozens of files) — which means swapping ORMs, or even just restructuring how a query is built, touches every one of those call sites. The **repository pattern** adds one more layer: a domain-specific class (`UserRepository`) that wraps all database access for one entity behind methods named for what the business logic actually needs, not what the [ORM](orm.md)'s API happens to look like:

```typescript
// Without a repository: business logic depends directly on Prisma's API shape
const activeUsers = await prisma.user.findMany({ where: { active: true } });

// With a repository: business logic depends on a method name, not an ORM
const activeUsers = await userRepository.findActiveUsers();
```

If the underlying query changes, or the [ORM](orm.md) itself is swapped, only `UserRepository`'s internals change — every caller stays exactly the same. This is the [Dependency Inversion Principle](../../programming/fundamentals/dependency-inversion-principle.md) applied directly to the data layer: business logic depends on a `UserRepository` *[abstraction](../../programming/fundamentals/abstraction.md)*, never on the concrete ORM.

## How Much Abstraction Is Too Much?

Database abstraction is a real engineering trade-off, not a free win:

- **Benefit**: application code becomes portable and testable — a repository interface can be backed by a fake/in-memory implementation in tests, with zero real database involved (see [Dependency Injection](../../programming/fundamentals/dependency-injection.md) for exactly this swap-the-implementation pattern).
- **Cost**: too many [abstraction](../../programming/fundamentals/abstraction.md) layers between business logic and the actual query can hide genuinely important database-specific behavior — a repository method that looks simple can silently generate an inefficient query (see [The N+1 Query Problem](n-plus-1-problem.md)), and the [abstraction](../../programming/fundamentals/abstraction.md) itself makes that harder to spot without looking through every layer.
- **Reality check**: most systems never actually swap their database engine — "portability" is frequently a theoretical benefit that's paid for in real, ongoing complexity. The repository pattern earns its cost more reliably through **testability** (fast, real-database-free unit tests) than through genuine engine portability.

## Related

- [ORM](orm.md) — the most common concrete implementation of database abstraction
- [Dependency Inversion Principle](../../programming/fundamentals/dependency-inversion-principle.md) — the SOLID principle the repository pattern applies to the data layer
- [Abstraction](../../programming/fundamentals/abstraction.md) — the general CS principle this specializes
- [The N+1 Query Problem](n-plus-1-problem.md) — a cost of over-abstracting: a clean-looking repository call can still generate an inefficient query
- [Dependency Injection](../../programming/fundamentals/dependency-injection.md) — how a repository interface gets swapped for a fake implementation in tests
- [Connection Pooling](../../databases/relational/connection-pooling.md) — a concern that lives below the [abstraction](../../programming/fundamentals/abstraction.md) layer, not above it
