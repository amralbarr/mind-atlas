# ULID

ULID stands for **Universally Unique Lexicographically Sortable Identifier** — a modern alternative to [UUID](uuid.md).

Example:

```text
01HZX3K8M7YQ7W2J9N5P4A6BCD
```

## Main Idea

ULID provides:

- global uniqueness
- distributed generation
- sortability by time
- better database performance than random UUIDs

## Why ULID Was Created

Random [UUID](uuid.md) v4 values are completely random, which causes index fragmentation, slower inserts, and poor ordering. ULIDs solve this by being time-ordered while still unique.

## UUID vs ULID

| Feature                     | [UUID](uuid.md) v4 | ULID   |
| ------------------------------ | ------- | ------ |
| Unique                              | Yes       | Yes      |
| Distributed generation                  | Yes       | Yes      |
| Sortable                                    | No        | Yes      |
| Human readability                               | Poor      | Better   |
| [Database indexing](indexing.md)                                   | Worse     | Better   |

### Why Sortability Matters

Databases perform best with sequential inserts.

Integer IDs (`1, 2, 3, 4`) insert sequentially with efficient indexes. Random UUIDs (`F9...`, `A1...`, `C7...`) insert randomly, causing B-tree fragmentation. See [Indexing](indexing.md). ULIDs (`01HZX...`, `01HZY...`, `01HZZ...`) are naturally ordered by creation time, giving better insertion patterns.

## ULID Structure

| Part         | Purpose      |
| -------------- | ------------ |
| Timestamp          | ordering       |
| Randomness             | uniqueness       |

Simplified: `[TIME][RANDOM]`

- **Timestamp part** — encodes creation time, enabling sorting.
- **Random part** — ensures uniqueness even with the same timestamp across multiple servers.

### Lexicographically Sortable Means

Alphabetical sorting equals chronological order. Example: `01AAA`, `01AAB`, `01AAC` — sorting these strings gives the correct time order, which is very useful.

## Why ULID Is Good for Databases

Inserts become mostly sequential, which brings better indexing, fewer page splits, faster inserts, and improved cache locality.

## ULID in Distributed Systems

Excellent for microservices, event systems, [distributed databases](../distributed/distributed-databases.md), and realtime systems.

## ULID vs UUID v7

Both share the same goal — combining a timestamp with randomness for sortable uniqueness. See [UUID](uuid.md) for details on [UUID](uuid.md) v7.

| ULID                | [UUID](uuid.md) v7                    |
| ---------------------- | ---------------------------- |
| Custom format               | Official UUID standard             |
| Base32, readable                | Standard UUID format                    |
| Sortable                              | Sortable                                      |

### Why Some Teams Prefer ULID

Shorter, readable, URL-friendly, and naturally sortable — e.g. `/orders/01HZX3K8M7...` looks cleaner than a UUID in some contexts.

## ULID in JavaScript/TypeScript

Popular library: [ulid npm package](https://www.npmjs.com/package/ulid)

```typescript
import { ulid } from 'ulid';

const id = ulid();
```

## ULID in Databases

Usually stored as `VARCHAR`/`TEXT`, or in binary-optimized formats.

## ULID Downsides

1. **Larger than integer IDs** — still bigger than `INT`/`BIGINT`.
2. **Not an official UUID standard** — some systems/tools expect the standard UUID format.
3. **Slightly more complex** than auto-increment integers.

## When to Use ULID

Good fit: distributed systems, event sourcing, high insert workloads, public APIs, ordered event streams.

Integer IDs may still be better for: small/simple systems, single-database apps, and maximum performance simplicity.

## Common Questions

**What is ULID?**
> ULID is a globally unique sortable identifier designed as an alternative to UUID with improved ordering and indexing behavior.

**Why is ULID better than UUID v4 for databases?**
Because ULIDs are time-ordered, reducing index fragmentation and improving insertion locality.

**What does lexicographically sortable mean?**
Alphabetical string order matches creation time order.

**ULID vs UUID?**

| ULID               | UUID                  |
| --------------------- | ----------------------- |
| Sortable                   | Usually random               |
| Better inserts                  | More fragmentation                  |

**Why are sortable IDs important?**
They improve indexing, [pagination](../../backend/api/pagination.md), and database insertion performance.

## Senior-Level Answer

> ULID is a distributed unique identifier format combining timestamp ordering with randomness, enabling globally unique IDs that preserve insertion locality and improve indexing efficiency compared to random UUIDs.

## Easy Way to Remember

```text
UUID = unique but random
ULID = unique + time sortable
```

## Related

- [UUID](uuid.md)
- [Surrogate Key](surrogate-key.md)
- [Primary Key](primary-key.md)
- [Indexing](indexing.md)
