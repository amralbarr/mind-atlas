# Database Normalization

Normalization is the process of organizing a relational database's tables and columns to reduce data redundancy and prevent update anomalies — structuring data so each fact is stored in exactly one place, rather than copied across many rows that all have to be kept in sync by hand.

## The Problem Normalization Solves

An unnormalized table that mixes unrelated facts into one row:

| order_id | customer_name | customer_email | product | price |
|---|---|---|---|---|
| 1 | Amr | amr@test.com | Laptop | 1200 |
| 2 | Amr | amr@test.com | Mouse | 25 |
| 3 | Ali | ali@test.com | Keyboard | 80 |

This single table has real problems:

- **Update anomaly** — if Amr changes his email, it must be updated in *every* row he appears in; miss one and the data is now inconsistent (two different emails for the same customer).
- **Insertion anomaly** — you can't record a new customer who hasn't placed an order yet, because the customer only exists as a side effect of an order row.
- **Deletion anomaly** — deleting Ali's only order deletes all knowledge that Ali exists as a customer at all.

Normalization fixes this by splitting the data into separate tables, each representing one distinct real-world entity, connected by [foreign keys](foreign-key.md):

```sql
CREATE TABLE customers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255),
    email VARCHAR(255) UNIQUE
);

CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    customer_id INT REFERENCES customers(id),
    product VARCHAR(255),
    price DECIMAL
);
```

Now Amr's email exists in exactly one row, in one table — updating it once updates it everywhere it's referenced (via the `customer_id` [foreign key](foreign-key.md)), and a customer can exist with zero orders.

## The Normal Forms

Normalization is defined as a series of progressively stricter rules ("normal forms"), each building on the one before it.

### First Normal Form (1NF)

Every column holds a single, atomic value — no repeating groups or comma-separated lists crammed into one field.

```text
❌ Violates 1NF:
| order_id | products              |
| 1        | "Laptop, Mouse, Bag"  |

✅ Satisfies 1NF (one row per product):
| order_id | product |
| 1        | Laptop  |
| 1        | Mouse   |
| 1        | Bag     |
```

### Second Normal Form (2NF)

Must already satisfy 1NF, plus: every non-key column depends on the **whole** [primary key](primary-key.md), not just part of it. This only matters for tables with a composite (multi-column) [primary key](primary-key.md).

```text
❌ Violates 2NF — composite key (order_id, product_id),
   but product_name only depends on product_id, not the whole key:
| order_id | product_id | product_name | quantity |

✅ Split out product_name into its own table, keyed by product_id alone:
| order_id | product_id | quantity |     | product_id | product_name |
```

### Third Normal Form (3NF)

Must already satisfy 2NF, plus: no non-key column depends on *another non-key column* (no "transitive dependency").

```text
❌ Violates 3NF — zip_code determines city, so city is
   transitively dependent on zip_code, not directly on customer_id:
| customer_id | zip_code | city   |

✅ Split zip/city into their own lookup table:
| customer_id | zip_code |     | zip_code | city |
```

Most real-world production schemas aim for **3NF** as the practical target — it eliminates the vast majority of redundancy-related anomalies without the diminishing returns of chasing higher normal forms (BCNF, 4NF, 5NF) that mostly matter for edge cases with unusual, multi-valued dependency patterns.

## Why Normalize at All

| Benefit | Explanation |
|---|---|
| **No update anomalies** | Each fact lives in one place; updating it once updates every reference to it |
| **No insertion/deletion anomalies** | Entities can exist independently of each other (a customer without orders, a product without sales) |
| **Smaller storage footprint** | No duplicated data sitting in every row that references it |
| **Clearer data model** | Tables map cleanly to distinct real-world entities, which tends to make the schema easier to reason about and extend |

## The Trade-off: Normalization vs. Denormalization

Normalization isn't free — it comes at the cost of needing more [joins](sql.md) to reassemble related data for reads:

```sql
-- Normalized: needs a join to get customer name with each order
SELECT o.id, c.name, o.product
FROM orders o
JOIN customers c ON o.customer_id = c.id;
```

For read-heavy systems where the same joined shape is queried constantly, **denormalization** — deliberately reintroducing some redundancy (e.g. storing `customer_name` directly on the `orders` row too) — can trade some update complexity for significantly faster reads, since the join no longer needs to happen at query time.

| | Normalized | Denormalized |
|---|---|---|
| Data redundancy | Minimal | Some duplication, by design |
| Write complexity | Simple — one place to update | More complex — same fact may need updating in multiple places |
| Read performance | May require multiple joins | Often faster — data already in the shape reads need |
| Best for | Transactional (OLTP) systems where writes/consistency matter most | Read-heavy reporting/analytics (OLAP), caching layers, systems that can tolerate eventual sync |

Most production systems land somewhere in between: a normalized core schema for correctness, with deliberate, selective denormalization (or a separate read-optimized store/cache) for the specific queries that need it — rather than treating either extreme as a universal rule.

## Normalization and NoSQL

Document databases like [MongoDB](../nosql/mongodb.md) often intentionally embrace denormalization (embedding related data directly inside a document) rather than following relational normalization rules — a design choice driven by a different set of trade-offs (avoiding joins entirely, since document databases generally don't support them well) rather than an oversight. Normalization as a formal discipline is specifically a relational-database concept.

## Common Questions

**Is a fully normalized (5NF/6NF) database always the "correct" design?**
> No — beyond 3NF/BCNF, the returns diminish sharply while query complexity keeps climbing. Most real systems stop at 3NF and denormalize selectively where read performance genuinely demands it, rather than chasing normalization for its own sake.

**Does normalization prevent all data inconsistency?**
> It prevents a specific, well-understood category — redundancy-driven inconsistency (the same fact stored in multiple places getting out of sync). It doesn't prevent other kinds of bugs (application logic errors, missing validation, race conditions) — those need their own separate safeguards.

**Why would anyone deliberately denormalize instead of just adding an index or caching layer?**
> Sometimes denormalization *is* effectively a targeted, persistent cache — storing a precomputed/joined shape directly avoids the join cost on every read, which an index alone can't eliminate (an index speeds up a join, but doesn't remove the need to perform it). The trade-off is accepting extra write-side complexity to keep the duplicated data in sync.

## Related

- [SQL](sql.md)
- [Foreign Key](foreign-key.md)
- [Primary Key](primary-key.md)
- [Surrogate Key](surrogate-key.md)
- [Database Indexing](indexing.md)
- [MongoDB](../nosql/mongodb.md)
