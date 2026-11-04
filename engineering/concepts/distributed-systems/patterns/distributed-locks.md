# Distributed Locks

An ordinary in-process mutex only coordinates threads inside one process — it's useless the moment two separate processes (or servers) can race to touch the same shared resource. A **distributed lock** solves that by using a shared external store (commonly [Redis](../messaging/redis-lists.md)) that every process can check against, so only one holder can proceed at a time regardless of which machine it's running on.

## When You Need One

Whenever multiple independent processes could otherwise race to change the same piece of external state simultaneously — for example, three requests each trying to start/stop models on the *same* physical GPU at once. Without coordination:

```text
request A: stopping model X
request B: starting model Y      } all racing to mutate
request C: starting video model  } the same GPU's state
```

can interleave into an inconsistent result (e.g. both B and C believe they reserved the freed VRAM). See [Idempotency & Race Conditions](../../programming/fundamentals/idempotency-and-race-conditions.md) for the broader principle this is one instance of — and note that a single atomic database operation is often a *simpler* fix than a lock when the whole operation can be expressed that way. A distributed lock earns its complexity specifically when the critical section spans multiple steps or multiple systems that can't be collapsed into one atomic write (e.g. "check GPU telemetry, then decide, then issue a start/stop command to a remote agent").

## The Three Failure Modes a Naive Lock Doesn't Handle

| Problem | What goes wrong |
|---|---|
| Holder crashes without releasing | Every other process waits forever — a lock with no expiry is a single point of total deadlock |
| Holder is slower than expected | If the lock expires while the holder is still working, a second process can acquire it while the first still believes it holds it — now two "exclusive" holders exist simultaneously |
| Releasing someone else's lock | Process A's lock expires, Process B acquires it, then A finishes late and calls "release" — accidentally releasing B's lock |

## The Real Pattern: TTL + Ownership Token + Renewal

```javascript
// Acquire: only succeeds if the key doesn't already exist
const token = crypto.randomUUID();
const acquired = await redis.set(
  'lock:gpu:gpu-node-01:0',
  token,
  { NX: true, PX: 10_000 } // NX = only if not exists, PX = 10s TTL
);

// Renewal (while still doing work): extend the TTL periodically
// so a slow-but-alive holder doesn't get preempted

// Release: only delete if the token still matches — never blind-delete
// (a Lua script makes this check-and-delete atomic)
if (await redis.get(key) === token) {
  await redis.del(key);
}
```

| Piece | Solves |
|---|---|
| **TTL** | Guarantees the lock is eventually released even if the holder crashes |
| **Ownership token** (a unique value per acquisition, not just a boolean) | Lets release be conditional — "only delete if I'm still the owner" — preventing the accidental-release-of-someone-else's-lock bug above |
| **Renewal** | Lets a holder extend its own TTL while genuinely still working, instead of picking one fixed TTL that's either too short (false expiry) or too long (slow failure recovery) |
| **Atomic check-and-delete** | The release step itself must be a single atomic operation (a Lua script in Redis), or the check and the delete can race against a new acquirer between them |

## Redlock and Multi-Node Redis

A single Redis instance is itself a single point of failure for the lock. **Redlock** is an algorithm for acquiring the same lock across a majority of independent Redis nodes, so the lock survives any one node failing — at the cost of real implementation complexity, and some disagreement in the distributed-systems community about its correctness guarantees under clock drift. For most internal use cases (like serializing GPU state changes within one cluster), a single well-configured Redis instance with TTL+token is enough; reach for Redlock only when the lock's correctness genuinely can't tolerate that single Redis instance being briefly unavailable.

## Common Questions

**Why not just use a database row with a `SELECT ... FOR UPDATE`?**
> That works too — it's exactly the mechanism behind [pessimistic locking](../../databases/relational/pessimistic-locking.md) — and is a reasonable choice when you're already inside a transaction against that database. A dedicated lock service like Redis is preferred when the critical section spans systems the database transaction can't reach (e.g. also calling a remote agent's [HTTP](../../networking/http.md) API), or when lock acquisition needs to be much faster/higher-throughput than a full DB transaction.

**What happens if the process holding the lock is just slow, not crashed?**
> This is exactly why renewal exists — a genuinely-still-working holder should be extending its own TTL periodically ("I'm still here, still working"), so only an actually-dead holder's lock expires. Without renewal, you're forced to guess one fixed TTL that's either too short (false expiry, second holder jumps in) or too long (real crash recovery takes ages).

## Related

- [Idempotency & Race Conditions](../../programming/fundamentals/idempotency-and-race-conditions.md)
- [Redis Lists](../messaging/redis-lists.md)
- [GPU-Aware Scheduling](../../ai/infrastructure/gpu-scheduling.md)
- [Distributed Systems Overview](distributed-systems-overview.md)
- [Consensus Algorithms (Raft & Paxos)](consensus-algorithms.md)
- [Pessimistic Locking](../../databases/relational/pessimistic-locking.md) — the single-database version of this same block-before-touching-shared-state idea, via `SELECT ... FOR UPDATE` instead of a Redis-backed lock
- [Optimistic Locking](../../databases/relational/optimistic-locking.md) — the opposite strategy when the shared state lives in one database and conflicts are rare enough to detect after the fact instead of locking up front
