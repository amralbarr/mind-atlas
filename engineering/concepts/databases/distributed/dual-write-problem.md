# The Dual-Write Problem

The **dual-write problem** occurs whenever a single logical operation requires writing to two different systems — two databases, a database and a cache, a database and a message broker, a database and a search index — with no shared transaction spanning both. If the first write succeeds and the second fails, the two systems silently diverge, and nothing in the code path knows it happened.

```
1. Write to System A  ✅ succeeds
2. Write to System B  ❌ fails (network blip, System B down, timeout)

Result: System A has the new state, System B doesn't.
No error reached the caller that clearly identifies *this specific* divergence,
and nothing automatically retries just the missing half.
```

This is a strictly harder problem than a single system's own transaction failure, because there is no cross-system equivalent of a database's atomic commit — System A has no way to "roll back" once it's already committed, and System B has no way to know a write was ever attempted.

## Where It Shows Up

| Pair | Concrete example |
|---|---|
| **Database + message broker** | Save an order to the database, then publish an `OrderCreated` event to [Kafka](../../distributed-systems/messaging/kafka.md) — see [Distributed Transactions — The Dual-Write Problem](distributed-transactions.md#the-dual-write-problem) for this exact case and its fix, the outbox pattern |
| **Database + cache** | Update a user's record, then invalidate/update the cached copy — see [Cache Invalidation](../../backend/architecture/caching-strategies.md#cache-invalidation) |
| **Database + search index** | Update a document's permission fields in a primary store, then update the corresponding fields in [Azure AI Search](../../cloud/azure/azure-ai-search.md) or a vector store's metadata — exactly [Flow H](../../../interview/interview-01/22-azure-rag-platform-map.md#h--document-permission-change-flow) of the [Azure](../../cloud/azure/azure.md) [RAG](../../ai/rag/rag.md) platform map, where a permission-change handler writes to both the search index and pgvector metadata |
| **Database migration cutover** | Writing to both the old and new database during a phased migration, before cutting reads over entirely |

The underlying shape is identical every time: two writes, no shared atomicity, a real window where they can disagree.

## The Three Real Fixes

| Fix | How it works | Best for |
|---|---|---|
| **Outbox pattern** | Write the intended second-system event into an "outbox" table in the *same* transaction as the primary write, then a separate process reads the outbox and delivers to the second system, retrying until it succeeds | Database + message broker, where the broker delivery can be made eventually-reliable through retry |
| **Change Data Capture (CDC)** | Never write to the second system directly at all — instead, read the primary database's own write-ahead log/replication stream and derive the second system's state from it | Keeping a search index or cache in sync with a database, without the application code ever performing the second write itself |
| **Accept [eventual consistency](../../distributed-systems/patterns/eventual-consistency.md) + reconciliation** | Let the two systems drift briefly, and run a periodic job that detects and repairs divergence | Cases where perfect real-time consistency isn't required, but silent permanent drift still isn't acceptable |

Notice what all three have in common: none of them make the two writes atomic — that's not actually achievable without a distributed transaction coordinator (2PC), which has its own well-known availability costs. Instead, each fix makes the *failure* recoverable: the outbox retries until it succeeds, CDC never attempts a second independent write at all, and reconciliation catches whatever a retry-based approach still missed.

## Fail Closed, Not Open, on the Second Write

When neither outbox nor CDC is in place and a direct second write is unavoidable (common for a permission-sensitive field, as in the search-index example above), the second write's failure mode matters as much as its success path: a failed permission-sync write should **deny access to the affected content until the write is confirmed**, not silently leave the first system's new permissions live while the second system still serves under stale ones. Failing open on a permission-change dual-write is a security gap, not just a consistency bug.

## Common Questions

**Isn't a distributed transaction (2PC) the "real" fix?**
> Technically yes, in the sense that it does provide atomicity across both systems — but two-phase commit requires every participant to be a willing, blocking participant in the protocol, which most message brokers, caches, and search indexes simply aren't designed to be, and even where it's technically possible, it trades availability for consistency more aggressively than most systems want. See [Distributed Transactions](distributed-transactions.md) for the 2PC vs. [Saga pattern](../../distributed-systems/patterns/saga-pattern.md) trade-off this same tension shows up in more broadly.

**Does using an outbox table mean the message broker delivery is instant?**
> No — outbox trades instant delivery for reliable eventual delivery. A separate process still has to poll or stream from the outbox table and publish to the broker, which adds some delay compared to publishing directly inline. That delay is the price paid for the publish never being silently lost.

**If I can't add an outbox table, is reconciliation enough on its own?**
> It depends on how long drift can be tolerated and what happens during that window. A reconciliation job run once an hour is fine for an analytics dashboard being briefly stale; it's not fine for a permission revocation where the stale window is itself the security exposure — that case needs the fail-closed behavior above, not just an eventual repair job.

## Related

- [Distributed Transactions](distributed-transactions.md) — the full 2PC vs. Saga vs. outbox-pattern treatment, with the database + message broker case worked out in detail
- [Saga Pattern](../../distributed-systems/patterns/saga-pattern.md) — the broader multi-step-transaction pattern outbox is one building block of
- [Caching Strategies — Cache Invalidation](../../backend/architecture/caching-strategies.md#cache-invalidation) — the database + cache instance of this same problem
- [Azure RAG Platform Map — Flow H](../../../interview/interview-01/22-azure-rag-platform-map.md#h--document-permission-change-flow) — a concrete database/event + search-index dual-write, with the fail-closed behavior this file recommends
- [Kafka](../../distributed-systems/messaging/kafka.md) — the message broker most commonly on the other side of the outbox-pattern fix
- [ACID](../relational/acid.md) — what a single system's own transaction guarantees, and why that guarantee doesn't extend across a second system
