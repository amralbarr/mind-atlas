# Foreign Key

A foreign key is:

> A column in one table that references the [primary key](primary-key.md) of another table.

It creates a relationship between tables, and is one of the most important relational database concepts.

## Simple Example

**Users table** (`id` is the [primary key](primary-key.md)):

| id  | name |
| --- | ---- |
| 1   | Amr  |
| 2   | Ali  |

**Orders table** (`user_id` is the foreign key, referencing `users.id`):

| id  | user_id | total |
| --- | ------- | ----- |
| 100 | 1       | 500   |
| 101 | 2       | 300   |

This means order 100 belongs to user 1, and order 101 belongs to user 2:

```text
Users
  ↓
Orders
```

## SQL Foreign Key Example

```sql
CREATE TABLE orders (
    id INT PRIMARY KEY,
    user_id INT,
    total DECIMAL,

    FOREIGN KEY (user_id)
    REFERENCES users(id)
);
```

## Why Foreign Keys Matter

### 1. Maintain Relationships

Foreign keys link tables together.

### 2. Enforce Data Integrity

The database prevents invalid references. For example, if user 999 does not exist:

```sql
INSERT INTO orders (user_id)
VALUES (999);
```

The database rejects the insert, because user 999 does not exist.

### 3. Enable Relational Queries

Foreign keys are used with `JOIN` to combine related data:

```sql
SELECT users.name, orders.total
FROM users
JOIN orders
ON users.id = orders.user_id;
```

Result:

| name | total |
| ---- | ----- |
| Amr  | 500   |
| Ali  | 300   |

## Relationship Types

### One-to-One

Example: `User ↔ Passport` — one user has one passport.

### One-to-Many

The most common relationship type. Example: `User → Many Orders` — one user can have many orders.

### Many-to-Many

Example: `Students ↔ Courses` — many students take many courses. This requires a **junction table**:

| student_id | course_id |
| ---------- | --------- |
| 1          | 10        |
| 1          | 11        |

Both columns are usually foreign keys.

## Cascade Operations

Foreign keys can define behavior when the referenced (parent) row changes.

```sql
FOREIGN KEY (user_id)
REFERENCES users(id)
ON DELETE CASCADE
```

If a user is deleted, all related orders are deleted automatically.

| Option      | Meaning                          |
| ----------- | --------------------------------- |
| CASCADE     | Auto delete/update children         |
| SET NULL    | Child foreign key becomes NULL        |
| RESTRICT    | Prevent the deletion                    |
| NO ACTION   | Default behavior                          |

Example: deleting `users.id = 1` with `CASCADE` also deletes `orders.user_id = 1`. Without cascade, the database may reject the deletion instead.

## Foreign Key vs Primary Key

| [Primary Key](primary-key.md)                  | Foreign Key                     |
| ----------------------------- | --------------------------------- |
| Identifies a row uniquely       | References another table            |
| Unique                            | Can repeat                              |
| Typically one per table              | Multiple allowed                          |

Example — a user's `id` is unique, but many orders can share the same `user_id`, since one user can have many orders.

## Foreign Keys and Indexes

Foreign key columns are often indexed, because joins and lookups on them become much faster. See [Database Indexing](indexing.md).

## ORM Examples

Prisma:

```prisma
model Order {
  id     Int  @id
  userId Int

  user User @relation(fields: [userId], references: [id])
}
```

TypeORM:

```typescript
@ManyToOne(() => User)
user: User;
```

## Common Questions

**Q1. What is a foreign key?**

> A foreign key is a column that references the [primary key](primary-key.md) of another table to establish relational integrity between tables.

**Q2. Why are foreign keys important?**

Because they enforce valid relationships, prevent inconsistent data, and enable relational joins.

**Q3. Difference between [primary key](primary-key.md) and foreign key?**

A [primary key](primary-key.md) is a unique identity for a row; a foreign key is a reference to another table.

**Q4. Can a foreign key contain duplicates?**

Yes — for example, many orders can share the same `user_id`.

**Q5. What is cascade delete?**

Automatically deleting related child rows when the parent row is deleted.

**Q6. What is a one-to-many relationship?**

One parent record associated with many child records.

**Senior-level answer:**

> A foreign key is a relational constraint that references the [primary key](primary-key.md) of another table, ensuring referential integrity and enabling normalized relational data modeling through controlled inter-table relationships.

**Easy way to remember:**

```text
Primary key = who I am
Foreign key = who I belong to
```

## Related

- [Primary Key](primary-key.md)
- [SQL](sql.md)
- [ACID](acid.md)
- [Database Indexing](indexing.md)
- [Surrogate Key](surrogate-key.md)
- [Database Normalization](database-normalization.md)
