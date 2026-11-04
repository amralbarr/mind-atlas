# Database Indexing

**Database indexing** is a technique used to speed up data retrieval by creating a separate structure that lets the database find rows quickly, without scanning the entire table.

## Simple Idea

Without an index:

```text
Scan every row → slow
```

With an index:

```text
Use a shortcut → fast
```

Think of it like the index in a book — instead of reading every page, you jump directly to what you need.

## How It Works

An index stores column values along with pointers to the actual rows. Most databases (like [PostgreSQL](postgresql.md)) use structures such as:

- **B-trees** (most common)
- Hash indexes
- GIN / GiST (advanced cases, e.g. full-text or array search)

## Example

Table:

```sql
users(id, name, email)
```

Query:

```sql
SELECT * FROM users WHERE email = 'test@mail.com';
```

Without an index, the database performs a full table scan of every row. With an index:

```sql
CREATE INDEX idx_email ON users(email);
```

the database jumps directly to matching rows.

## Performance Impact

| Case         | Speed        |
| ------------ | ------------ |
| No index     | Slow (O(n))     |
| With index   | Fast (O(log n))  |

## Types of Indexes

### Single Column

```sql
CREATE INDEX idx_name ON users(name);
```

### Composite Index

```sql
CREATE INDEX idx_user ON users(name, email);
```

Column order matters: `(name, email)` is not the same index as `(email, name)`.

### Unique Index

```sql
CREATE UNIQUE INDEX idx_email ON users(email);
```

Prevents duplicate values in the indexed column.

### Full-Text Index

Used for text search across documents and free-form content.

## Trade-offs

**Pros:**

- Faster `SELECT` queries
- Better performance on large tables

**Cons:**

- Slower `INSERT`/`UPDATE` (every index must be updated too)
- More storage usage
- Too many indexes can hurt overall performance

## When to Use Indexing

Create indexes on columns used in:

- `WHERE` clauses
- `JOIN` conditions
- `ORDER BY` clauses
- Frequently queried fields (e.g. `user_id`, `project_id`, `created_at`, `status` for job/queue tables)

This matters especially for queue-polling systems and pipeline/job tables that are queried repeatedly by status or timestamp.

## When Not to Index

Avoid indexing:

- Small tables (a full scan is already cheap)
- Columns with low cardinality/uniqueness (e.g. a boolean or gender column)
- Every column "just in case" — too many indexes slow down writes

## One-line Definition

> Database indexing = creating a fast lookup structure to avoid scanning entire tables.

## Index Fragmentation

Index fragmentation means index pages become disorganized and inefficient over time. It causes slower queries, slower inserts, more disk reads, and worse cache performance — an important database performance topic, especially as tables grow to millions or billions of rows.

### How B-Trees Store Data

Most [SQL](sql.md) databases use B-tree indexes, which store ordered keys efficiently organized across pages, for example:

```text
Page1: 1 2 3
Page2: 4 5 6
Page3: 7 8 9
```

### Sequential Inserts vs. Random Inserts

**Sequential inserts (good)** — values like `1, 2, 3, 4, 5` are appended at the end of the index, and the database writes efficiently.

**Random inserts (bad)** — random values, such as [UUID](uuid.md) v4 keys, insert scattered throughout the index rather than at the end:

```text
F8...
A1...
C7...
B2...
```

This forces the database to split and reorganize pages, scattering data instead of keeping it sequential:

```text
Page1: 1 8 20
Page2: 2 15 30
Page3: 3 9 25
```

That scattering is index fragmentation.

### Why Fragmentation Is Bad

1. **More disk reads** — the database must jump around storage instead of reading contiguous pages.
2. **Worse cache locality** — the database/CPU cache becomes less effective.
3. **Slower range queries** — sequential scanning becomes expensive.
4. **More page splits** — the database continuously reorganizes index pages.

### Page Splits

Suppose a page is full:

```text
1 2 3 4
```

and a new value, `2.5`, needs to be inserted. The database splits the page:

```text
Page A: 1 2
Page B: 2.5 3 4
```

This costs CPU and [I/O](../../programming/fundamentals/io.md), and fragments storage further.

### Why UUID v4 Causes Fragmentation

[UUID](uuid.md) v4 values are random, so each insert lands at a random location in the index — unlike sequential integers (`1, 2, 3, 4, 5`), which append cleanly at the end. Databases favor append-only insert patterns because they cause fewer page splits, keep storage contiguous, and cache better.

### UUID v7 / ULID Solve This

Modern identifiers like [UUID](uuid.md) v7 and [ULID](ulid.md) are time-ordered, so inserts mostly happen near the end of the index, producing much less fragmentation than random [UUID](uuid.md) v4 — while still supporting distributed, collision-resistant generation. See [UUID](uuid.md) and [ULID](ulid.md).

### Types of Fragmentation

**Logical fragmentation** — the index's logical key order no longer matches its physical storage order.

**Internal fragmentation** — pages contain unused free space. For example, a page with a capacity of 100 rows may hold only 50 after splits, wasting space.

This affects all major relational databases: [PostgreSQL](postgresql.md), [MySQL](mysql.md), and Microsoft [SQL](sql.md) Server.

### Reducing Fragmentation

**Reindexing** — rebuild the index from scratch. In [PostgreSQL](postgresql.md):

```sql
REINDEX TABLE users;
```

**VACUUM ([PostgreSQL](postgresql.md))** — cleans up dead tuples and pages.

**Fill factor** — intentionally leave empty space in each page (e.g. 70% full) so future inserts don't immediately trigger a split.

**Use sequential-friendly IDs** — prefer auto-increment integers, [UUID](uuid.md) v7, or [ULID](ulid.md) over random [UUID](uuid.md) v4.

### ID Strategy Trade-offs

| ID Type              | Pros                              | Cons                              |
| --------------------- | ---------------------------------- | ----------------------------------- |
| Integer / auto-increment | Best index performance               | Hard to generate in distributed systems; predictable |
| [UUID](uuid.md) v4                    | Great uniqueness/distribution              | Causes fragmentation; slower indexes    |
| [ULID](ulid.md) / [UUID](uuid.md) v7                | Distributed, sortable, less fragmentation    | Newer/less universally supported          |

See [Surrogate Key](surrogate-key.md), [Natural Key](natural-key.md), [UUID](uuid.md), and [ULID](ulid.md) for more on choosing an ID strategy.

### Common Questions

**Q1. What is index fragmentation?**

> Index fragmentation occurs when index pages become disorganized due to random insertions, updates, and page splits, reducing query and insertion efficiency.

**Q2. Why does [UUID](uuid.md) v4 cause fragmentation?**

Because random values insert into random index positions, causing page splits and scattered storage.

**Q3. Why are sequential IDs faster?**

Because inserts append near the end of B-tree indexes with minimal page splits.

**Q4. How do you reduce fragmentation?**

Rebuild indexes, use ordered IDs, tune fill factor, and vacuum/reorganize regularly.

**Q5. Why are [ULID](ulid.md)/UUID v7 important?**

They preserve ordering while still supporting distributed, unique ID generation.

**Senior-level answer:**

> Index fragmentation is the degradation of B-tree storage locality caused by non-sequential modifications, leading to increased page splits, reduced cache efficiency, and degraded query performance. It is particularly relevant in systems using random UUID-based primary keys.

**Easy way to remember:**

```text
Sequential inserts = healthy index
Random inserts = fragmented index
```

## Related

- [SQL](sql.md)
- [ACID](acid.md)
- [Foreign Key](foreign-key.md)
- [Surrogate Key](surrogate-key.md)
- [The N+1 Query Problem](../../backend/data/n-plus-1-problem.md)
- [ORM](../../backend/data/orm.md)
- [Big O Notation / Algorithmic Complexity](../../programming/fundamentals/big-o-notation.md)
- [Pagination](../../backend/api/pagination.md)
- [Database Normalization](database-normalization.md)
