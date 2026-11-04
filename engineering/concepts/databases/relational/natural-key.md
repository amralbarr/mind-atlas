# Natural Key

A natural key is:

> A real-world business value used to uniquely identify a record.

The data itself has business meaning and is naturally unique.

## Examples of Natural Keys

| Example          | Why Natural?     |
| ----------------- | ---------------- |
| National ID        | naturally unique   |
| Email                 | usually unique       |
| Passport Number          | unique                  |
| ISBN (books)                | unique                    |
| Car VIN                        | unique                      |

### Example Table

| national_id | name |
|-------------|------|
| 123456789   | Amr  |
| 987654321   | Ali  |

Here, `national_id` can be the [primary key](primary-key.md) because it's unique and has real business meaning.

## Natural Key vs Surrogate Key

- **Natural Key** — real-world data, e.g. `email`, `passport_number`, `national_id`.
- **[Surrogate Key](surrogate-key.md)** — an artificially generated ID, e.g. `id = 1`, `id = 2`, or a [UUID](uuid.md). No business meaning.

### Example Comparison

**Natural key**

| email | name |
|-------|------|
| amr@test.com | Amr |

[Primary key](primary-key.md): `email`

**[Surrogate key](surrogate-key.md)**

| id | email |
|----|-------|
| 1  | amr@test.com |

[Primary key](primary-key.md): `id`

## Why Natural Keys Are Attractive

- already unique
- no extra ID needed
- business meaningful

## Problems with Natural Keys

This is the important part.

### 1. Can Change

Example: an email address changes — bad for a [primary key](primary-key.md).

### 2. Large Size

Example: passport numbers or [UUID](uuid.md)-like strings produce larger indexes.

### 3. Business Logic Dependency

If a business rule changes, the key may become invalid.

### 4. Sensitive Data Exposure

National IDs and emails are poor choices as public identifiers.

## Why Modern Systems Prefer Surrogate Keys

Surrogate keys are stable, small, efficient to index, and independent from business logic.

### Common Modern Design

| Purpose              | Field           |
| --------------------- | --------------- |
| [Primary Key](primary-key.md)             | `id`              |
| Business Uniqueness        | `email UNIQUE`      |

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE
);
```

## Candidate Key

A candidate key is any field that could uniquely identify a row — e.g. `email`, `national_id`, `passport_number`. One of them becomes the [primary key](primary-key.md).

## Composite Natural Key

Sometimes a natural key uses multiple columns:

| country_code | phone  |
|--------------|--------|
| +966         | 555123 |

Together they form a unique identity.

## Natural Keys in Distributed Systems

Usually avoided because replication, synchronization, and updates become more complex. Modern distributed systems often use a [UUID](uuid.md) as a [surrogate key](surrogate-key.md) instead.

## Common Questions

**Why are surrogate keys preferred over natural keys?**
> Surrogate keys are stable, compact, immutable, and independent from business rules, making indexing and relational consistency easier over time.

**When are natural keys useful?**
When the value is truly immutable, compact, guaranteed unique, and business-critical.

**Is email a good [primary key](primary-key.md)?**
Usually no — emails may change, produce larger indexes, and expose sensitive info. Better: `id` as PRIMARY KEY, `email` as UNIQUE.

### Common Comparison

| Natural Key           | [Surrogate Key](surrogate-key.md)         |
| ----------------------- | ----------------------- |
| Real business data         | Artificial ID              |
| Meaningful                     | No business meaning            |
| Can change                          | Stable                            |
| Often larger                             | Usually small                       |
| More fragile                                  | More maintainable                       |

## Real-World Best Practice

Modern backend systems usually use a surrogate primary key plus natural unique constraints — e.g. `id` plus a unique `email`.

## Senior-Level Answer

> A natural key is a business-domain attribute that uniquely identifies a record, such as an email or national ID. While meaningful, natural keys are often avoided as primary keys in modern systems due to mutability, indexing overhead, and coupling to business rules.

## Easy Way to Remember

```text
Natural key   = real-world identity
Surrogate key = system-generated identity
```

## Related

- [Surrogate Key](surrogate-key.md)
- [Primary Key](primary-key.md)
- [Primary Key vs Unique Key](primary-key-vs-unique-key.md)
- [UUID](uuid.md)
