# Idempotency & Double-Submit Prevention

An operation is **idempotent** if performing it multiple times produces the same result as performing it once. Critical for financial operations, payment processing, and any state-changing API where a retry or accidental double-click must not cause a duplicate effect.

## The Problem

```
User clicks "Send 100 SAR"
    ↓ request sent
Network hiccup — user doesn't see a response
    ↓ user clicks again (or browser auto-retries)
Two debit transactions created — 200 SAR deducted
```

This happens because:
- The user double-clicks before the UI disables the button
- The network drops the response but the server already processed the request
- The client retries a timed-out request that actually succeeded
- Two browser tabs submit the same form

---

## Layer 1: UI Prevention (First Line of Defense)

Disable the submit button immediately on first click and show a loading state:

```typescript
// React
const [isSubmitting, setIsSubmitting] = useState(false);

async function handleSend() {
  if (isSubmitting) return;          // guard against race
  setIsSubmitting(true);
  try {
    await sendMoney({ amount, to });
  } finally {
    setIsSubmitting(false);          // re-enable only after response
  }
}

<button onClick={handleSend} disabled={isSubmitting}>
  {isSubmitting ? 'Processing...' : 'Send 100 SAR'}
</button>
```

**Why this is not enough alone:** the user might open two tabs, the network might retry, or the response might be lost after the server committed the transaction.

---

## Layer 2: Idempotency Key (The Real Fix)

The client generates a unique key per *intent* (not per request), and includes it in every attempt. The server uses this key to deduplicate:

```
First attempt:   POST /wallet/transfer  Idempotency-Key: key_abc123
Server:          processes, stores result against key_abc123, returns 200

Second attempt:  POST /wallet/transfer  Idempotency-Key: key_abc123
Server:          finds key_abc123 already processed, returns cached 200
                 NO second transaction created
```

**Client — generate the key once per user action:**

```typescript
import { v4 as uuidv4 } from 'uuid';

// Generate once when the user initiates the action, not on every retry
const idempotencyKey = uuidv4();   // store in state, reuse on retry

async function sendMoney(amount: number, to: string) {
  return fetch('/wallet/transfer', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Idempotency-Key': idempotencyKey,   // same key on every retry
    },
    body: JSON.stringify({ amount, to }),
  });
}
```

**Server — store and deduplicate (NestJS / Prisma example):**

```typescript
// Middleware or interceptor that runs before the handler
async function idempotencyCheck(req, res, next) {
  const key = req.headers['idempotency-key'];
  if (!key) return next();

  // Check if this key was already processed
  const cached = await db.idempotencyRecord.findUnique({ where: { key } });
  if (cached) {
    // Return the original response — do not re-execute
    return res.status(cached.statusCode).json(JSON.parse(cached.responseBody));
  }

  // Capture the response after handler runs
  const originalJson = res.json.bind(res);
  res.json = async (body) => {
    await db.idempotencyRecord.create({
      data: {
        key,
        statusCode: res.statusCode,
        responseBody: JSON.stringify(body),
        expiresAt: new Date(Date.now() + 24 * 60 * 60 * 1000),  // 24h TTL
      },
    });
    return originalJson(body);
  };

  next();
}
```

**DB schema:**
```prisma
model IdempotencyRecord {
  id           String   @id @default(cuid())
  key          String   @unique
  statusCode   Int
  responseBody String
  createdAt    DateTime @default(now())
  expiresAt    DateTime

  @@index([expiresAt])   // for cleanup job
}
```

---

## Layer 3: Database Unique Constraint (Hard Guard)

Even with an idempotency key, a race condition between two simultaneous requests (same key, same millisecond) can slip through if both read "not found" before either writes. Add a DB-level constraint as the ultimate guard:

```sql
-- For a transfer table
ALTER TABLE transfers ADD CONSTRAINT uq_idempotency_key UNIQUE (idempotency_key);
```

```prisma
model Transfer {
  id              String  @id @default(cuid())
  idempotencyKey  String  @unique    // DB enforces — second insert throws
  amount          Decimal
  fromUserId      String
  toUserId        String
  status          TransferStatus
  createdAt       DateTime @default(now())
}
```

If two requests race through simultaneously, the second `INSERT` throws a unique constraint violation — catch it and return the result of the first:

```typescript
try {
  const transfer = await db.transfer.create({ data: { idempotencyKey, ...payload } });
  return transfer;
} catch (e) {
  if (e.code === 'P2002') {  // Prisma unique constraint error
    // Race — return the existing record
    return db.transfer.findUnique({ where: { idempotencyKey } });
  }
  throw e;
}
```

---

## Layer 4: Optimistic Locking / Version Check

For update operations (not inserts), use a version counter to prevent stale writes:

```prisma
model Wallet {
  id      String  @id
  balance Decimal
  version Int     @default(0)
}
```

```typescript
// Include the current version in the WHERE clause
const updated = await db.wallet.updateMany({
  where: { id: walletId, version: currentVersion },  // only succeeds if version matches
  data: { balance: { decrement: amount }, version: { increment: 1 } },
});

if (updated.count === 0) {
  throw new ConflictException('Wallet was modified concurrently — please retry');
}
```

If two concurrent requests both read `version: 5`, only one can update to `version: 6` — the other gets `count: 0` and must retry.

---

## Summary: Which Layer Handles What

| Threat | Layer | Mechanism |
|---|---|---|
| User double-click | UI | Disable button on first click |
| Two tabs submitting | UI + Backend | Idempotency key (same key = same response) |
| Network retry after timeout | Backend | Idempotency key |
| Race condition (simultaneous requests) | Database | Unique constraint on idempotency key |
| Stale read / concurrent update | Database | [Optimistic locking](../../databases/relational/optimistic-locking.md) (version column) |

**For a wallet specifically:** use all four layers. A missed debit or duplicate credit is a financial incident, not just a UX bug.

---

## Related

- [Idempotency and Race Conditions](../../programming/fundamentals/idempotency-and-race-conditions.md) — the broader check-then-act/race-condition principle this note's layered defenses are a concrete application of
- [ACID](../../databases/relational/acid.md) — the isolation guarantees these layers compensate for across separate request/response round-trips
- [Distributed Transactions](../../databases/distributed/distributed-transactions.md) — coordinating this same kind of safe-retry/dedup problem across multiple systems rather than one database
- [Rate Limiting](../architecture/rate-limiting.md)
- [Exponential Backoff and Jitter](../resilience/exponential-backoff-and-jitter.md) — why a retried side-effecting call needs the same idempotency key on every attempt
- [Optimistic Locking](../../databases/relational/optimistic-locking.md) — the full mechanism behind this note's Layer 4 version-column guard, including [ORM](../data/orm.md) (JPA `@Version`) and [HTTP](../../networking/http.md) (ETag/If-Match) equivalents
- [Pessimistic Locking](../../databases/relational/pessimistic-locking.md) — the alternative, block-up-front strategy for the same stale-write problem Layer 4 solves optimistically; worth reaching for instead when contention on the same row is high
