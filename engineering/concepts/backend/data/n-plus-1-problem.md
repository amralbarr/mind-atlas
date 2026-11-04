# The N+1 Query Problem

The N+1 problem is one of the **most common performance bugs** in backend engineering:

> The application executes **one query** to fetch the parent records, then **N additional queries** — one per record — to fetch their related data, instead of a single optimized query.

## An Analogy

You need 10 items from the grocery store:
- **N+1:** you drive to the store and buy one item, drive home, then drive back for the next item... **10 round trips**.
- **The fix:** you write a list of all 10 and buy them all in **one trip**.

The time lost isn't in the **buying** itself — it's in the **driving back and forth**. That's exactly what happens with a database.

## A Concrete Example

**Users table**

| id | name |
|----|------|
| 1  | Amr  |
| 2  | Ali  |

**Orders table**

| id | user_id |
|----|---------|
| 10 | 1       |
| 11 | 1       |
| 12 | 2       |

**The goal:** fetch all users along with their orders.

### ❌ The Naive Approach (N+1)

```sql
SELECT * FROM users;                          -- query 1: fetch the users

SELECT * FROM orders WHERE user_id = 1;       -- one query per user
SELECT * FROM orders WHERE user_id = 2;
```

| Number of users | Number of queries |
|---|---|
| 2 | 3 |
| 100 | 101 |
| 1,000 | **1,001** |

**Why is it called N+1?** One query for the parent records, **plus N** queries for the related records.

### ✅ The Fix: A Single Query

```sql
SELECT *
FROM users
LEFT JOIN orders ON users.id = orders.user_id;
```

## Why Is It Bad — In Numbers

Assume each database round trip takes **2 milliseconds** (network + query parsing + execution):

| | Round trips | Approximate time |
|---|---|---|
| N+1 with 1,000 users | 1,001 | **≈ 2 seconds** |
| One optimized query | 1 | **≈ 20 milliseconds** |

(Illustrative numbers, but a gap of this magnitude is realistic.)

**The real damage:**
- **Many database round trips** — every query carries network, parsing, and execution overhead.
- **High latency** — a thousand small queries are far slower in aggregate than one large one.
- **Database overload** — under real traffic (hundreds of concurrent users), the database itself can **collapse**.

**The most dangerous part:** this bug **doesn't show up in development**. With 5 test users, 6 queries go unnoticed. Then in production with 10,000 users, the page falls over.

## Why Does an ORM Hide This Problem?

An **[ORM](orm.md)** (like SQLAlchemy, [Django](../../programming/python/django.md) [ORM](orm.md), or Prisma) lets you work with the database **as objects**, so you never see the raw [SQL](../../databases/relational/sql.md). The code **looks completely innocent**:

### Python: SQLAlchemy

```python
# ❌ N+1: looks like perfectly ordinary code
users = session.scalars(select(User)).all()          # query 1

for user in users:
    print(user.name, len(user.orders))               # every user.orders = a hidden query!
```

The line `user.orders` **looks** like reading an ordinary attribute, but it actually **fires a database query** on every iteration. This is **lazy loading**.

```python
# ✅ Fix 1: selectinload — exactly two queries, no matter how many users
from sqlalchemy.orm import selectinload

users = session.scalars(
    select(User).options(selectinload(User.orders))
).all()
# query 1: SELECT * FROM users
# query 2: SELECT * FROM orders WHERE user_id IN (1, 2, ...)

# ✅ Fix 2: joinedload — a single query via JOIN
from sqlalchemy.orm import joinedload

users = session.scalars(
    select(User).options(joinedload(User.orders))
).unique().all()
```

### Python: Django

```python
# ❌ N+1
for user in User.objects.all():
    print(user.orders.count())

# ✅ The fix
for user in User.objects.prefetch_related("orders"):
    print(len(user.orders.all()))     # from memory, no new query
```

| Django tool | When to use it |
|---|---|
| `select_related` | A **to-one** relationship (e.g. `order.user`): uses a JOIN |
| `prefetch_related` | A **to-many** relationship (e.g. `user.orders`): uses a second query with `IN` |

### TypeScript: Prisma and TypeORM

```typescript
// ❌ N+1
const users = await prisma.user.findMany();
for (const user of users) {
  const orders = await prisma.order.findMany({ where: { userId: user.id } });
}

// ✅ Prisma
const users = await prisma.user.findMany({ include: { orders: true } });

// ✅ TypeORM
const users = await userRepo.find({ relations: ['orders'] });
```

## Lazy Loading vs. Eager Loading

| | **Lazy loading** | **Eager loading** |
|---|---|---|
| **When is related data fetched?** | Only when it's actually accessed | Upfront, alongside the parent records |
| **Advantage** | Never fetches data you don't need | A fixed, small number of queries |
| **Risk** | **N+1** if triggered inside a loop | May fetch data you don't actually need |
| **Good fit when** | You only need the relation for one or two records | You already know you'll need it for every record |

## The Three Fixes, and When to Choose Each

### 1. JOIN (one query)

```sql
SELECT * FROM users LEFT JOIN orders ON users.id = orders.user_id;
```

⚠️ **Watch out:** the result **duplicates** the user's data across every one of their orders:

| user.id | user.name | order.id |
|---|---|---|
| 1 | Amr | 10 |
| 1 | Amr | 11 | ← duplicated
| 2 | Ali | 12 |

With multiple nested relationships (user → orders → line items), this duplication **multiplies** and can become enormous.

### 2. Batching with `IN` (two queries)

```sql
SELECT * FROM users;
SELECT * FROM orders WHERE user_id IN (1, 2, 3, ...);
```

**No duplication**, and the query count stays fixed at **2** regardless of how many users there are. This is exactly what `selectinload` and `prefetch_related` do under the hood. **Usually the best choice for to-many relationships.**

### 3. DataLoader (in GraphQL)

```graphql
users {
  orders {
    items
  }
}
```

In [GraphQL](../api/graphql.md), every nested field has its **own resolver**, unaware of the others. The orders resolver gets called **once per user**, producing N+1 — then the items resolver gets called **once per order**, compounding the problem further.

**DataLoader** collects every request made during the same tick and sends them as **one batch**:

```
Without DataLoader:  orders(user=1), orders(user=2), orders(user=3), ...  ← N queries
With DataLoader:     orders(user IN [1, 2, 3, ...])                       ← one query
```

## The Same Pattern Outside Databases

N+1 isn't a SQL-only problem — it's **any network round trip inside a loop**:

```python
# ❌ N+1 with an embeddings API: 5,000 network calls
for chunk in chunks:
    chunk.vector = embedding_client.embed(chunk.text)

# ✅ Batched: only 50 calls (100 chunks per batch)
for batch in batched(chunks, 100):
    vectors = embedding_client.embed([c.text for c in batch])
```

The exact same shape shows up with: calling a microservice once per item, reading a file from [ADLS](../../cloud/azure/adls.md) once per record, or publishing to [Kafka](../../distributed-systems/messaging/kafka.md) with a `flush()` after every single message.

**The rule:** if you see a **network call inside a loop**, ask yourself: can this be batched?

## How Do You Detect It?

| Tool | How |
|---|---|
| **SQLAlchemy** | `create_engine(url, echo=True)` prints every query — if you see the same query repeating with different values, that's N+1 |
| **Django** | The Django Debug Toolbar shows the query count per page |
| **Slow query logs** | Database logs for slow or repeated queries |
| **APM** (Datadog, New Relic, [Azure](../../cloud/azure/azure.md) Application Insights) | Shows the query count per [HTTP](../../networking/http.md) request |
| **In tests** | Write a test asserting the **query count stays fixed** no matter how many records exist |

**That last test is the strongest defense**, because it catches the bug before production:

```python
# Django
def test_users_page_query_count(self):
    create_users(50)
    with self.assertNumQueries(2):      # must stay 2 whether there are 5 users or 50
        self.client.get("/users/")
```

## Common Interview Questions

| Question | Short answer |
|---|---|
| **What is the N+1 problem?** | One query for the parent records, then a separate query per record to fetch its related data |
| **Why is it dangerous?** | Query count grows **linearly** with data size, so performance collapses as the system grows |
| **How do you fix it?** | Eager loading, JOIN, batching with `IN`, DataLoader, and tuning the [ORM](orm.md)'s relation configuration |
| **Why are ORMs prone to it?** | Lazy loading and [abstraction](database-abstraction.md) hide the actual queries from the developer |
| **Why is it especially common in [GraphQL](../api/graphql.md)?** | Every nested resolver fetches its own data independently, with no awareness of sibling requests |

### Advanced Interview Answer

> "The N+1 problem is an anti-pattern where query count explodes because traversing object relationships triggers excessive database round trips. It shows up most often with ORMs, due to lazy loading, and in GraphQL resolvers. I address it with eager loading, batching via `IN`, or DataLoader, and guard against regressions with a test that pins the query count — because this bug doesn't show up in development with small datasets, only at production scale."

## Summary

```
1 optimized query     ← ✅ good
1,001 tiny queries    ← ❌ bad
```

**General rule:** any database or network call **inside a loop** is a suspect until proven otherwise.

## Related

- [ORM](orm.md) — the most common source of accidental N+1 queries, via lazy loading
- [Database Abstraction](database-abstraction.md) — the [abstraction](../../programming/fundamentals/abstraction.md) layer that hides the generated queries in the first place
- [GraphQL](../api/graphql.md) — resolver-per-field makes N+1 especially easy to trigger
- [Connection Pooling](../../databases/relational/connection-pooling.md) — reduces the *connection* cost per query, but does nothing for the *query count* itself
- [Embeddings](../../ai/ingestion/embeddings.md) — a real example of the same batching problem outside SQL entirely
- [Kafka](../../distributed-systems/messaging/kafka.md) — another non-SQL instance: flushing once per message instead of batching
- [System Design](../architecture/system-design.md)
- [Distributed Databases](../../databases/distributed/distributed-databases.md)
