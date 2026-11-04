# Consensus Algorithms (Raft & Paxos)

A consensus algorithm lets a group of independent nodes agree on a single value or sequence of operations, even when some nodes are slow, crash, or the network between them is unreliable — the foundational building block underneath any distributed system that needs one consistent source of truth despite running on multiple, individually unreliable machines.

## Why Consensus Is Hard

In a single-machine system, "what's the current value of X" has one obvious answer. Across multiple machines connected by an unreliable network, that question gets genuinely hard: a message can be delayed, dropped, or arrive out of order; a node can crash and come back; two nodes might briefly believe they're each in charge. A consensus algorithm has to guarantee that, despite all of that, every non-faulty node eventually agrees on the same sequence of decisions — never landing on two different, conflicting answers.

## What Consensus Actually Guarantees

| Property | Meaning |
|---|---|
| **Agreement** | All correctly functioning nodes eventually agree on the same value/log |
| **Validity** | The agreed-upon value was actually proposed by some node — nodes can't "agree" on something nobody suggested |
| **Termination** | Every non-faulty node eventually decides, given enough time (assuming the network eventually stabilizes) |
| **Fault tolerance** | The system keeps working correctly as long as a *majority* of nodes are up and can communicate — this majority requirement is why consensus clusters are typically sized as odd numbers (3, 5, 7) |

## Why Majority (Quorum), Not Unanimity

Requiring every single node to agree would mean one crashed node halts the entire system — clearly unworkable. Consensus algorithms instead require a **majority (quorum)** of nodes to agree, which guarantees any two majorities always overlap by at least one node — that overlapping node is what prevents two conflicting decisions from both being accepted, even if the cluster is split by a network partition.

```text
5-node cluster: needs 3 nodes to agree (majority)
Any two possible majorities of 3 out of 5 must share at least 1 node
   → that shared node prevents a split-brain "double decision"
```

This is also why clusters are sized as odd numbers: a 4-node cluster tolerates the same single-node-failure count as a 3-node cluster (both need a majority of the remaining nodes) but costs one more machine for no extra fault tolerance.

## Paxos

Paxos, introduced by Leslie Lamport, was the original rigorously proven consensus algorithm — and is notoriously difficult to understand and implement correctly, to the point that its own foundational paper spawned a cottage industry of "Paxos made simple/moderately complex" explanations. At a high level, it works through two phases per round:

1. **Prepare phase** — a node proposing a value asks a majority "has anyone proposed something with a higher round number than mine?"
2. **Accept phase** — if no higher proposal exists, the node asks that same majority to actually accept its value.

Paxos is correct and foundational, but its difficulty in practice (especially the "multi-Paxos" extension needed for a continuously replicated log, rather than agreeing on one single value) is exactly the gap Raft was designed to close.

## Raft

Raft was explicitly designed as an easier-to-understand alternative to Paxos, while providing equivalent guarantees — and largely succeeded, becoming the consensus algorithm of choice in most modern systems built after its 2014 publication. Raft achieves this by splitting the problem into three separable sub-problems: **leader election**, **log replication**, and **safety**.

### Leader Election

At any time, a Raft cluster has at most one **leader**; every other node is a **follower**. Only the leader accepts writes and replicates them to followers — this is what makes Raft's model easier to reason about than Paxos's leaderless, symmetric design.

```text
Follower  Follower  Follower
    │         │         │
    └────── heartbeats from Leader ──────┘

If followers stop hearing heartbeats (leader crashed):
  → a follower's election timeout fires
  → it becomes a candidate, requests votes from the rest of the cluster
  → if it gets a majority of votes, it becomes the new leader
```

### Log Replication

Once a leader is elected, every write is appended to the leader's log and replicated to a majority of followers before being considered "committed" (safe, durable, guaranteed not to be lost even if the leader immediately crashes):

```text
Client write → Leader appends to its log
             → Leader replicates entry to followers
             → Once a majority of nodes have the entry: committed
             → Leader applies it and responds to the client
```

### Why This Matters Practically

This leader-plus-majority-replication design is exactly what underlies:

- **etcd** ([Kubernetes](../kubernetes/ingress.md)' own configuration/coordination store) — uses Raft to keep its cluster consistent, which is why [Kubernetes](../kubernetes/ingress.md) itself can tolerate a control-plane node failing without losing cluster state.
- **[NATS JetStream](../messaging/nats.md)** and **CockroachDB/TiDB** — use Raft for replicating data/log entries across nodes.
- **[Kafka's KRaft mode](../messaging/kafka.md)** — [Kafka](../messaging/kafka.md) replaced its older ZooKeeper-based coordination with a Raft-based consensus protocol (KRaft) for managing cluster metadata itself.

## Raft vs. Paxos

| | Paxos | Raft |
|---|---|---|
| Understandability | Notoriously difficult, even for experts | Explicitly designed to be teachable |
| Leader model | No inherent leader in the base algorithm (symmetric roles); multi-Paxos adds one informally | A single leader is a first-class, core part of the design |
| Practical adoption | Historically significant, used in Google Chubby/Spanner | Dominant choice in newer systems (etcd, CockroachDB, [NATS](../messaging/nats.md) JetStream, [Kafka](../messaging/kafka.md) KRaft) |
| Guarantees | Equivalent — both solve the same fundamental problem | Equivalent |

Raft didn't out-compete Paxos on correctness or performance — both provide the same guarantees — it won on the practical grounds of being implementable correctly by ordinary engineering teams without years of distributed-systems research background.

## Consensus vs. Eventual Consistency

These solve different problems and are sometimes wrongly treated as alternatives: consensus produces a single, strongly agreed-upon sequence of operations (strong consistency, at the cost of requiring a majority to be reachable); [eventual consistency](eventual-consistency.md) explicitly tolerates temporary disagreement between replicas in exchange for availability even during a partition. A system might use consensus internally for its own metadata/leader election (like [Kafka](../messaging/kafka.md)'s KRaft) while offering eventually-consistent reads to its own clients (like [Cassandra](../../databases/nosql/cassandra.md)) — these are independent design choices at different layers.

## Common Questions

**Do all [distributed databases](../../databases/distributed/distributed-databases.md) use Raft or Paxos internally?**
> No — only systems that need strong consistency/a single agreed-upon log do (CockroachDB, etcd, Spanner-family systems). Systems designed around [eventual consistency](eventual-consistency.md) instead ([Cassandra](../../databases/nosql/cassandra.md), DynamoDB) deliberately avoid the coordination cost of consensus for ordinary reads/writes, trading strict ordering guarantees for availability and lower latency.

**What happens if a Raft cluster loses its majority (e.g. 3 out of 5 nodes go down)?**
> The cluster stops accepting new writes entirely (it can't reach quorum) rather than risk an inconsistent decision — this is Raft explicitly choosing consistency over availability during a severe partition, directly reflecting the [CAP theorem](../../databases/distributed/distributed-databases.md#cap-theorem)'s trade-off.

**Is a consensus algorithm the same thing as a distributed lock?**
> Related but different in scope — a [distributed lock](distributed-locks.md) is a narrower, often best-effort mechanism for one piece of mutual exclusion (Redis TTL+token locks, for instance, explicitly don't provide the same formal guarantees as Raft/Paxos). Consensus algorithms are the more rigorous, general-purpose foundation that a distributed lock service could itself be *built on* (e.g. etcd's locks are built on top of its Raft-replicated log) for stronger correctness guarantees.

## Related

- [Distributed Systems Overview](distributed-systems-overview.md)
- [Distributed Locks](distributed-locks.md)
- [Eventual Consistency](eventual-consistency.md)
- [Kafka](../messaging/kafka.md)
- [NATS](../messaging/nats.md)
- [Kubernetes Basics](../kubernetes/kubernetes-basics.md)
