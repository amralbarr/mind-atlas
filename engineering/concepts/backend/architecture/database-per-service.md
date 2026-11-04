# Database per Service

**Database per service** is the microservices principle that each service owns its own data store exclusively — no other service is ever allowed to read from or write to it directly. A service's database is private implementation detail, exactly like its internal functions or classes; the only way another part of the system gets at that data is through the owning service's own [API](../api/api.md) or the events it publishes. This is the data-layer half of what [service isolation](monolith-vs-microservices.md) means in a microservices architecture — without it, "microservices" is really just a monolith's single shared database with extra network hops bolted on top.

## A Concrete Example

Imagine a learning platform split into services like **Studio** (course authoring), **Learner** (enrollment and progress), **Mastery Engine** (skill/competency scoring), and **AI Management** (model and prompt configuration). Under database-per-service, each of those four owns its own exclusive data store:

```text
Studio          ──owns──▶  Studio DB          (courses, lessons, content versions)
Learner         ──owns──▶  Learner DB         (enrollments, progress, attempts)
Mastery Engine  ──owns──▶  Mastery Engine DB  (skill scores, mastery levels)
AI Management   ──owns──▶  AI Management DB   (model configs, prompts, usage)
```

If the Mastery Engine needs to know which lessons a learner has completed, it does **not** run a query against the Learner DB's tables directly — it calls the Learner service's API, or reacts to a `LessonCompleted` event the Learner service published. The Learner team can change its own schema (rename a column, split a table, swap [PostgreSQL](../../databases/relational/postgresql.md) for [MongoDB](../../databases/nosql/mongodb.md)) without ever coordinating with the Mastery Engine team, because nothing outside Learner depends on its internal storage shape — only on the stable contract it exposes.

## Why Shared Databases Between Services Create Coupling

A shared database is the single most common way a system that looks like microservices on an architecture diagram is actually a distributed [monolith](monolith-vs-microservices.md) in practice:

| Problem | Why it happens |
|---|---|
| **Hidden coupling** | If Service B reads Service A's tables directly, B is now coupled to A's *internal schema*, not just its public contract — a column rename in A silently breaks B, with no compiler error and no API version to bump |
| **Blast radius** | A bad migration, a lock-heavy query, or an outage on the shared database now takes down every service that touches it, not just the one that caused the problem — the fault isolation that's supposed to be microservices' main selling point disappears |
| **No independent deployability** | Services can't evolve their schemas independently if other services depend on those schemas directly — every schema change becomes a cross-team coordination event, defeating the whole point of splitting into separate services with separate deployment cadences |
| **Unclear ownership** | When multiple services write to the same tables, nobody fully owns the data's invariants — validation and business rules end up duplicated (or contradicted) across every service that writes to it, instead of enforced in one place |
| **Technology lock-in** | A shared database forces every service touching it onto the same database engine and schema, even if one service's access pattern would be far better served by a different data store |

This is the same coupling problem a well-designed internal API/module boundary prevents inside a single codebase — database-per-service is that same discipline applied at the service-boundary level instead of the class/module level.

## The Pattern Itself

"Database per service" means:

1. **Each service has its own schema or database instance** that only that service's code can connect to — enforced at the infrastructure level (separate credentials, separate network access, sometimes a physically separate database server), not just as a team convention that's easy to violate under deadline pressure.
2. **No direct cross-service [SQL](../../databases/relational/sql.md)/database access, ever** — not even "just this one read-only query for a report," since that one exception becomes a hidden dependency that blocks the owning service's next migration.
3. **The owning service is the only thing allowed to change that data's shape** — it can refactor its internal schema freely as long as its external contract (API responses, published event shapes) stays stable or is versioned.

This doesn't necessarily mean N physically separate database servers for N services — a private schema per service inside one shared database cluster, enforced by database-level permissions, is a common lighter-weight variant. What matters is the *logical* ownership boundary and the enforcement that nothing bypasses it, not the physical deployment topology.

## How Services Communicate Instead

Since direct table access is off the table, services exchange data through:

| Mechanism | Example |
|---|---|
| **Synchronous API calls** | Service B calls Service A's [REST](../api/rest.md) or [gRPC](../api/grpc.md) endpoint to fetch current data on demand |
| **Asynchronous events** | Service A publishes an event (e.g. via [Kafka](../../distributed-systems/messaging/kafka.md) or [RabbitMQ](../../distributed-systems/messaging/rabbitmq.md)) when its own data changes; interested services consume it and update their own local copy or react to it |
| **API composition** | A caller (or an [API gateway](../api-gateways/kong.md)) calls several services and combines their responses, rather than one service querying across database boundaries itself |

The asynchronous/event route is especially common specifically *because* of database-per-service: if the Mastery Engine needs a fast local read of "has this learner completed lesson X" without calling the Learner service synchronously on every request, it subscribes to the Learner service's events and maintains its own denormalized, eventually-consistent local copy of just the fields it needs — trading some duplication and [eventual consistency](../../distributed-systems/patterns/eventual-consistency.md) for isolation and resilience to the Learner service being temporarily unavailable.

## Relation to Bounded Contexts (Domain-Driven Design)

Database-per-service is the technical enforcement mechanism for a modeling idea from Domain-Driven Design: the **bounded context** — a boundary within which a particular domain model (its entities, its terminology, its business rules) is defined consistently, and outside of which the same term can legitimately mean something different. "Course" inside Studio (an authored content structure being edited) and "Course" inside Learner (an enrollment record with progress state) are different models of a similar real-world idea, each valid only within its own context.

A microservice is typically designed to align with one bounded context, and giving that service exclusive ownership of its own database is what actually *enforces* the bounded context's boundary in running code — without it, two services informally sharing a database tend to drift toward one shared, contested model of "Course" that satisfies neither context well, re-introducing the tight coupling bounded contexts exist to prevent. In other words: bounded context is the design-level boundary, and database-per-service is the data-ownership rule that keeps that boundary real once the system is actually deployed and being written to by multiple services.

## Trade-offs: What This Pattern Costs You

Database-per-service isn't free — it trades a simpler data layer for better isolation and independent deployability:

- **No cross-service joins.** A query that used to be a single [SQL](../../databases/relational/sql.md) join across two tables now requires either two separate calls stitched together in application code, or a pre-built local read model kept in sync via events.
- **[Distributed transactions](../../databases/distributed/distributed-transactions.md) become hard.** An operation that needs to update data in two services consistently can no longer rely on one database's [ACID](../../databases/relational/acid.md) transaction — it needs a pattern like [the Saga pattern](../../distributed-systems/patterns/saga-pattern.md) (a sequence of local transactions plus compensating actions on failure) instead of a single atomic commit. See [Distributed Transactions](../../databases/distributed/distributed-transactions.md) for the deeper treatment.
- **Data duplication becomes normal, not a smell.** Services that need fast local reads of another service's data deliberately keep their own eventually-consistent copy of just the fields they need, rather than querying the source of truth live on every request — a trade-off that would look like an anti-pattern (denormalization, data duplication) inside a single shared database, but is a reasonable, expected cost of isolation here.
- **More operational surface area.** N services now potentially means N databases to provision, back up, monitor, and patch, instead of one.

## Database per Service vs. Sharding: Different Axis, Same Instinct to "Split the Data"

It's easy to conflate these since both involve splitting data across more than one database, but they split along entirely different axes and solve different problems:

| | Database per Service | [Sharding](../../databases/distributed/distributed-databases.md) |
|---|---|---|
| What's split | Different **types of data owned by different services** (Studio's courses vs. Learner's progress) | The **same type of data**, partitioned by a key (e.g. users 1-1000 on Node A, 1001-2000 on Node B) |
| Why you do it | Service autonomy, isolation, independent deployability — an organizational/architectural boundary | Horizontal scale — one service's single dataset has outgrown what one database node can hold or handle |
| Who queries across the split | Different services, each with their own code and team | The *same* service/application, routing to the correct shard transparently |
| Can you have both at once? | Yes — a single microservice can shard its own database internally while still being the sole owner of that (sharded) data | — |

A system can need both simultaneously: Learner owns its own database (database-per-service, for isolation from Studio and Mastery Engine) and that same Learner database might itself be sharded by learner ID (for scale) once Learner's own write volume outgrows one node — two independent decisions solving two independent problems.

## Common Questions

**Is "database per service" the same as "every service must have its own physical database server"?**
> No — the requirement is exclusive logical ownership and enforced access control, not a specific physical deployment. A private schema per service inside one shared cluster, with database permissions preventing cross-schema access, satisfies the pattern just as well as fully separate server instances; the latter is simply a stronger (and more expensive) enforcement of the same boundary.

**What if two services genuinely need the same underlying data?**
> One of them owns it as the source of truth and exposes it through its API/events; the other maintains its own local, intentionally-denormalized copy of just what it needs, kept current via events, rather than both reading the same tables directly. Deciding which service is the actual owner is itself a bounded-context modeling decision, not just a technical one.

**Does this mean you can never run a report that spans multiple services' data?**
> Not directly against each service's live operational database — cross-service reporting/analytics typically reads from a separate data warehouse or lake that each service feeds (via events or periodic export) specifically for that purpose, keeping the "no direct cross-service access" rule intact for the operational databases while still answering cross-cutting questions.

**What's the single biggest sign this pattern has been violated in practice?**
> A migration or schema change in one service's database breaking another service's code without anyone having touched that other service's code — the clearest possible evidence that a "microservice" was actually reading another service's internal tables directly instead of going through its API.

## Related

- [Monolith vs Microservices](monolith-vs-microservices.md) — the broader architecture decision this pattern is the data-layer half of; its "Database Architecture Difference" section names this pattern without detail
- [Multi-Tenancy & Tenant Isolation](multi-tenancy.md) — a different, orthogonal isolation axis (one database, many tenants) versus this pattern's one-database-per-service axis
- [Distributed Databases](../../databases/distributed/distributed-databases.md) — covers [sharding](../../databases/distributed/sharding.md) and replication, the scaling-axis counterpart to this ownership-axis pattern
- [Distributed Transactions](../../databases/distributed/distributed-transactions.md) — the hard problem this pattern creates once an operation needs to touch more than one service's data consistently
- [Saga Pattern](../../distributed-systems/patterns/saga-pattern.md) — the standard way to coordinate a multi-step operation across separately-owned service databases without a single [ACID](../../databases/relational/acid.md) transaction
- [Eventual Consistency](../../distributed-systems/patterns/eventual-consistency.md) — the consistency model a service's locally-cached copy of another service's data has to accept
- [Kafka](../../distributed-systems/messaging/kafka.md) — a common transport for the "publish an event when my data changes" half of cross-service communication under this pattern
- [RabbitMQ](../../distributed-systems/messaging/rabbitmq.md) — an alternative event/message transport for the same purpose
- [REST](../api/rest.md) and [gRPC](../api/grpc.md) — the synchronous-call alternative to events for a service exposing its owned data to others
- [ACID](../../databases/relational/acid.md) — the single-database transaction guarantee this pattern trades away once data is split across service boundaries
- [Connection Pooling](../../databases/relational/connection-pooling.md) — a per-service concern once each service has its own database connections to manage independently
- [Read Replicas vs. Write Replicas](../../databases/relational/read-replicas.md) — a scaling technique a service can apply to its own privately-owned database without affecting this pattern's ownership boundary
