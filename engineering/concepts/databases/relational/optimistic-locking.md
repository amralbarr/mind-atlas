# Optimistic Locking

Optimistic locking is a concurrency-control strategy that assumes conflicts between concurrent writers are **rare**, so it never blocks readers or writers up front. Instead, every writer carries a marker of the version of the row it read, and the database (or application) only commits the write if that marker still matches what's currently stored. If another transaction updated the row in the meantime, the write is rejected and the caller must retry — rather than every writer queuing up and waiting for a lock the way [pessimistic locking](pessimistic-locking.md) does.

## The Core Mechanism: Read, Compare, Swap

```text
Transaction A:  reads row (version = 5)
Transaction B:  reads row (version = 5)      ← both read the same version

Transaction A:  UPDATE ... SET version = 6 WHERE id = X AND version = 5
                → 1 row affected, succeeds

Transaction B:  UPDATE ... SET version = 6 WHERE id = X AND version = 5
                → 0 rows affected — version is now 6, not 5
                → B's write is rejected, B must re-read and retry
```

No lock is ever held between the read and the write — the two transactions are free to run concurrently the whole time. The conflict is only detected at the moment of the write itself, via a conditional `UPDATE` that includes the expected version in its `WHERE` clause. This is why optimistic locking is sometimes described as a form of [compare-and-swap](../../programming/fundamentals/asynchronous-non-blocking-execution.md) applied to a database row.

## Typical Implementation: A Version Column

The most common implementation adds an integer (or timestamp) column to the table and bumps it on every successful update:

```sql
ALTER TABLE wallets ADD COLUMN version INT NOT NULL DEFAULT 0;

-- The write itself: version is both a precondition and gets incremented
UPDATE wallets
SET balance = balance - 100, version = version + 1
WHERE id = 42 AND version = 5;
```

If the `UPDATE` affects 0 rows, the application knows the row changed since it was read and must surface a conflict rather than silently proceeding. A timestamp (`updated_at`) can substitute for an integer counter, but an incrementing integer is preferred where possible — timestamps can collide at low clock resolution and are vulnerable to clock skew across nodes.

### ORM Example: JPA `@Version`

In Java's JPA/Hibernate, a field annotated `@Version` turns this pattern into something automatic: the [ORM](../../backend/data/orm.md) reads the current version transparently, includes it in the `WHERE` clause of every `UPDATE` it generates, increments it on success, and throws `OptimisticLockException` the moment an `UPDATE` affects zero rows because another transaction already bumped the version:

```java
@Entity
public class Wallet {
    @Id
    private Long id;
    private BigDecimal balance;

    @Version
    private Long version;   // JPA manages this field automatically
}
```

The application never writes the `WHERE version = ...` clause by hand — JPA generates it from the `@Version` field on every managed-entity update.

### Prisma Example: Manual Version Check

Prisma has no built-in optimistic-locking primitive, so the same pattern is written by hand using `updateMany` (not `update`, since `update` doesn't let you add extra `WHERE` conditions beyond the [primary key](primary-key.md)) and checking the returned count:

```typescript
const result = await prisma.wallet.updateMany({
  where: { id: walletId, version: currentVersion },
  data: { balance: { decrement: amount }, version: { increment: 1 } },
});

if (result.count === 0) {
  throw new ConflictException('Wallet was modified concurrently — please retry');
}
```

This is the exact pattern already used as "Layer 4" in the handbook's [idempotency](../../backend/api/idempotency.md) note for protecting a wallet balance against concurrent updates — [idempotency](../../backend/api/idempotency.md) keys stop duplicate *requests*, while this version check stops a *stale read* from silently overwriting a concurrent change, which is a different failure mode.

### HTTP APIs: ETags and `If-Match`

The same read-compare-swap idea extends naturally to [REST](../../backend/api/rest.md) APIs over [HTTP](../../networking/http.md). The server returns an `ETag` header (a hash or version token of the resource) on `GET`; the client must send that same value back in an `If-Match` header on the next `PUT`/`PATCH`:

```text
GET /documents/42          → 200 OK, ETag: "v5"
client edits locally
PUT /documents/42          If-Match: "v5"
server: current ETag is still "v5" → write succeeds, new ETag: "v6"

-- meanwhile, a second client did the same thing concurrently --
PUT /documents/42          If-Match: "v5"
server: current ETag is now "v6", not "v5" → 412 Precondition Failed
```

A `412 Precondition Failed` response tells the caller exactly what a `count: 0` from an `UPDATE` tells the application layer: the resource changed since it was last read, go re-fetch and retry. This is why optimistic-locking conflicts typically surface to API callers as either a `409 Conflict` (application-level "stale object" error) or a `412 Precondition Failed` ([HTTP](../../networking/http.md)-standard conditional-request failure) — never a silent overwrite.

## When Optimistic Locking Is the Right Choice

Optimistic locking fits best when:

- **Contention is low** — most reads and writes to the same row don't actually overlap in time, so paying a retry cost occasionally is far cheaper than every writer blocking on a lock for every update.
- **Read-heavy workloads** — readers never block, since no lock is ever acquired for a read.
- **Long user-think-time between read and write** — e.g. a user opens a form, edits it over several minutes, then submits; holding a database lock for that entire window ([pessimistic locking](pessimistic-locking.md)) would be disastrous for throughput, but optimistic locking only pays the conflict-detection cost at the final write.
- **Retries are cheap and safe to expose to the caller** — the conflict path (re-fetch, maybe re-apply the user's intent, retry) needs to be something the application or the end user can reasonably handle.

It fits poorly when conflicts are frequent — under high contention, most writes would fail and retry, wasting work and creating a worse user/system experience than simply blocking would have. That scenario is what [pessimistic locking](pessimistic-locking.md) is for instead.

## Related

- [Pessimistic Locking](pessimistic-locking.md) — the opposite strategy: block concurrent access up front instead of detecting conflicts after the fact; this note's closing section compares when to use each.
- [Idempotency & Double-Submit Prevention](../../backend/api/idempotency.md) — uses this exact version-column pattern as its "Layer 4" guard against a stale read clobbering a concurrent wallet update.
- [ACID](acid.md) — optimistic locking is one way applications achieve the isolation an [ACID](acid.md) transaction alone doesn't guarantee across separate read and write round-trips.
- [Distributed Transactions](../../databases/distributed/distributed-transactions.md) — version-based conflict detection is a lighter-weight alternative to coordinating locks across multiple systems.
- [Distributed Locks](../../distributed-systems/patterns/distributed-locks.md) — a different (pessimistic) concurrency mechanism, used when the critical section spans systems a single database transaction can't reach.
- [HTTP](../../networking/http.md) — carries the ETag/If-Match headers that implement this same pattern over a [REST](../../backend/api/rest.md) API.
- [Idempotency and Race Conditions](../../programming/fundamentals/idempotency-and-race-conditions.md) — the broader principle of detecting and handling concurrent [mutation](../../programming/fundamentals/mutation.md) that both locking strategies are specific instances of.
