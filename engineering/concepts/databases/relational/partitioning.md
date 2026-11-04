# Database Partitioning

Partitioning splits **one logical table** into smaller physical pieces — partitions — that still live within the **same database instance**, based on a partition key. The database (or the application) routes a given row to the right partition automatically, and queries that include the partition key can skip scanning partitions that can't possibly contain a match. This is the step typically reached for once a single table has grown large enough that scans, index maintenance, and bulk operations (archiving old data, vacuuming) on the whole table are getting expensive — but before write throughput itself has outgrown what one instance can handle (that's [sharding](../distributed/sharding.md), a different, more drastic step — see the distinction below).

```text
Logical table: orders (100M rows)

Partition by range on created_at:

orders_2024_q1  (rows where created_at in Q1 2024)
orders_2024_q2  (rows where created_at in Q2 2024)
orders_2024_q3  (rows where created_at in Q3 2024)
orders_2024_q4  (rows where created_at in Q4 2024)

All four partitions still live on the SAME database server.
```

A query like `SELECT * FROM orders WHERE created_at >= '2024-07-01'` only needs to scan `orders_2024_q3` and `orders_2024_q4` — this is called **partition pruning**, and it's the main performance win partitioning delivers.

## Partitioning Strategies

| Strategy | How rows are assigned | Good fit when |
|---|---|---|
| **Range** | A column's value falls within a defined range (dates, numeric IDs) | Time-series data, anything naturally queried by date range — the most common strategy in practice |
| **List** | A column's value matches one of an explicit, enumerated set (a country code, a status enum) | A small, known number of discrete categories that queries commonly filter on |
| **Hash** | A hash function applied to the partition key decides the partition | No natural range or list grouping exists, but even distribution across partitions is wanted |
| **Composite** | Two strategies combined (e.g. range by date, then hash within each range) | Very large tables where a single strategy alone doesn't distribute evenly |

### Range Partitioning Example (PostgreSQL)

```sql
CREATE TABLE orders (
    id BIGINT,
    created_at TIMESTAMP,
    customer_id BIGINT,
    total NUMERIC
) PARTITION BY RANGE (created_at);

CREATE TABLE orders_2024_q1 PARTITION OF orders
    FOR VALUES FROM ('2024-01-01') TO ('2024-04-01');

CREATE TABLE orders_2024_q2 PARTITION OF orders
    FOR VALUES FROM ('2024-04-01') TO ('2024-07-01');
```

Applications still query the `orders` table as if it were a single table — [PostgreSQL](postgresql.md) transparently routes each query to the relevant partition(s) underneath.

### Hash Partitioning Example

```sql
CREATE TABLE users (
    id BIGINT,
    email TEXT
) PARTITION BY HASH (id);

CREATE TABLE users_p0 PARTITION OF users FOR VALUES WITH (MODULUS 4, REMAINDER 0);
CREATE TABLE users_p1 PARTITION OF users FOR VALUES WITH (MODULUS 4, REMAINDER 1);
CREATE TABLE users_p2 PARTITION OF users FOR VALUES WITH (MODULUS 4, REMAINDER 2);
CREATE TABLE users_p3 PARTITION OF users FOR VALUES WITH (MODULUS 4, REMAINDER 3);
```

Hash partitioning trades away partition pruning for range queries (there's no meaningful "range" of hash values to prune by) in exchange for even row distribution across partitions regardless of the actual data distribution.

## What Partitioning Actually Buys

| Benefit | Why |
|---|---|
| **Faster queries that filter on the partition key** | Partition pruning skips irrelevant partitions entirely instead of scanning the whole table |
| **Cheaper maintenance** | `VACUUM`, `REINDEX`, and statistics updates run per-partition — a stale quarter's partition can be reindexed without touching current data |
| **Fast bulk deletes** | Dropping an entire old partition (e.g. `DROP TABLE orders_2022_q1`) is near-instant compared to a `DELETE` with a `WHERE` clause scanning and removing millions of rows row-by-row |
| **Smaller, more cache-friendly working set** | A query touching only recent data only needs the index/pages of the relevant partition to be hot in memory, not the entire historical table |

## What Partitioning Does NOT Solve

Partitioning does not add another machine's worth of CPU, memory, or disk — all partitions still compete for the same instance's resources. A table partitioned four ways on an overloaded single server is still bottlenecked by that one server's total capacity; it's just organized more efficiently within it. Once total write throughput or total storage genuinely exceeds what one instance can handle no matter how it's internally organized, the next step is [sharding](../distributed/sharding.md) — spreading data across *separate* database instances, not just separate structures within one. See [Database Scaling Strategies](../../../overviews/databases/database-scaling-strategies.md) for where partitioning sits in that broader progression.

## Partitioning vs. Sharding

These are frequently confused because both split data by a key, but they differ in one essential way:

| | Partitioning | [Sharding](../distributed/sharding.md) |
|---|---|---|
| Where the pieces live | All partitions on the **same** database instance | Each shard on a **separate** database instance/node |
| Adds more total compute/storage capacity? | No — still bounded by one machine | Yes — each new shard is a new machine's worth of resources |
| Query routing | Handled transparently by the database engine itself | Usually requires application-level or [middleware](../../backend/middleware.md)-level routing logic to know which node holds which shard |
| Cross-partition/cross-shard joins | Still possible — it's still one database engine, one transaction scope | Expensive or outright unsupported — joining across separate database instances is a fundamentally harder problem |
| Typical trigger | A single table has grown unwieldy to scan/maintain | Total throughput or storage has outgrown what any single instance (partitioned or not) can hold |

## Partitioning vs. Indexing

Both make queries faster by avoiding unnecessary scanning, but at different granularities: an [index](indexing.md) narrows a scan down to specific rows *within* a table (or partition); partitioning narrows which *partitions* even need to be considered before any index lookup happens. In practice they're complementary, not alternatives — a large partitioned table still has indexes defined per-partition (or globally, depending on the database) to speed up lookups within whichever partition(s) a query touches.

## Common Questions

**Does partitioning require changing how the application queries the table?**
> Generally no — the application still issues normal queries against the logical table name, and the database's query planner figures out which partitions to touch based on the `WHERE` clause and the partition key. The one place this breaks down is a query with no filter on the partition key at all, which forces a scan across every partition — effectively erasing the benefit.

**Can you partition a table that's already read-replicated?**
> Yes — partitioning and [read replicas](read-replicas.md) address different problems (table-scan/maintenance cost vs. read throughput) and compose normally: a primary's partitioned table replicates to [read replicas](read-replicas.md) the same way an unpartitioned one would.

**Is partitioning only useful for huge tables?**
> Mostly, yes — partitioning adds real complexity (migration work, careful partition-key choice, more moving pieces to monitor), so it's usually not worth adopting until a table is large enough (commonly cited in the tens of millions of rows and up, though this varies by workload) that scan/maintenance costs are actually causing problems.

## Related

- [Sharding](../distributed/sharding.md) — the next step once partitioning's single-instance ceiling is reached, splitting data across separate database instances instead of within one
- [Database Scaling Strategies](../../../overviews/databases/database-scaling-strategies.md) — where partitioning sits in the overall database scaling progression (pooling → replicas → partitioning → [sharding](../distributed/sharding.md))
- [Database Indexing](indexing.md) — a complementary, finer-grained technique that still applies within each partition
- [Read Replicas](read-replicas.md) — a separate, composable scaling lever addressing read throughput rather than table/maintenance size
- [PostgreSQL](postgresql.md) — the database the worked `PARTITION BY` examples above target
- [Distributed Databases](../distributed/distributed-databases.md) — the broader multi-node theory that [sharding](../distributed/sharding.md) (partitioning's cross-instance successor) is one instance of
