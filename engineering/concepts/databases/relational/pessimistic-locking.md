# Pessimistic Locking

Pessimistic locking is a concurrency-control strategy that assumes conflicts between concurrent writers are **likely**, so it prevents them up front instead of detecting them after the fact. A transaction that wants to modify a row acquires an exclusive lock on it *before* making any change; every other transaction that wants to touch the same row must wait until the lock is released. This is the opposite trade-off from [optimistic locking](optimistic-locking.md), which lets everyone proceed concurrently and only checks for conflicts at write time.

## The Core Mechanism: `SELECT ... FOR UPDATE`

Pessimistic locking at the database level is expressed with `SELECT ... FOR UPDATE` — a `SELECT` that, instead of just reading rows, also acquires a row-level exclusive lock on every row it returns, held until the enclosing transaction commits or rolls back:

```sql
BEGIN;

SELECT * FROM wallets WHERE id = 42 FOR UPDATE;
-- row 42 is now locked — any other transaction's SELECT ... FOR UPDATE,
-- UPDATE, or DELETE on this row blocks here until this transaction ends

UPDATE wallets SET balance = balance - 100 WHERE id = 42;

COMMIT;
-- lock released — the next waiting transaction can now proceed
```

A second, concurrent transaction running the same `SELECT ... FOR UPDATE` against row 42 simply blocks at that line until the first transaction commits or rolls back — there is no conflict to detect or retry, because the second transaction never got to proceed until it was safe to do so.

### `NOWAIT` and `SKIP LOCKED`

Both [PostgreSQL](postgresql.md) and [MySQL](mysql.md) (5.7+) support two variants that avoid blocking indefinitely:

| Variant | Behavior | Typical use |
|---|---|---|
| `FOR UPDATE NOWAIT` | Fails immediately with an error if the row is already locked, instead of waiting | A caller that would rather fail fast and tell the user "try again" than sit blocked |
| `FOR UPDATE SKIP LOCKED` | Silently skips any row that's already locked and returns only the unlocked ones | Multiple worker processes competing to claim jobs from a shared queue table — each worker grabs whatever's free instead of queuing behind a row someone else already claimed |

```sql
-- A worker pool claiming jobs: never wait on a row another worker already has
SELECT * FROM job_queue
WHERE status = 'pending'
ORDER BY created_at
LIMIT 1
FOR UPDATE SKIP LOCKED;
```

### Row-Level vs. Table-Level Locks

`SELECT ... FOR UPDATE` locks only the specific rows the query returns — this is **row-level locking**, and it's what real applications should reach for almost all of the time, since it only blocks transactions that actually touch the same rows. A **table-level lock** (`LOCK TABLE` in [PostgreSQL](postgresql.md), or an unqualified `SELECT ... FOR UPDATE` that scans the whole table without a selective `WHERE`) blocks *every* transaction touching the table regardless of which rows they need — a much blunter tool, reserved for operations like schema migrations or bulk maintenance where genuinely nothing else should run concurrently.

## Tradeoffs

Pessimistic locking trades throughput for certainty:

- **Blocking** — every transaction waiting on a lock is blocked, doing no useful work, for as long as the lock is held. A long-running transaction holding a lock (e.g. one that also makes a slow external API call before committing) stalls every other transaction that needs the same row.
- **Deadlock risk** — if transaction A locks row 1 then waits to lock row 2, while transaction B locks row 2 then waits to lock row 1, neither can ever proceed. The database detects this ([PostgreSQL](postgresql.md) and [MySQL](mysql.md) both run deadlock detection) and kills one of the two transactions with an error, but the application must be written to retry that killed transaction. The standard mitigation is **always acquiring locks in the same, consistent order** across the whole codebase (e.g. always lock the lower ID first) so this cycle can't form.
- **Reduced throughput under low contention** — if two transactions were never actually going to touch the same row, pessimistic locking still pays the cost of acquiring and releasing a lock for every transaction, which [optimistic locking](optimistic-locking.md) avoids entirely by not locking at all.
- **Held across round-trips is dangerous** — if the lock is held while waiting on a user, a network call, or anything outside the database's own control, every other transaction needing that row stalls for that entire external wait. Pessimistic locks should be held for the shortest possible span — ideally just the few statements inside one tight transaction, never across a user's think-time.

## When Pessimistic Locking Is the Right Choice

Pessimistic locking fits best when:

- **Contention is high** — many transactions are genuinely competing for the same rows at the same time, so most [optimistic locking](optimistic-locking.md) attempts would fail and retry anyway; paying the blocking cost up front is cheaper than repeated wasted retries.
- **Conflicts must never reach the application layer** — some operations (e.g. decrementing a limited inventory count, or claiming a single available seat) require certainty that no two transactions can both believe they succeeded, and the cost of a failed optimistic retry loop or a race slipping through is unacceptable.
- **The critical section is short** — a lock held for a handful of statements inside a tight transaction is cheap; a lock held across anything slow or external is not, which is exactly why this strategy is unsuitable for the long-user-think-time scenario [optimistic locking](optimistic-locking.md) handles well.
- **Retry logic in the application is harder to get right than waiting** — some teams prefer the simplicity of "this transaction just waits its turn" over designing a correct retry-with-backoff path for every optimistic conflict.

It fits poorly whenever most concurrent access to a row doesn't actually conflict — in that case the blocking cost is pure overhead with nothing gained, and [optimistic locking](optimistic-locking.md)'s assume-no-conflict approach wins.

## Optimistic vs. Pessimistic: Choosing Between Them

| | [Optimistic Locking](optimistic-locking.md) | Pessimistic Locking |
|---|---|---|
| Assumption | Conflicts are rare | Conflicts are likely |
| Mechanism | Version/timestamp check at write time | Lock acquired before any read/write |
| Blocking | Never — concurrent transactions proceed freely | Yes — competing transactions wait |
| Conflict surfaces as | `409 Conflict` / `412 Precondition Failed`, caller retries | No conflict to retry — the transaction simply waited its turn |
| Deadlock risk | None (no locks held) | Real — requires consistent lock ordering |
| Best fit | Low contention, read-heavy, long gaps between read and write | High contention, short critical sections, conflicts must never slip through |
| Throughput under low contention | High — no locking overhead | Lower — pays lock cost even when nothing would have conflicted |
| Throughput under high contention | Lower — many wasted retries | Higher — no wasted work, just an orderly wait |

A useful rule of thumb: if you'd be surprised when a conflict actually happens, use [optimistic locking](optimistic-locking.md) and handle the rare retry; if you'd be surprised when a conflict *doesn't* happen, use pessimistic locking and accept the blocking cost as the price of certainty.

## Related

- [Optimistic Locking](optimistic-locking.md) — the opposite strategy: detect conflicts after the fact via a version check instead of blocking up front; see the comparison table above for when to choose each.
- [ACID](acid.md) — pessimistic locking is one of the mechanisms a database uses to deliver the isolation [ACID](acid.md) transactions promise.
- [Distributed Locks](../../distributed-systems/patterns/distributed-locks.md) — the same lock-before-touching-shared-state idea, extended across processes/machines using an external store like Redis instead of a single database's row lock.
- [Idempotency & Double-Submit Prevention](../../backend/api/idempotency.md) — a related but distinct concurrency problem (duplicate *requests*, not concurrent *conflicting* writes) that this note's wallet-balance example sits alongside.
- [Distributed Transactions](../../databases/distributed/distributed-transactions.md) — coordinating locks or conflict detection across multiple databases/services is considerably harder than the single-row case this note covers.
- [Idempotency and Race Conditions](../../programming/fundamentals/idempotency-and-race-conditions.md) — the broader principle of concurrent-[mutation](../../programming/fundamentals/mutation.md) safety that both locking strategies are specific instances of.
