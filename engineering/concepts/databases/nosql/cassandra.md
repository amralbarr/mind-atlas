# Apache Cassandra

Cassandra is a distributed wide-column database built for massive write throughput, fault tolerance, and no single point of failure — every node is equal (a peer-to-peer architecture with no primary/replica distinction), and it deliberately trades strong consistency for availability and partition tolerance. See [Distributed Databases](../distributed/distributed-databases.md) for how this compares to [MongoDB](mongodb.md) and distributed [SQL](../relational/sql.md) options.

## Core Concepts

| Term | Meaning |
|---|---|
| **Peer-to-peer architecture** | Every node in a Cassandra cluster is identical — there's no primary node coordinating writes, unlike [MongoDB](mongodb.md)'s primary/secondary replica set |
| **Partition key** | Determines which node(s) in the cluster own a given row — chosen carefully to spread data (and load) evenly across the cluster |
| **Replication factor** | How many nodes hold a copy of each piece of data — the mechanism behind fault tolerance, since any node can go down without data loss as long as enough replicas exist |
| **Consistency level** | Set **per query**, not globally — how many replicas must acknowledge a read/write before it's considered successful (`ONE`, `QUORUM`, `ALL`); this is where Cassandra lets an application explicitly choose its own consistency/availability tradeoff |
| **Tunable consistency** | The general name for the above — unlike a database with one fixed consistency model, Cassandra lets each query trade off latency/availability against consistency independently |
| **Multi-datacenter replication** | Built-in support for replicating data across geographically separate datacenters, each aware of the others' topology |

## Data Model (CQL — Cassandra Query Language)

```sql
CREATE KEYSPACE myapp
  WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 3};

CREATE TABLE myapp.events (
  device_id  UUID,
  event_time TIMESTAMP,
  payload    TEXT,
  PRIMARY KEY (device_id, event_time)
);
```

`device_id` is the partition key (decides which node owns this device's rows); `event_time` is a clustering column (sorts rows within that partition) — this shape is why Cassandra is a strong fit for time-series/IoT data: writes for one device always land on the same node, sorted by time, ready for efficient range queries.

## Reading/Writing with a Consistency Level

```python
from cassandra.cluster import Cluster
from cassandra import ConsistencyLevel
from cassandra.query import SimpleStatement

session = Cluster(['10.0.0.1', '10.0.0.2']).connect('myapp')

insert = SimpleStatement(
    "INSERT INTO events (device_id, event_time, payload) VALUES (%s, %s, %s)",
    consistency_level=ConsistencyLevel.QUORUM,
)
session.execute(insert, (device_id, event_time, payload))
```

`QUORUM` requires a majority of replicas to acknowledge the write before it's considered successful — a middle ground between `ONE` (fast, less durable) and `ALL` (fully durable, slowest, and unavailable if any replica is down).

## Common Questions

**Why is Cassandra described as prioritizing availability over consistency (CAP theorem)?**
> By default and by design, Cassandra favors staying available and partition-tolerant, accepting writes/reads even during a network partition, at the cost of returning possibly-stale data from some replicas until they converge ([eventual consistency](../../distributed-systems/patterns/eventual-consistency.md)). Tunable consistency levels let a specific query opt into stronger consistency (`QUORUM`, `ALL`) when correctness matters more than availability for that particular operation — see [Distributed Databases](../distributed/distributed-databases.md#cap-theorem).

**What workloads is Cassandra a poor fit for?**
> Anything needing flexible ad-hoc queries/joins across data — Cassandra's data model is designed around the queries you'll run being known in advance (denormalized, one table per query pattern), not a normalized relational model you can query arbitrarily. Complex joins or ad-hoc analytical queries are much better served by a [SQL](../relational/sql.md) database or a dedicated analytics store.

## Related

- [Distributed Databases](../distributed/distributed-databases.md)
- [MongoDB](mongodb.md)
- [ACID](../relational/acid.md)
