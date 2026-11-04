# Idempotency & Race Conditions

A **race condition** happens when two concurrent operations interleave in a way the code didn't account for, producing a result that depends on timing rather than logic. An operation is **idempotent** if running it multiple times produces the same end state as running it once — a property that makes many race conditions harmless even when the interleaving itself still happens.

## The Classic "Check-Then-Act" Race

A very common source of race conditions is splitting a "does this exist? if not, create it" operation into two separate steps:

```text
1. SELECT ... WHERE key = X       (check)
2. if not found: INSERT ...       (act)
```

Between step 1 and step 2, another concurrent request can run the same two steps — both see "not found" in step 1, and both proceed to insert, resulting in a duplicate (or a unique-constraint error, or two divergent records, depending on the schema). This is a **check-then-act** race, and it's dangerous specifically because it can look correct in every manual test — the window between the two steps is often microseconds, so it only shows up under real concurrent load.

## The Fix: Make It One Atomic Operation

The fix isn't to add a lock around the two steps (though that's one valid option) — it's usually to replace the two steps with a single database operation that's atomic by construction:

- An **upsert** (`INSERT ... ON CONFLICT DO NOTHING/UPDATE`) — the database itself guarantees only one row exists for a given unique key, no matter how many concurrent callers race to insert it.
- A **unique constraint** as a backstop even when application code tries to be careful — the database enforces the invariant even if some code path somewhere doesn't use the atomic pattern correctly.

The general principle: whenever "check if X, then do Y based on that check" spans two round-trips to shared state, ask whether the datastore offers a single atomic primitive that collapses both steps into one — that's almost always safer than trying to reason about locking by hand.

## Idempotency as a Complementary Safety Net

Even with an atomic check-and-create, network retries are a related but distinct problem: a client that times out waiting for a response has no way to know if the request actually succeeded server-side — retrying it should be *safe*, not create a duplicate. An [idempotency](../../backend/api/idempotency.md) key (a client-generated unique id sent with the request, stored server-side against the result of the first successful attempt) lets a retried request with the same key return the original result instead of re-executing the operation — this is a different mechanism from the atomic-upsert fix above, solving a different problem (safe client retries vs. safe concurrent creation), and systems that need both implement both.

## Real-World Example

A real third-party embeddable-widget design calls out exactly the check-then-act race for a "look up or auto-create an account for this external identity, the first time we see it" flow: two concurrent first-page-loads for the same new external user must not be allowed to race into two separate accounts being created. The fix specified is precisely an atomic upsert — `findUnique` plus `create` inside a single query, or a real `ON CONFLICT DO NOTHING RETURNING` — not a `findFirst` followed by a separate `create` call, plus a database-level check constraint as a backstop invariant.

## Common Questions

**If a race condition is rare (a small timing window), is it safe to ignore in a low-traffic system?**
> Rarity doesn't mean safety — a rare-but-real race in a system that runs millions of requests over its lifetime will eventually be hit, often at the worst possible time (a traffic spike, a retry storm during an incident, exactly when correctness matters most). Fixing it structurally (atomic operation) is cheap relative to debugging the resulting data corruption in production later.

**Is a mutex/lock always the wrong answer compared to an atomic database operation?**
> Not always — a lock is appropriate when the operation genuinely can't be expressed as a single atomic datastore primitive (e.g. coordinating across multiple different systems). But when the operation *can* be expressed atomically in the database itself, that's usually simpler and more robust than application-level locking, which has its own failure modes (a lock that isn't released on crash, lock contention under load).

## Related

- [Idempotency & Double-Submit Prevention](../../backend/api/idempotency.md) — applied patterns: [idempotency](../../backend/api/idempotency.md) keys, UI button guards, DB unique constraints, and [optimistic locking](../../databases/relational/optimistic-locking.md) for financial APIs
- [Single-Threading & the Event Loop](../../distributed-systems/patterns/single-threading.md)
- [ACID](../../databases/relational/acid.md)
- [Multi-Tenancy & Tenant Isolation](../../backend/architecture/multi-tenancy.md)
- [Distributed Locks](../../distributed-systems/patterns/distributed-locks.md)
- [Pessimistic Locking](../../databases/relational/pessimistic-locking.md) — the alternative to the atomic-operation fix above when the critical section genuinely can't be collapsed into one atomic write: block competing transactions instead of outrunning them
