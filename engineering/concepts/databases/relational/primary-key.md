# Primary Key

A primary key is:

> A column (or combination of columns) that uniquely identifies each row in a table.

It is one of the most fundamental concepts in relational database design.

## Example

### Users Table

| id | name | email |
|----|------|-------|
| 1  | Amr  | amr@test.com |
| 2  | Ali  | ali@test.com |

Here, `id` is the primary key because:

- each value is unique
- it identifies exactly one row

## Primary Key Rules

A primary key must be:

| Rule     | Meaning                 |
| -------- | ----------------------- |
| Unique   | no duplicates           |
| Not NULL | always has a value      |
| Stable   | should not change often |

### Example of an Invalid Primary Key

Duplicate IDs are rejected by the database:

| id | name |
|----|------|
| 1  | Amr  |
| 1  | Ali  |

## SQL Example

```sql
CREATE TABLE users (
    id INT PRIMARY KEY,
    name VARCHAR(100)
);
```

### Auto-Increment Primary Key

Very common in practice:

```sql
id SERIAL PRIMARY KEY
```

The database automatically generates values: `1, 2, 3, 4...`

## Why Primary Keys Are Important

### 1. Unique Identification

They make it easy to find a specific row:

```sql
SELECT * FROM users
WHERE id = 1;
```

### 2. Relationships Between Tables

Foreign keys reference primary keys — a core mechanic of relational databases.

**Users table**

| id | name |
|----|------|
| 1  | Amr  |

**Orders table**

| id | user_id | total |
|----|---------|-------|
| 10 | 1       | 500   |

Here, `orders.user_id` references `users.id`.

### 3. Indexing Performance

Primary keys are automatically indexed in most databases, which makes lookups very fast.

#### Clustered Index (Advanced)

In many [SQL](sql.md) databases, the table is physically organized by its primary key — a very important performance topic.

## Natural Key vs Surrogate Key

- **[Natural Key](natural-key.md)** — real business data used as the primary key, e.g. `national_id`, `email`. Problem: natural data may change, become invalid, or be large.
- **[Surrogate Key](surrogate-key.md)** — an artificially generated ID, e.g. `id = 1`, `id = 2`. Most modern systems prefer this approach.

## UUID Primary Keys

Modern distributed systems often use UUIDs as primary keys, e.g. `550e8400-e29b-41d4-a716-446655440000`.

### Why UUID?

Good for:

- distributed systems
- microservices
- avoiding ID collisions

### Integer vs UUID

| Integer ID       | [UUID](uuid.md)                |
| ---------------- | ------------------- |
| Smaller          | Larger              |
| Faster indexing  | Slower indexing     |
| Sequential       | Globally unique     |
| Easier debugging | Better distribution |

See [UUID](uuid.md) and [ULID](ulid.md) for more detail.

## Composite Primary Key

A primary key can use multiple columns:

```sql
PRIMARY KEY (user_id, product_id)
```

Used in many-to-many relationships:

| user_id | product_id |
|---------|------------|
| 1       | 10         |
| 1       | 11         |

The combination must be unique.

## Candidate Key

A candidate key is any field that could uniquely identify a row; one candidate is chosen to become the primary key.

Example: a table may have `email`, `national_id`, and `id`, all unique — but `id` is chosen as the primary key.

## Primary Key vs Unique Key

| Primary Key     | Unique Key                     |
| --------------- | ------------------------------- |
| One per table   | Multiple allowed                 |
| NOT NULL        | Can allow NULL (depends on DB)     |
| Main identifier | Additional uniqueness               |

```sql
email UNIQUE
id PRIMARY KEY
```

See [Primary Key vs Unique Key](primary-key-vs-unique-key.md) for a full breakdown.

## Primary Key in ORMs

Prisma:

```prisma
model User {
  id Int @id @default(autoincrement())
}
```

TypeORM:

```typescript
@PrimaryGeneratedColumn()
id: number;
```

See [ORM](../../backend/data/orm.md) for more on how ORMs generate and manage keys.

## Common Questions

**What is a primary key?**
> A primary key uniquely identifies each row in a database table and cannot contain duplicate or null values.

**Why are primary keys important?**
Because they:
- uniquely identify records
- enable relationships
- improve indexing/query performance

**Difference between primary key and [foreign key](foreign-key.md)?**

| Primary Key    | [Foreign Key](foreign-key.md)               |
|----------------|---------------------------|
| Identifies row | References another table  |
| Unique         | Can repeat                |

**Difference between primary key and unique key?**
The primary key is the main identifier; a unique key only enforces uniqueness.

**Why are UUIDs used?**
To generate globally unique IDs in distributed systems.

## Senior-Level Answer

> A primary key is a unique, non-null identifier for database records that enables entity integrity, efficient indexing, and relational mapping across tables. It forms the foundational identity mechanism in relational database design.

## Easy Way to Remember

```text
Primary key = unique identity of row
```

## Related

- [Natural Key](natural-key.md)
- [Surrogate Key](surrogate-key.md)
- [Primary Key vs Unique Key](primary-key-vs-unique-key.md)
- [Foreign Key](foreign-key.md)
- [Indexing](indexing.md)
