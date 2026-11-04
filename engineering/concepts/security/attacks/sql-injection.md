# SQL Injection

[SQL](../../databases/relational/sql.md) injection is a vulnerability where attacker-controlled input is concatenated directly into a [SQL](../../databases/relational/sql.md) query string, letting the attacker change the query's actual logic — reading data they shouldn't, bypassing [authentication](../auth/authentication.md), or modifying/deleting data — instead of just supplying a value.

## The Core Mistake: Building Queries by String Concatenation

```javascript
// Vulnerable
const suppliedPass = req.body.pass;
const query = `SELECT * FROM users WHERE email = '${email}' AND pass = '${suppliedPass}'`;
```

If `email` is supplied by the attacker as:

```text
' OR '1'='1
```

the query becomes:

```sql
SELECT * FROM users WHERE email = '' OR '1'='1' AND pass = '...'
```

`'1'='1'` is always true, so the `WHERE` clause matches every row — the attacker logs in as the first user in the table without knowing any password.

## A More Damaging Example

```text
Input: '; DROP TABLE users; --
```

```sql
SELECT * FROM users WHERE email = ''; DROP TABLE users; --'
```

If the driver/database allows multiple statements per call, this drops the entire `users` table. The `--` comments out the rest of the original query so it doesn't cause a syntax error.

## The Fix: Parameterized Queries (Prepared Statements)

The value is sent to the database **separately** from the query structure, so the database never interprets it as [SQL](../../databases/relational/sql.md) — it's always treated as a literal value, no matter what characters it contains.

```javascript
// Safe — parameterized query
const result = await db.query(
  'SELECT * FROM users WHERE email = $1 AND password = $2',
  [email, password]
);
```

```python
# Safe — parameterized query (Python, psycopg2)
cursor.execute(
    "SELECT * FROM users WHERE email = %s AND password = %s",
    (email, password)
)
```

Even if `email` contains `' OR '1'='1`, the database treats it as a literal string to compare against the `email` column — not as [SQL](../../databases/relational/sql.md) syntax — so the injection has no effect.

## Why ORMs Help (But Aren't a Silver Bullet)

An [ORM](../../backend/data/orm.md) generates parameterized queries by default for its standard query-builder methods (`.find()`, `.where()`, etc.), which is why "just use an [ORM](../../backend/data/orm.md)" is common advice. But an [ORM](../../backend/data/orm.md) can still be made vulnerable if raw [SQL](../../databases/relational/sql.md) is dropped in manually with string interpolation:

```typescript
// Still vulnerable, even though it's "using an ORM"
await prisma.$queryRawUnsafe(`SELECT * FROM users WHERE email = '${email}'`);

// Safe — parameterized raw query
await prisma.$queryRaw`SELECT * FROM users WHERE email = ${email}`;
```

The safety comes specifically from parameterization, not from "using an [ORM](../../backend/data/orm.md)" as a label — any raw/unsafe escape hatch reintroduces the exact same risk.

## Other Injection Surfaces Beyond Login Forms

- **Search/filter parameters** — `?sort=name` used directly to build an `ORDER BY` clause (parameterization doesn't work for identifiers like column/table names — these must be validated against an allow-list instead).
- **NoSQL "injection"** — a related class of bug in document databases: passing an unsanitized object where a query operator is expected (e.g. [MongoDB](../../databases/nosql/mongodb.md) accepting `{ "$gt": "" }` as a password field from [JSON](../../programming/fundamentals/json.md) input) can similarly bypass intended query logic. The fix is the same principle — never let attacker-controlled input dictate query *structure*, only query *values*.

## Defense-in-Depth

| Layer | What it adds |
|---|---|
| **Parameterized queries** | The primary, reliable defense — makes injection structurally impossible for value positions |
| **Least-privilege DB accounts** | The application's DB user shouldn't have `DROP TABLE` or cross-schema permissions it doesn't need — limits blast radius if injection does occur |
| **Input validation** | Reject obviously malformed input early (e.g. an email field that isn't email-shaped) — a secondary layer, not a substitute for parameterization |
| **[ORM](../../backend/data/orm.md)/query builder by default** | Removes the temptation to hand-write [SQL](../../databases/relational/sql.md) string concatenation for routine CRUD |
| **[WAF](waf.md) (Web Application Firewall)** | Can catch known injection patterns at the edge — a backstop, not a fix for the underlying code |

## Common Questions

**Does using an [ORM](../../backend/data/orm.md) automatically mean an application is safe from SQL injection?**
> No — it's safe for the [ORM](../../backend/data/orm.md)'s own generated queries, but any raw/unsafe [SQL](../../databases/relational/sql.md) escape hatch (common when the [ORM](../../backend/data/orm.md)'s query builder can't express something) reintroduces the exact same risk if that raw [SQL](../../databases/relational/sql.md) is built via string concatenation instead of parameterization.

**Can SQL injection happen through something other than a text input field?**
> Yes — [HTTP](../../networking/http.md) headers, cookies, URL path segments, and even file names/upload metadata can all end up in a SQL query if the backend isn't careful. Any attacker-influenced value that reaches a query is a potential injection point, not just obvious form fields.

**Why can't parameterization fix identifiers like column or table names?**
> Because parameterized query placeholders (`$1`, `%s`) are only for *values* in the query — the database driver quotes/escapes them as literals. A column or table name is part of the query's *structure*, which placeholders can't substitute into. Dynamic identifiers must be validated against a fixed allow-list of known-safe names instead.

## Related

- [ORM](../../backend/data/orm.md)
- [XSS](xss.md)
- [PostgreSQL](../../databases/relational/postgresql.md)
- [Access Control & IAM](../authorization/access-control-iam.md)
