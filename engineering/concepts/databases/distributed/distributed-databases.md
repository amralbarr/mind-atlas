# Distributed Databases

A distributed database is a database spread across multiple servers or nodes that work together and present themselves as one logical database system.

Instead of:

```text
Application → One PostgreSQL Server
```

you have:

```text
Application → DB Node 1
            → DB Node 2
            → DB Node 3
            → DB Node 4
```

All nodes cooperate to serve as a single system.

## Why Distributed Databases Exist

A single database server has hard limits: CPU, RAM, storage, and network throughput. Eventually you cannot scale vertically forever. The distributed approach solves this by scaling horizontally — adding more database nodes instead of a bigger single machine — in exchange for:

- Scalability
- High availability
- Fault tolerance
- Geographic distribution

## The Landscape

### Distributed NoSQL Databases

| Database | Type |
|---|---|
| [Apache Cassandra](../nosql/cassandra.md) | Wide-column |
| [MongoDB](../nosql/mongodb.md) | Document |
| Redis | Key-value — see [Redis Lists](../../distributed-systems/messaging/redis-lists.md) |
| [Apache Kafka](../../distributed-systems/messaging/kafka.md) | Distributed log |
| Couchbase | Document |

### Distributed SQL Databases

| Database | Type |
|---|---|
| CockroachDB | Distributed [SQL](../relational/sql.md) |
| Google Spanner | Distributed [SQL](../relational/sql.md) |
| TiDB | Distributed [SQL](../relational/sql.md) |

## Core Concepts

### Replication

Data is copied across multiple nodes (Node A, Node B, Node C all hold the same data) for fault tolerance, high availability, backups, and read scaling. If one node fails, the others still have the data.

### Sharding (Partitioning)

Data is split across nodes rather than copied:

```text
Users 1-1000    → Node A
Users 1001-2000 → Node B
Users 2001-3000 → Node C
```

[Sharding](sharding.md) distributes storage, reads, and writes across machines, and is what enables [horizontal scaling](../../backend/architecture/horizontal-scaling.md) — you scale by adding nodes.

### Consistency

When data is replicated, all copies must stay synchronized — a genuinely hard problem. For example, when a user updates their profile, Node A may update immediately while Node B lags behind, producing temporary inconsistency.

- **Strong consistency** — all nodes are synchronized immediately.
- **[Eventual consistency](../../distributed-systems/patterns/eventual-consistency.md)** — data becomes consistent over time. Common in distributed NoSQL systems.

### CAP Theorem

Distributed databases are heavily shaped by the CAP theorem: a distributed system can only fully guarantee two of the following three at once:

- Consistency
- Availability
- Partition tolerance

## Case Studies

Two of the most commonly deployed distributed NoSQL databases, each with its own dedicated note covering data modeling, replication/[sharding](sharding.md) mechanics, and hands-on query examples:

- **[MongoDB](../nosql/mongodb.md)** — document database; replica sets for high availability (automatic primary failover), [sharding](sharding.md) for horizontal scale.
- **[Cassandra](../nosql/cassandra.md)** — wide-column, peer-to-peer (no primary node), built for massive write throughput and multi-datacenter replication, with per-query tunable consistency trading off availability against correctness.

## SQL vs Distributed NoSQL

| Feature | Traditional [SQL](../relational/sql.md) | Distributed NoSQL |
|---|---|---|
| Scaling | Mostly vertical | Horizontal |
| Consistency | Strong | Often eventual |
| Schema | Fixed | Flexible |
| Joins | Strong | Limited |
| Transactions | Strong [ACID](../relational/acid.md) | Often weaker |

## ACID vs BASE

**[ACID](../relational/acid.md) (traditional [SQL](../relational/sql.md))** — Atomicity, Consistency, Isolation, Durability. Prioritizes correctness. See [ACID](../relational/acid.md) for the full breakdown.

**BASE (many distributed NoSQL systems)** — Basically Available, Soft state, [Eventual consistency](../../distributed-systems/patterns/eventual-consistency.md). Prioritizes scalability and availability over strict correctness guarantees.

## Distributed Transactions

A genuinely difficult topic: running a transaction across multiple nodes or services. Classic example — a bank transfer must update account A and account B consistently across a distributed system. Common solutions include two-phase commit, the [Saga pattern](../../distributed-systems/patterns/saga-pattern.md), and event sourcing. See [Distributed Transactions](distributed-transactions.md) for a deeper treatment.

## Common Challenges

1. **Network partitions** — nodes cannot communicate with each other.
2. **Data synchronization** — keeping replicas up to date.
3. **Conflict resolution** — two nodes updating the same data simultaneously.
4. **Query complexity** — distributed joins are expensive.
5. **Latency** — cross-node communication is inherently slower than local access.

## Benefits

- High availability
- Horizontal scalability
- Fault tolerance
- Geographic distribution
- Support for massive datasets

## Real-World Use Cases

- **[Cassandra](../nosql/cassandra.md)** — telemetry, IoT, logs, time-series data, massive write workloads.
- **[MongoDB](../nosql/mongodb.md)** — flexible documents, scalable web apps, evolving schemas.
- **CockroachDB / Spanner** — distributed [SQL](../relational/sql.md) with global consistency guarantees.

## Important Distinction

A distributed database is not the same thing as microservices. You can have a monolith backed by a distributed database, or microservices backed by a single database — these are independent architecture decisions. See [System Design](../../backend/architecture/system-design.md) and [Monolith vs Microservices](../../backend/architecture/monolith-vs-microservices.md) for the broader architectural context.

## Common Questions

**What is a distributed database?**

> A distributed database stores and manages data across multiple nodes while presenting itself as a single, unified database system.

**What is replication?** Copying the same data to multiple nodes for availability and fault tolerance.

**What is [sharding](sharding.md)?** Splitting data across nodes to distribute load and scale horizontally.

**Difference between replication and [sharding](sharding.md)?**

| Replication | [Sharding](sharding.md) |
|---|---|
| Copies the same data | Splits the data |
| Optimizes for availability | Optimizes for scalability |

**What is [eventual consistency](../../distributed-systems/patterns/eventual-consistency.md)?** Replicas may temporarily differ but eventually synchronize.

**Why are distributed databases hard?** Consistency, partitions, replication, and coordination all compound.

**Senior-level summary:**

> Distributed databases partition and replicate data across multiple nodes to achieve scalability, fault tolerance, and high availability. They introduce challenges around consistency, coordination, and [distributed transactions](distributed-transactions.md), often requiring tradeoffs defined by the CAP theorem.

## Key Takeaway

```text
Replication = copy data
Sharding    = split data
```

## Related

- [MongoDB](../nosql/mongodb.md)
- [Cassandra](../nosql/cassandra.md)
- [ACID](../relational/acid.md)
- [Distributed Transactions](distributed-transactions.md)
- [Distributed Systems Overview](../../distributed-systems/patterns/distributed-systems-overview.md)
- [Network Communication](../../distributed-systems/patterns/network-communication.md)
- [Kafka](../../distributed-systems/messaging/kafka.md)
- [Eventual Consistency](../../distributed-systems/patterns/eventual-consistency.md)
- [Read Replicas vs. Write Replicas](../relational/read-replicas.md)
- [Consensus Algorithms (Raft & Paxos)](../../distributed-systems/patterns/consensus-algorithms.md)
- [Sharding](sharding.md) — the dedicated atomic note on the [sharding](sharding.md) concept this file summarizes in its Core Concepts and Common Questions sections
- [Partitioning](../relational/partitioning.md) — the single-instance technique this file's "[Sharding](sharding.md) ([Partitioning](../relational/partitioning.md))" heading conflates with [sharding](sharding.md); the two are distinct (same instance vs. separate instances) per that note
- [Database Scaling Strategies](../../../overviews/databases/database-scaling-strategies.md) — ties sharding together with [connection pooling](../relational/connection-pooling.md), [read replicas](../relational/read-replicas.md), and [partitioning](../relational/partitioning.md) as one ordered scaling progression
