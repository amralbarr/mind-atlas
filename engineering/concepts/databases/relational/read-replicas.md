# Read Replicas vs. Write Replicas (Database Replication)

Database replication keeps copies of the same data on multiple database nodes. The most common topology splits nodes by role — a single **primary (write replica)** that accepts all writes, and one or more **read replicas** that receive a continuous copy of the primary's data and serve read-only queries — spreading read load across multiple machines while keeping writes centralized and unambiguous.

## The Basic Topology

```text
                Writes
                  ↓
             ┌─────────┐
             │ Primary │  (accepts writes, source of truth)
             └────┬────┘
        replication stream
         ┌─────────┼─────────┐
         ↓         ↓         ↓
     Replica 1  Replica 2  Replica 3   (read-only, serve SELECT queries)
```

Application writes always go to the primary; reads can be spread across the primary and any number of read replicas, since read-heavy workloads (dashboards, reporting, most typical web traffic) usually vastly outnumber writes.

## Why Split Reads and Writes At All

A single database node has a hard ceiling on throughput. Because most applications are read-heavy (far more `SELECT`s than `INSERT`/`UPDATE`/`DELETE`), read replicas let you scale the *bottleneck* — read capacity — horizontally by adding more replicas, without touching the more complex problem of scaling writes (which usually requires [sharding](../distributed/sharding.md) or a distributed-[SQL](sql.md) system instead — see [Distributed Databases](../distributed/distributed-databases.md)).

| Benefit | Why it matters |
|---|---|
| **Horizontal read scaling** | Add another replica to handle more read traffic — much simpler than scaling writes |
| **Isolation of expensive queries** | Route heavy analytics/reporting queries to a dedicated replica so they don't compete with production traffic on the primary |
| **Geographic distribution** | Place replicas closer to users in different regions, reducing read latency, while writes still funnel to one primary |
| **High availability** | A replica can often be promoted to primary if the original primary fails (though this promotion process — failover — has to be handled carefully, whether automatically or manually) |

## Replication Lag: The Real Trade-off

Replication is not instantaneous — there's always some delay between a write landing on the primary and that same write appearing on a replica. This is the same core trade-off as [eventual consistency](../../distributed-systems/patterns/eventual-consistency.md), applied specifically to primary/replica database topology:

```text
t=0:  Write "balance = 500" lands on Primary
t=0 to t=X: Replica still shows the old "balance = 300" — replication lag
t=X:  Replica catches up, now also shows "balance = 500"
```

If an application writes to the primary and then *immediately* reads from a replica (a common pattern: "save, then redirect to a page that reads the saved data"), it can read stale data during that lag window — a frequent source of confusing "my change didn't save!" bug reports that are actually a replication-lag race, not a real data-loss bug.

### Common Mitigations for Replication Lag

- **Read-your-own-writes routing** — route a user's reads back to the primary (or a replica known to be caught up) immediately after that same user's own write, while other users' reads can still go to any replica.
- **Monitoring replication lag directly** — most databases expose a lag metric; a replica falling too far behind should be pulled out of the read-serving rotation rather than silently serving increasingly stale data.
- **Accepting the lag where it's harmless** — for read traffic that doesn't need up-to-the-millisecond freshness (a public content feed, analytics dashboards), a few hundred milliseconds of lag is often completely invisible in practice.

## Synchronous vs. Asynchronous Replication

| | Synchronous | Asynchronous |
|---|---|---|
| When the primary confirms a write | Only after at least one replica has also confirmed receiving it | Immediately, without waiting for any replica |
| Write latency | Higher — bounded by the slowest required replica | Lower — the replica's speed doesn't affect write latency |
| Data-loss risk on primary failure | None for synchronously-confirmed writes — a replica already has it | A very recent write might exist only on the now-failed primary and be lost |
| Common default | Used selectively for critical data (financial systems) given its latency cost | The default for most read replicas, since replication lag is an acceptable trade-off for read scaling |

## Application-Level Read/Write Splitting

The application (or an [ORM](../../backend/data/orm.md)/driver-level feature) has to actually route queries correctly — this doesn't happen automatically just because replicas exist:

```typescript
// Prisma example: separate read/write connection URLs
const writeClient = new PrismaClient({ datasources: { db: { url: process.env.PRIMARY_URL } } });
const readClient = new PrismaClient({ datasources: { db: { url: process.env.REPLICA_URL } } });

await writeClient.order.create({ data: { ... } });          // always the primary
const orders = await readClient.order.findMany();             // can go to a replica
```

Some managed database services (Amazon Aurora, for instance) provide a single "reader endpoint" that automatically load-balances across all available read replicas, hiding this routing logic from the application entirely.

## Read Replicas vs. Sharding

These solve different scaling problems and are often confused:

| | Read Replicas | [Sharding](../distributed/sharding.md) |
|---|---|---|
| What's split | Nothing — every replica holds a **full copy** of the same data | The data itself is **partitioned** — each shard holds a different subset |
| Scales | Read throughput | Both read *and* write throughput, plus total storage capacity |
| Complexity | Relatively simple to set up (most databases support it natively) | Significantly more complex (routing logic, cross-shard queries/joins, rebalancing) |
| Fixes a single-node write bottleneck? | No — all writes still go to one primary | Yes — writes for different shards can go to different nodes |

Read replicas are usually the first, simpler scaling lever reached for; [sharding](../distributed/sharding.md) is reached for once writes themselves — not just reads — have outgrown what a single primary can handle. See [Distributed Databases](../distributed/distributed-databases.md) for [sharding](../distributed/sharding.md) in full.

## Common Questions

**Can you write to a read replica?**
> Not in the standard primary/replica model — replicas are read-only by design, specifically so there's never ambiguity about which node holds the authoritative, current value for a given piece of data. (Multi-primary/multi-leader replication topologies exist and do allow writes to more than one node, but they introduce conflict-resolution complexity that most systems deliberately avoid unless they specifically need it.)

**If a read replica can be promoted to primary during failover, why keep replication asynchronous instead of always synchronous?**
> Because synchronous replication adds real write latency (waiting for a replica's confirmation on every write) — many systems accept the small risk of losing the very latest asynchronously-replicated writes during a rare primary failure in exchange for meaningfully faster writes the rest of the time. Systems that can't tolerate any loss at all (financial ledgers) pay the latency cost for synchronous replication specifically on their critical write paths.

**Does adding more read replicas help if the bottleneck is actually write throughput?**
> No — read replicas do nothing for write scaling, since every write still funnels through the single primary. A write-throughput bottleneck needs [sharding](../distributed/sharding.md), a distributed-[SQL](sql.md) database, or vertical scaling of the primary instead.

## Related

- [Distributed Databases](../distributed/distributed-databases.md)
- [Eventual Consistency](../../distributed-systems/patterns/eventual-consistency.md)
- [Connection Pooling](connection-pooling.md)
- [ACID](acid.md)
- [Sharding](../distributed/sharding.md) — the scaling step reached for once write throughput, not just reads, has outgrown a single primary
- [Partitioning](partitioning.md) — a separate, composable single-instance technique that addresses table-scan/maintenance cost rather than read throughput
- [Database Scaling Strategies](../../../overviews/databases/database-scaling-strategies.md) — the overview placing read replicas as the second rung on the broader database-scaling ladder
