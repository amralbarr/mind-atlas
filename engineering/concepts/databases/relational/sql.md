# SQL

SQL (**Structured Query Language**) is the standard language used to interact with relational databases.

It is used with databases such as:

- [PostgreSQL](postgresql.md)
- [MySQL](mysql.md)
- Microsoft SQL Server
- Oracle Database
- [SQLite](sqlite.md)

## Simple Definition

> SQL is a language used to store, retrieve, update, and manage data inside databases.

## Example Database

Imagine an application database with a `users` table:

| id  | name | age |
| --- | ---- | --- |
| 1   | Amr  | 30  |
| 2   | Ali  | 25  |

## CRUD Operations

SQL can create, read, update, and delete data — commonly known as **CRUD**:

| Operation | SQL Statement |
| --------- | -------------- |
| Create    | `INSERT`       |
| Read      | `SELECT`       |
| Update    | `UPDATE`       |
| Delete    | `DELETE`       |

### SELECT — Read Data

The most common SQL command.

```sql
SELECT * FROM users;
```

Returns all users:

| id  | name | age |
| --- | ---- | --- |
| 1   | Amr  | 30  |
| 2   | Ali  | 25  |

Select specific columns:

```sql
SELECT name FROM users;
```

Filter with a `WHERE` condition:

```sql
SELECT * FROM users
WHERE age > 26;
```

### INSERT — Add Data

```sql
INSERT INTO users (name, age)
VALUES ('Amr', 30);
```

### UPDATE — Modify Data

```sql
UPDATE users
SET age = 31
WHERE id = 1;
```

### DELETE — Remove Data

```sql
DELETE FROM users
WHERE id = 1;
```

## Relational Databases

A relational database stores data in **tables** made up of rows, columns, and relationships between tables.

### Example Relationship

**Users table:**

| id  | name |
| --- | ---- |
| 1   | Amr  |

**Orders table:**

| id  | user_id | total |
| --- | ------- | ----- |
| 1   | 1       | 500   |

The `user_id` column links `orders` back to `users`.

### SQL Joins

Joins combine rows from multiple related tables:

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

## Primary Key and Foreign Key

A [primary key](primary-key.md) uniquely identifies each row in a table (usually unique and indexed), for example `id`.

A [foreign key](foreign-key.md) links tables together by referencing another table's [primary key](primary-key.md), for example `user_id` referencing `users.id`. See [Foreign Key](foreign-key.md) for cascade behavior, relationship types, and more.

## SQL Database Characteristics

| Feature             | SQL Database |
| -------------------- | ------------- |
| Structured schema     | Yes           |
| Relations             | Yes           |
| [ACID](acid.md) transactions     | Yes           |
| Strong consistency    | Yes           |
| Joins                 | Excellent     |

## ACID Transactions

SQL databases guarantee **[ACID](acid.md)** properties for transactions — Atomicity, Consistency, Isolation, and Durability. See [ACID](acid.md) for a full breakdown.

Example bank transfer transaction:

```sql
BEGIN;

UPDATE accounts
SET balance = balance - 100
WHERE id = 1;

UPDATE accounts
SET balance = balance + 100
WHERE id = 2;

COMMIT;
```

Transactions prevent partial updates and corrupted data — either both `UPDATE` statements apply, or neither does.

## Indexes

Indexes improve query speed by letting the database quickly locate rows instead of scanning the entire table:

```sql
CREATE INDEX idx_users_email
ON users(email);
```

See [Database Indexing](indexing.md) for index types, trade-offs, and fragmentation.

## SQL vs NoSQL

| SQL                 | NoSQL                       |
| ------------------- | ---------------------------- |
| Tables               | Documents / key-value        |
| Structured schema    | Flexible schema               |
| Strong consistency   | Often [eventual consistency](../../distributed-systems/patterns/eventual-consistency.md)    |
| Joins                | Limited or none                |
| [ACID](acid.md)                 | Varies by database             |

## Common SQL Databases

| Database              | Notes                 |
| ---------------------- | ---------------------- |
| [PostgreSQL](postgresql.md)              | Advanced, open-source   |
| [MySQL](mysql.md)                   | Very popular            |
| [SQLite](sqlite.md)                  | Lightweight              |
| Microsoft SQL Server    | Enterprise                |

## ORM (Object-Relational Mapper)

Modern backends often use an [ORM](../../backend/data/orm.md) instead of writing raw SQL. Examples: Prisma, TypeORM, SQLAlchemy.

Instead of:

```sql
SELECT * FROM users;
```

You write:

```typescript
prisma.user.findMany()
```

## SQL Query Execution Flow

```text
Application
    ↓
SQL Query
    ↓
Database Engine
    ↓
Result
```

## Common Questions

**Q1. What is SQL?**

> SQL is a language used to define, query, manipulate, and manage relational database data.

**Q2. Difference between SQL and NoSQL?**

SQL databases use structured relational tables with strong consistency, while NoSQL databases use flexible schemas optimized for scalability and distributed workloads.

**Q3. What is a [primary key](primary-key.md)?**

A unique identifier for table rows.

**Q4. What is a [foreign key](foreign-key.md)?**

A field that references another table's [primary key](primary-key.md).

**Q5. What is a JOIN?**

An operation combining rows from multiple related tables.

**Q6. Why are indexes important?**

Indexes improve query performance by reducing full table scans.

**Q7. What is a transaction?**

A group of operations executed atomically.

**Senior-level answer:**

> SQL is a declarative language for interacting with relational databases, enabling structured querying, transactional consistency, relational modeling, and efficient data manipulation through standardized operations and indexing strategies.

**Easy way to remember:**

```text
SQL = language for relational databases
```

## Related

- [Database Indexing](indexing.md)
- [ACID](acid.md)
- [Foreign Key](foreign-key.md)
- [Distributed Transactions](../distributed/distributed-transactions.md)
- [ORM](../../backend/data/orm.md)
