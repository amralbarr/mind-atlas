# Database Scaling Strategies: Pooling → Replicas → Partitioning → Sharding

A single database instance has a hard ceiling — finite CPU, memory, disk, and connection capacity. As load grows, teams typically climb a fairly consistent ladder of techniques, each addressing a different bottleneck and each more operationally expensive than the last. This overview ties together four atomic concepts, in the order they're usually reached for, rather than explaining any one of them in full — see each one's own file for the real depth.

```text
     Cheapest, simplest                                    Most expensive, most complex
            │                                                          │
            ▼                                                          ▼
  Connection Pooling → Read Replicas → Partitioning → Sharding
  (reduce per-query      (scale read      (keep one table    (scale past a single
   connection overhead)   throughput)      manageable)         instance entirely)
```

This progression isn't a rigid rule every system must follow in lockstep — a system might never need [partitioning](../../concepts/databases/relational/partitioning.md), or might reach for [sharding](../../concepts/databases/distributed/sharding.md) earlier if it's write-heavy from day one — but it reflects the order these problems typically actually show up in, and each step solves a genuinely different bottleneck than the one before it.

## The Four Techniques, Briefly

| Technique | What it actually does | What bottleneck it fixes | Full note |
|---|---|---|---|
| **[Connection pooling](../../concepts/databases/relational/connection-pooling.md)** | Reuses a set of already-open database connections instead of opening a fresh one per request | Connection-establishment overhead ([TCP](../../concepts/networking/tcp.md)/[TLS](../../concepts/networking/tls.md)/auth handshake cost) and connection-count exhaustion under concurrent load | [Connection Pooling](../../concepts/databases/relational/connection-pooling.md) |
| **[Read replicas](../../concepts/databases/relational/read-replicas.md)** | Keeps continuously-updated full copies of the data on additional nodes, serving read-only queries from them | Read throughput — most apps are read-heavy, so spreading `SELECT`s across replicas relieves the primary without touching write capacity | [Read Replicas](../../concepts/databases/relational/read-replicas.md) |
| **[Partitioning](../../concepts/databases/relational/partitioning.md)** | Splits one large table into smaller physical pieces (by range/list/hash), still on the *same* instance | Table-scan, index-maintenance, and bulk-operation cost on one unwieldy table — not raw capacity | [Partitioning](../../concepts/databases/relational/partitioning.md) |
| **[Sharding](../../concepts/databases/distributed/sharding.md)** | Splits data across multiple *separate* database instances/nodes, each holding a different subset | Total throughput or storage that has outgrown what any single instance can hold, no matter how well-tuned | [Sharding](../../concepts/databases/distributed/sharding.md) |

## Why This Order

Each step is reached for once the previous one stops being enough, and each is progressively more invasive to adopt:

1. **[Connection pooling](../../concepts/databases/relational/connection-pooling.md) is first** because it's nearly free to add (a library or a sidecar like [PgBouncer](../../concepts/databases/relational/pgbouncer.md)), requires no schema or architecture change, and often buys real headroom just by removing wasted per-request connection overhead. If the database is being overwhelmed by connection *count* rather than query volume, pooling alone can resolve it.
2. **[Read replicas](../../concepts/databases/relational/read-replicas.md) come next** because most workloads are read-heavy, and adding a replica is comparatively simple (most databases support it natively) compared to anything that touches how data itself is organized. It only requires the application to route reads and writes to the right place — see the application-level read/write splitting section in [Read Replicas](../../concepts/databases/relational/read-replicas.md).
3. **[Partitioning](../../concepts/databases/relational/partitioning.md) comes after that** because it solves a problem replicas can't — a single table that's gotten too large to scan, index, or maintain efficiently, regardless of how many [read replicas](../../concepts/databases/relational/read-replicas.md) exist (since every replica still has to replicate and store the same oversized table).
4. **[Sharding](../../concepts/databases/distributed/sharding.md) is last** because it's the only one of the four that adds genuinely new CPU/memory/disk capacity — and the only one that forces real application-level complexity (shard-aware routing, no easy cross-shard joins or transactions). It's reached for only once write throughput or total storage itself has outgrown what one instance — however pooled, replicated, or partitioned — can hold.

## A Worked Progression

Consider an order-processing table that starts on one small database and grows over time:

```text
Stage 0: One small Postgres instance, low traffic.
         → No scaling needed yet.

Stage 1: Traffic grows; many short-lived app instances are each opening
         their own DB connections, and the database is hitting its
         max-connections limit before it's even CPU-bound.
         → Add connection pooling (PgBouncer in front of Postgres).

Stage 2: Pooling buys headroom, but read traffic (dashboards, order
         lookups, reporting) keeps growing and the primary's CPU is now
         dominated by SELECTs.
         → Add read replicas; route reads to replicas, writes to primary.

Stage 3: The orders table itself has grown to hundreds of millions of
         rows. VACUUM, REINDEX, and "delete orders older than 2 years"
         are now slow and disruptive, even though neither reads nor
         writes have outgrown the instance's raw capacity yet.
         → Partition the orders table by date range (one partition per
           quarter); old partitions can now be dropped instantly instead
           of bulk-deleted row by row.

Stage 4: Total write volume has grown so much that even the partitioned
         primary's write capacity is maxed out — more orders are being
         written per second than one instance's disk/CPU can sustain,
         no matter how the table is organized internally.
         → Shard by customer region or customer ID range across several
           independent database instances, each with its own primary,
           replicas, and partitioned tables.
```

Each stage's fix addresses a bottleneck the previous stage's fix had no effect on — more [read replicas](../../concepts/databases/relational/read-replicas.md) wouldn't have helped Stage 1's connection-count problem, and [partitioning](../../concepts/databases/relational/partitioning.md) wouldn't have helped Stage 4's raw write-throughput ceiling.

## How They Compose

These aren't mutually exclusive alternatives — a mature, large-scale system typically runs several at once:

```text
          Shard A              Shard B              Shard C
      ┌─────────────┐      ┌─────────────┐      ┌─────────────┐
      │  Primary     │      │  Primary     │      │  Primary     │
      │  (partitioned│      │  (partitioned│      │  (partitioned│
      │   tables)    │      │   tables)    │      │   tables)    │
      │     ↓        │      │     ↓        │      │     ↓        │
      │  Replica(s)  │      │  Replica(s)  │      │  Replica(s)  │
      └─────────────┘      └─────────────┘      └─────────────┘
            ↑                     ↑                     ↑
       Each instance's connections flow through a connection pool
```

Each shard is itself a full instance that can have its own [read replicas](../../concepts/databases/relational/read-replicas.md) and internally [partitioned](../../concepts/databases/relational/partitioning.md) tables, and every connection into any of those instances still goes through [connection pooling](../../concepts/databases/relational/connection-pooling.md). This is why the four techniques are presented as a ladder of *when to first reach for each*, not a set of alternatives to pick just one from.

## How This Relates to Application-Layer Scaling

The application layer has its own, simpler version of this same "add more instead of making one bigger" idea: [horizontal scaling](../../concepts/backend/architecture/horizontal-scaling.md) running more stateless containers behind a [load balancer](../../concepts/networking/load-balancing.md). It's simpler at that layer specifically because application containers are (or should be) stateless and trivially interchangeable — duplicating one is cheap. A database holds state, which is exactly why its equivalent scaling ladder has four distinct rungs instead of one: you can't just duplicate a database node the way you duplicate a stateless container and expect correctness for free.

## Common Questions

**Do you have to go through all four steps in order?**
> No — this is the typical order problems show up in for a read-heavy application growing organically, not a mandatory sequence. A write-heavy system from day one (e.g. high-volume IoT ingestion) might reach for [sharding](../../concepts/databases/distributed/sharding.md), or choose a database built for horizontal scale from the start ([MongoDB](../../concepts/databases/nosql/mongodb.md), [Cassandra](../../concepts/databases/nosql/cassandra.md)), well before [read replicas](../../concepts/databases/relational/read-replicas.md) or [partitioning](../../concepts/databases/relational/partitioning.md) become relevant at all.

**Why not just shard from the beginning and skip the earlier, simpler steps?**
> [Sharding](../../concepts/databases/distributed/sharding.md) adds real, permanent complexity — cross-shard joins and transactions become hard problems, and the application needs shard-aware routing logic. Reaching for it before it's actually needed means paying that complexity cost for capacity the system doesn't yet use. The earlier rungs are preferred specifically because they're cheaper to adopt and reverse.

**Which of these actually increases total write capacity?**
> Only [sharding](../../concepts/databases/distributed/sharding.md). [Connection pooling](../../concepts/databases/relational/connection-pooling.md) reduces overhead, not capacity. [Read replicas](../../concepts/databases/relational/read-replicas.md) scale *reads* only — every write still funnels through one primary. [Partitioning](../../concepts/databases/relational/partitioning.md) makes one instance's tables more manageable but doesn't add another instance's worth of resources. [Sharding](../../concepts/databases/distributed/sharding.md) is the only technique here that puts more independent machines to work on writes.

## Related

- [Connection Pooling](../../concepts/databases/relational/connection-pooling.md) — the first, cheapest rung on this ladder
- [Read Replicas](../../concepts/databases/relational/read-replicas.md) — the second rung, scaling read throughput via full data copies
- [Partitioning](../../concepts/databases/relational/partitioning.md) — the third rung, splitting one table within a single instance
- [Sharding](../../concepts/databases/distributed/sharding.md) — the final rung, splitting data across separate instances for real added capacity
- [Distributed Databases](../../concepts/databases/distributed/distributed-databases.md) — the deeper multi-node theory (CAP theorem, consistency models) behind sharded and replicated systems
- [Horizontal Scaling](../../concepts/backend/architecture/horizontal-scaling.md) — the application-layer equivalent of "add more instead of making one bigger," simpler because containers are stateless
- [PgBouncer](../../concepts/databases/relational/pgbouncer.md) — a concrete external pooler commonly used to implement the first rung in front of [PostgreSQL](../../concepts/databases/relational/postgresql.md)
- [Database Indexing](../../concepts/databases/relational/indexing.md) — a complementary technique (speeding up lookups within a table/partition) that composes with every rung on this ladder but doesn't itself add capacity
