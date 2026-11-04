# Eventual Consistency

Eventual consistency is a consistency model where replicas of the same data are allowed to temporarily disagree, with the guarantee that — assuming no new writes arrive — every replica will *eventually* converge to the same value. It trades immediate, guaranteed-fresh reads for higher availability and lower latency, especially across geographically distributed nodes.

## Strong vs. Eventual Consistency

| | Strong Consistency | Eventual Consistency |
|---|---|---|
| A read right after a write | Always sees the latest write, everywhere | May see a stale (older) value for some period of time |
| Coordination required | Every read/write may need to check with other nodes/a majority | Writes can be accepted locally and propagated later |
| Availability during a partition | Often sacrificed — a node may refuse to serve a read/write it can't confirm is current | Preserved — a node serves what it has, even if it hasn't heard the latest update yet |
| Typical latency | Higher (coordination cost) | Lower (no need to wait for other replicas) |
| Example systems | Traditional single-primary [SQL](../../databases/relational/sql.md) databases, [Raft/Paxos-based](consensus-algorithms.md) systems | [Cassandra](../../databases/nosql/cassandra.md), DynamoDB, [DNS](../../networking/dns.md), most [CDN](../../networking/cdn.md) caches |

## A Concrete Illustration

```text
t=0: User updates their profile picture
     Node A (where the write landed): has the new picture immediately
     Node B (a replica, hasn't synced yet): still has the old picture

t=0 to t=X: A request routed to Node B returns the OLD picture — this is
            the "eventual" window; the system is temporarily inconsistent
            but not broken

t=X: replication catches up
     Node B now also has the new picture — the system has converged
```

The length of that window (`X`) depends entirely on the system's replication mechanism and network conditions — it might be milliseconds within one datacenter or longer across regions, but it's never instantaneous the way strong consistency promises.

## Why Systems Choose Eventual Consistency Deliberately

This isn't a limitation being tolerated — for many workloads it's the *better* trade-off:

- **Availability during partitions** — per the [CAP theorem](../../databases/distributed/distributed-databases.md#cap-theorem), a system can't have perfect consistency, availability, *and* partition tolerance simultaneously; eventually consistent systems choose to keep serving reads/writes even when replicas can't currently reach each other, rather than refusing requests until connectivity is restored.
- **Lower latency** — not waiting for cross-region/cross-node confirmation before responding means faster reads and writes, which matters enormously for user-facing latency at global scale.
- **Better write throughput** — accepting a write locally and replicating asynchronously means a write doesn't block on the slowest replica in the cluster.

Not every piece of data needs strong consistency — a social media "like" count being briefly stale for a few hundred milliseconds is invisible to users and utterly inconsequential; a bank balance being briefly stale during a double-spend check is not. The right consistency model is a per-use-case decision, not a universal default.

## BASE, as the Counterpart to ACID

Eventually consistent systems are often described by the acronym **BASE**, deliberately contrasted with the [ACID](../../databases/relational/acid.md) guarantees of traditional relational databases:

| BASE | Meaning |
|---|---|
| **B**asically **A**vailable | The system guarantees availability, even under partition/failure |
| **S**oft state | State may change over time even without new input, as replicas converge |
| **E**ventual consistency | Given enough time without new writes, all replicas converge to the same value |

## Conflict Resolution: What Happens When Two Writes Disagree

Allowing writes to be accepted independently on different nodes means two conflicting writes to the same piece of data can genuinely happen concurrently — eventual consistency needs a rule for resolving that when replicas finally compare notes:

| Strategy | How it resolves conflicts |
|---|---|
| **Last-write-wins (LWW)** | The write with the latest timestamp wins; simple, but can silently discard a legitimate concurrent write if clocks are even slightly out of sync |
| **Vector clocks** | Track causal history per replica to detect *true* concurrent writes (versus one write that causally happened after another) rather than relying on wall-clock time alone |
| **CRDTs (Conflict-free Replicated Data Types)** | Data structures specifically designed so that concurrent updates can always be merged deterministically without conflict (e.g. a counter that only ever increments, or a set using union as its merge rule) |
| **Application-level resolution** | Surface the conflict to the application (or even the end user, as in some collaborative editors) to decide how to merge — used when neither automatic strategy above is safe for the specific data |

## Read-Your-Own-Writes: A Common Middle Ground

Pure eventual consistency (any replica, any time) is often too weak for good user experience — a user who just posted a comment expects to see it immediately, even if other users briefly don't. **Read-your-own-writes consistency** is a common relaxation: the *same client* is guaranteed to see its own recent writes (often by routing that client's subsequent reads to the replica/primary that accepted the write, or a session-scoped consistency token), while other clients may still see a stale view for a short window.

## Where This Shows Up in Practice

| System | How it applies |
|---|---|
| **[Cassandra](../../databases/nosql/cassandra.md)** | Tunable per-query consistency level (`ONE`, `QUORUM`, `ALL`) — lets each query trade off consistency vs. availability/latency individually |
| **[DNS](../../networking/dns.md)** | Propagation delay after a record change is a real-world, everyday instance of eventual consistency — different resolvers around the world converge on the new record over time, not instantly |
| **[CDN](../../networking/cdn.md) caches** | An updated origin file may take time to propagate/invalidate across every edge node |
| **Distributed caches** | A write-behind cache (see [Caching Strategies](../../backend/architecture/caching-strategies.md)) is eventually consistent with its backing store by design |

## Common Questions

**Is eventual consistency "wrong" or a compromise a system is forced into?**
> Neither — it's a deliberate design choice that better fits many real workloads (higher availability, lower latency, better write throughput) at the cost of a brief, bounded staleness window. Strong consistency is the compromise for workloads that genuinely can't tolerate any staleness (financial transactions, inventory counts near zero) — each model is correct for different requirements, not universally superior.

**How would a client know if the data it just read is stale?**
> Generally, it can't tell from the data alone — this is exactly the trade-off. Some systems expose extra metadata (a version number, a "read consistency level" the client requested) to make staleness detectable/boundable, but the raw guarantee itself doesn't self-report "this might be old."

**Does eventual consistency mean data can be permanently inconsistent?**
> No — "eventual" is a genuine guarantee, not a hand-wave: assuming writes stop and replicas can communicate, they are guaranteed to converge. The concern is the *duration* and *unpredictability* of that window, not whether convergence happens at all.

## Related

- [Distributed Databases](../../databases/distributed/distributed-databases.md)
- [Distributed Systems Overview](distributed-systems-overview.md)
- [Cassandra](../../databases/nosql/cassandra.md)
- [ACID](../../databases/relational/acid.md)
- [Consensus Algorithms](consensus-algorithms.md)
- [Caching Strategies](../../backend/architecture/caching-strategies.md)
