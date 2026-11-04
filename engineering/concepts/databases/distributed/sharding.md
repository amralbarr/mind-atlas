# Database Sharding

Sharding splits a database's data across **multiple separate database instances (nodes)**, each holding a different subset of the data, rather than one instance holding all of it. It's the scaling step reached for once a single instance — no matter how well-indexed, partitioned, or vertically scaled — can no longer handle the total write throughput or storage volume, because sharding is the one lever on the database-scaling ladder that actually adds more machines' worth of CPU, memory, and disk to the problem. See [Database Scaling Strategies](../../../overviews/databases/database-scaling-strategies.md) for where it sits relative to [connection pooling](../relational/connection-pooling.md), [read replicas](../relational/read-replicas.md), and [partitioning](../relational/partitioning.md).

```text
Without sharding:                 With sharding:

Application                       Application
     ↓                                 ↓
One DB instance                   Shard router / app logic
(all data, one machine)                ↓        ↓        ↓
                                   Shard A   Shard B   Shard C
                                   (users    (users    (users
                                    1-1M)     1M-2M)    2M-3M)
```

Each shard is a complete, independent database (with its own CPU, memory, disk, and often its own primary + [read replicas](../relational/read-replicas.md)) holding only its assigned slice of the data — not a copy of everything, which is what distinguishes sharding from replication.

## Why Sharding Is the Step Beyond Partitioning

[Partitioning](../relational/partitioning.md) splits one table into pieces that still live on the *same* instance — it helps scan and maintenance costs, but every partition still competes for that one instance's total CPU, memory, and disk. Sharding solves a different, harder problem: when the *instance itself* is the bottleneck, splitting data across genuinely separate machines is the only way to add more real capacity.

| | [Partitioning](../relational/partitioning.md) | Sharding |
|---|---|---|
| Pieces live on | The same database instance | Separate database instances/nodes |
| Adds real additional capacity (CPU/memory/disk)? | No | Yes |
| Query routing | Handled transparently by the database engine | Usually requires explicit shard-routing logic (application or [middleware](../../backend/middleware.md)) |
| Joins across pieces | Still possible — one engine, one transaction scope | Expensive or unsupported across shards |
| Typical trigger | One table has gotten unwieldy to scan/maintain | Total throughput or storage has outgrown any single instance |

## Sharding Strategies (Choosing a Shard Key)

The **shard key** is the value used to decide which shard a given row belongs on — getting this choice right is the single most consequential decision in a sharded design, because it's expensive to change later.

| Strategy | How it works | Trade-off |
|---|---|---|
| **Range-based** | Contiguous key ranges go to the same shard (e.g. user IDs 1–1M → Shard A) | Simple and supports efficient range queries, but can create "hot" shards if data/traffic isn't evenly distributed across the range (e.g. all new users landing on the newest, busiest shard) |
| **Hash-based** | A hash function applied to the shard key decides the shard, spreading rows evenly regardless of their natural distribution | Even load distribution, but destroys range-query locality — "all orders from last week" might now be scattered across every shard |
| **Directory-based** | A lookup service maps each key (or key range) to its shard explicitly | Maximum flexibility to rebalance or move individual keys between shards, at the cost of an extra lookup hop and the lookup service itself becoming a critical dependency |
| **Geography/tenant-based** | Rows are sharded by a natural business dimension — region, customer/tenant ID | Matches real-world data locality and regulatory requirements (keeping EU user data on EU shards), but can produce uneven shard sizes if tenants vary wildly in size |

## What Sharding Costs

Sharding is deliberately described as the *last* lever on the database-scaling ladder (after pooling, replicas, and [partitioning](../relational/partitioning.md)) because of what it costs, not just what it buys:

- **Cross-shard joins become expensive or impossible** — a query needing data from two different shards can't rely on the database engine to join them in one operation; the application has to fetch from both and join in code, or the schema has to be designed to avoid needing such joins at all.
- **Cross-shard transactions are a genuinely hard problem** — updating data on two shards atomically requires a distributed-transaction protocol (two-phase commit) or an architectural pattern like the [Saga pattern](../../distributed-systems/patterns/saga-pattern.md) instead of a normal single-database transaction.
- **Rebalancing is operationally heavy** — adding a new shard to relieve a hot one means physically moving a subset of data between live shards without downtime or data loss, which most systems need dedicated tooling for.
- **Uneven ("hot") shards defeat the purpose** — a poorly chosen shard key can concentrate traffic on one shard while others sit idle, which is worse than not sharding at all in terms of operational complexity for the capacity actually gained.
- **Application/[ORM](../../backend/data/orm.md) complexity goes up** — most application code and [ORMs](../../backend/data/orm.md) are written assuming a single logical database; sharding usually means either a shard-aware data access layer or a [middleware](../../backend/middleware.md)/proxy layer that hides the routing (at the cost of being another moving part to operate).

## Sharding in Practice: Built-in vs. Manual

| | Built-in sharding | Manual/application-level sharding |
|---|---|---|
| Who handles shard routing | The database itself | Application code or a dedicated routing layer |
| Examples | [MongoDB](../nosql/mongodb.md) (sharded clusters with a built-in `mongos` router), [Cassandra](../nosql/cassandra.md) (peer-to-peer [partitioning](../relational/partitioning.md) is sharding by design), [Elasticsearch](../search/elasticsearch.md)/[OpenSearch](../search/opensearch.md) (shards are a first-class concept), CockroachDB, Google Spanner | Sharding a traditional [PostgreSQL](../relational/postgresql.md)/[MySQL](../relational/mysql.md) deployment by hand, or via an extension/proxy (e.g. Citus for [PostgreSQL](../relational/postgresql.md), Vitess for [MySQL](../relational/mysql.md)) |
| Operational burden | Lower — the database manages shard placement, rebalancing, and routing | Higher — the team owns routing logic, rebalancing, and failure handling |
| When reached for | Default when the chosen database already supports it natively | When using a database that wasn't designed to be distributed, and adding sharding support after the fact |

Databases designed from the ground up for horizontal scale ([MongoDB](../nosql/mongodb.md), [Cassandra](../nosql/cassandra.md), and distributed-[SQL](../relational/sql.md) systems like CockroachDB/Spanner) treat sharding as a built-in, largely automatic feature — see [Distributed Databases](distributed-databases.md) for the broader theory these systems are built on. Traditional relational databases ([PostgreSQL](../relational/postgresql.md), [MySQL](../relational/mysql.md)) were not designed with sharding in mind, which is why sharding them means either adopting a sharding-aware extension/proxy or building the routing logic by hand.

## Common Questions

**Is sharding the same thing as replication?**
> No, and this is the single most common confusion. Replication copies the *same* data onto multiple nodes (every [replica](../relational/read-replicas.md) has everything) to improve read throughput and availability. Sharding splits *different* data across multiple nodes (each shard has a subset) to add real additional capacity. Production systems commonly use both together — each shard has its own set of [read replicas](../relational/read-replicas.md) for availability and read scaling within that shard.

**Does sharding fix slow queries?**
> Not directly — a query that's slow because of a missing [index](../relational/indexing.md) is still slow on a shard; sharding only helps when the actual problem is that total load/data volume exceeds what one instance can hold, not when the problem is a specific unoptimized query.

**Can you shard a database that's also using [read replicas](../relational/read-replicas.md) and [partitioning](../relational/partitioning.md)?**
> Yes, and in large systems this is normal, not exceptional — each shard can itself be an instance with its own [read replicas](../relational/read-replicas.md) for read scaling, and a large shard's own tables could even be [partitioned](../relational/partitioning.md) internally. The three techniques solve different problems and compose: [pooling](../relational/connection-pooling.md) reduces per-query overhead, replicas scale reads, [partitioning](../relational/partitioning.md) keeps one instance's tables manageable, and sharding adds more instances when one instance (however optimized internally) isn't enough.

**How do you pick a shard key?**
> Choose a key that distributes both data volume and query/write traffic evenly across shards, and that most queries can include in their filter (so queries can be routed to a single shard rather than fanning out to all of them). Getting this wrong is expensive to fix later since it usually means re-sharding — redistributing already-live data across a new shard layout.

## Related

- [Database Scaling Strategies](../../../overviews/databases/database-scaling-strategies.md) — the overview placing sharding as the final, most drastic step after pooling, replicas, and [partitioning](../relational/partitioning.md)
- [Partitioning](../relational/partitioning.md) — the single-instance precursor to sharding; sharding is [partitioning](../relational/partitioning.md)'s logic extended across separate machines
- [Read Replicas](../relational/read-replicas.md) — a composable, different scaling lever (copies vs. splits) often combined with sharding per-shard
- [Connection Pooling](../relational/connection-pooling.md) — the first, cheapest rung on the same scaling ladder sharding sits at the top of
- [Distributed Databases](distributed-databases.md) — the general multi-node theory (CAP theorem, consistency models) that sharded systems are built on
- [MongoDB](../nosql/mongodb.md) — a document database with sharding as a first-class, largely automatic built-in feature
- [Cassandra](../nosql/cassandra.md) — a wide-column database where [partitioning](../relational/partitioning.md) data across peer nodes (effectively sharding) is the core design, not an add-on
- [Saga Pattern](../../distributed-systems/patterns/saga-pattern.md) — the common pattern for handling a transaction that spans multiple shards without a native cross-shard transaction
- [Distributed Transactions](distributed-transactions.md) — the deeper treatment of why coordinating a write across more than one shard/node is hard
- [Horizontal Scaling](../../backend/architecture/horizontal-scaling.md) — the equivalent "add more instances" idea at the stateless application layer, which sharding mirrors at the (much harder, stateful) data layer
