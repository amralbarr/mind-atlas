# Primary Key vs Unique Key

This is a common source of confusion for developers: "multiple allowed" for unique keys means *multiple UNIQUE constraints in the same table*, not *multiple duplicated values*.

## Understanding UNIQUE

A UNIQUE key means values in that column cannot repeat.

Allowed:

| email |
|-------|
| a@test.com |
| b@test.com |

Not allowed:

| email |
|-------|
| a@test.com |
| a@test.com |

## Primary Key

A [PRIMARY KEY](primary-key.md) is:

- unique
- NOT NULL
- the main identity of the row

There is only one [primary key](primary-key.md) definition per table.

```sql
CREATE TABLE users (
    id INT PRIMARY KEY,
    name VARCHAR(100)
);
```

Here, `id` is the main identity.

## Unique Key

A UNIQUE key is an additional uniqueness rule.

```sql
CREATE TABLE users (
    id INT PRIMARY KEY,
    email VARCHAR(255) UNIQUE,
    national_id VARCHAR(50) UNIQUE
);
```

| Column      | Constraint  |
| ----------- | ----------- |
| id          | [PRIMARY KEY](primary-key.md) |
| email       | UNIQUE      |
| national_id | UNIQUE      |

### What "Multiple Allowed" Actually Means

A table can have:

- one [primary key](primary-key.md)
- many unique constraints

| Column   | Type        |
| -------- | ----------- |
| id       | [PRIMARY KEY](primary-key.md) |
| email    | UNIQUE      |
| username | UNIQUE      |
| phone    | UNIQUE      |

All valid — but values within each column still cannot repeat:

| id | email |
|----|-------|
| 1  | a@test.com |
| 2  | a@test.com |

This is rejected, because UNIQUE means no duplicate values.

### Why Use UNIQUE If a Primary Key Already Exists?

Because other fields also must stay unique — e.g. emails and usernames must not duplicate, even though `id` is already the row's identity.

**Example**

| id | email | username |
|----|-------|----------|
| 1  | a@test.com | amr |
| 2  | b@test.com | ali |

Rules: `id` is the unique identity, `email` cannot repeat, `username` cannot repeat.

### Why the Primary Key Usually Uses a Surrogate ID

Because it needs to be stable, small, and efficient. See [Surrogate Key](surrogate-key.md).

### Why UNIQUE Is Used on Business Fields

Because emails and usernames must not duplicate, even though they aren't the row's main identity.

## Key Differences

### PRIMARY KEY

Means "main identity of row." The database treats it specially internally.

### UNIQUE KEY

Means "this field also must remain unique," but it is not the main identity.

### NULL Handling

This distinction is important:

- **[PRIMARY KEY](primary-key.md)** cannot be NULL — `NULL` in an `id` column is impossible.
- **UNIQUE KEY** behavior depends on the database. Some databases (including [PostgreSQL](postgresql.md)) allow multiple NULLs in a UNIQUE column, because `NULL != NULL` in [SQL](sql.md) logic — each NULL is treated as an unknown value, not a duplicate.

```sql
CREATE TABLE users (
    email VARCHAR(255) UNIQUE
);
```

Allowed in [PostgreSQL](postgresql.md):

| email |
|-------|
| NULL  |
| NULL  |

### Composite UNIQUE Key

UNIQUE can also apply to multiple columns together:

```sql
UNIQUE(first_name, phone)
```

This means the *combination* must be unique.

Allowed:

| first_name | phone |
|------------|-------|
| Amr        | 123   |
| Amr        | 456   |

Rejected:

| first_name | phone |
|------------|-------|
| Amr        | 123   |
| Amr        | 123   |

## Deeper Understanding

**PRIMARY KEY** is used for: row identity, relationships, foreign keys, clustering/indexing.

**UNIQUE KEY** is used for: business constraints, validation, alternate unique fields.

### Real Best Practice

Modern systems usually combine both:

```sql
CREATE TABLE users (
    id UUID PRIMARY KEY,
    email VARCHAR(255) UNIQUE,
    username VARCHAR(50) UNIQUE,
    phone VARCHAR(20) UNIQUE
);
```

## Common Questions

**Why not make email the primary key?**
Because email can change, produces larger indexes, and creates a business-logic dependency. Better: `id` as PRIMARY KEY, `email` as UNIQUE.

**Can a table have multiple UNIQUE keys?**
Yes — e.g. `email`, `username`, and `phone` can all be UNIQUE in the same table.

**Can a table have multiple PRIMARY KEYs?**
No. Only one primary key definition per table (though it can be composite):

```sql
PRIMARY KEY(user_id, product_id)
```

This is still one primary key constraint using multiple columns.

## Easy Way to Remember

```text
PRIMARY KEY = main identity
UNIQUE KEY  = also cannot repeat
```

## Related

- [Primary Key](primary-key.md)
- [Natural Key](natural-key.md)
- [Surrogate Key](surrogate-key.md)
- [UUID](uuid.md)
- [Foreign Key](foreign-key.md)
