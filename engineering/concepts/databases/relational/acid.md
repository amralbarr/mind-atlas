# ACID

**ACID** is a set of properties that guarantee reliable and consistent database transactions. It is fundamental to relational database systems.

## ACID Properties

### Atomicity (All or Nothing)

A transaction either:

- Fully completes, or
- Fully fails and is rolled back

There is no partial execution.

Example — transferring money:

- Deduct from account A (succeeds)
- Add to account B (fails)
- The system rolls back, and account A is restored

### Consistency (Valid State)

After a transaction, the database must remain valid according to its rules:

- Constraints
- Triggers
- Relationships

Example:

- A balance cannot go negative, if that constraint is defined
- Foreign keys must remain valid

### Isolation (No Interference)

Transactions don't interfere with each other, even when running at the same time.

Example: two users updating the same record won't corrupt the data.

Isolation levels, from weakest to strongest:

- Read Uncommitted
- Read Committed
- Repeatable Read
- Serializable (strongest)

### Durability (Permanent)

Once a transaction is committed, it is permanently saved — even if the system crashes or loses power immediately afterward.

## Example: Bank Transfer

```sql
BEGIN;
UPDATE accounts SET balance = balance - 100 WHERE id = 1;
UPDATE accounts SET balance = balance + 100 WHERE id = 2;
COMMIT;
```

ACID ensures:

- No partial update (Atomicity)
- Rules are preserved (Consistency)
- No conflict with other transactions (Isolation)
- Data survives crashes (Durability)

## Why ACID Matters

Without ACID guarantees, systems risk:

- Data corruption
- Lost updates
- Inconsistent states

## ACID vs Distributed Systems

ACID works well in a single database (like a single [PostgreSQL](postgresql.md) instance). In distributed systems spanning multiple databases or services, maintaining strict ACID guarantees globally is difficult, which leads to patterns like:

- The [Saga pattern](../../distributed-systems/patterns/saga-pattern.md)
- [Eventual consistency](../../distributed-systems/patterns/eventual-consistency.md)

See [Distributed Transactions](../distributed/distributed-transactions.md) for how these patterns replace strict ACID guarantees across services.

## Quick Summary

| Property    | Meaning           |
| ----------- | ------------------ |
| Atomicity   | All or nothing      |
| Consistency | Valid state          |
| Isolation   | No interference        |
| Durability  | Permanent save          |

## Related

- [SQL](sql.md)
- [Distributed Transactions](../distributed/distributed-transactions.md)
- [Database Indexing](indexing.md)
- [Foreign Key](foreign-key.md)
- [Optimistic Locking](optimistic-locking.md) — one concrete mechanism applications use to achieve the Isolation property across separate read/write round-trips, where the database's own transaction isolation alone isn't enough
- [Pessimistic Locking](pessimistic-locking.md) — the other concrete mechanism (`SELECT ... FOR UPDATE`) for the same Isolation guarantee, blocking competing transactions instead of detecting conflicts after the fact
