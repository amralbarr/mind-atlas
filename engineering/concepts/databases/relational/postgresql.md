# PostgreSQL

PostgreSQL (often called Postgres) is a powerful, open-source object-relational database system with over 35 years of active development. It is the preferred production database for most modern web and data applications due to its strict [SQL](sql.md) standards compliance, rich data types ([JSON](../../programming/fundamentals/json.md), arrays, [UUID](uuid.md), range types), advanced indexing, and extensibility (e.g. `pgvector` for vector search).

## When to Use PostgreSQL

| Good fit                                                                                                                  | Poor fit                                                   |
| ------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------- |
| Production web apps ([FastAPI](../../programming/python/fastapi.md), [Django](../../programming/python/django.md), Rails) | Embedded / no-server apps (use [SQLite](sqlite.md))        |
| Complex queries, CTEs, window functions                                                                                   | Ultra-simple read-heavy apps that prefer [MySQL](mysql.md) |
| [JSON](../../programming/fundamentals/json.md) storage with querying (`JSONB`)                                                                                      | Teams already deeply committed to [MySQL](mysql.md)                    |
| Vector search via `pgvector`                                                                                              |                                                            |
| Full-text search (`tsvector`)                                                                                             |                                                            |
| Strong data integrity requirements                                                                                        |                                                            |

## Installation

```bash
# Ubuntu / Debian
sudo apt install postgresql postgresql-contrib -y
sudo systemctl enable --now postgresql

# Connect as postgres superuser
sudo -u postgres psql

# Docker (quickest)
docker run -d \
  --name postgres \
  -e POSTGRES_USER=myuser \
  -e POSTGRES_PASSWORD=mypass \
  -e POSTGRES_DB=mydb \
  -p 5432:5432 \
  postgres:16
```

## Docker Compose

```yaml
services:
  db:
    image: postgres:16
    environment:
      POSTGRES_USER: myuser
      POSTGRES_PASSWORD: mypass
      POSTGRES_DB: mydb
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql:ro

volumes:
  postgres_data:
```

## psql CLI

```bash
# Connect
psql -h localhost -U myuser -d mydb

# Inside psql
\l           -- list databases
\c mydb      -- connect to database
\dt          -- list tables
\d users     -- describe table
\q           -- quit

# Run a SQL file
psql -h localhost -U myuser -d mydb -f schema.sql

# Dump database
pg_dump -U myuser mydb > backup.sql

# Restore
psql -U myuser mydb < backup.sql
```

## Core SQL (PostgreSQL Syntax)

```sql
-- Create table
CREATE TABLE users (
    id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name       TEXT NOT NULL,
    email      TEXT UNIQUE NOT NULL,
    role       TEXT NOT NULL DEFAULT 'user' CHECK (role IN ('admin', 'user')),
    metadata   JSONB DEFAULT '{}',
    tags       TEXT[],
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Insert
INSERT INTO users (name, email) VALUES ('Alice', 'alice@example.com');

-- Query
SELECT * FROM users WHERE role = 'admin' ORDER BY created_at DESC LIMIT 10;

-- JSONB query
SELECT * FROM users WHERE metadata->>'department' = 'finance';
SELECT * FROM users WHERE metadata @> '{"active": true}';

-- Array query
SELECT * FROM users WHERE 'python' = ANY(tags);

-- Full-text search
SELECT * FROM posts WHERE to_tsvector('english', body) @@ plainto_tsquery('english', 'search term');

-- Window function
SELECT name, salary, RANK() OVER (PARTITION BY department ORDER BY salary DESC) AS rank FROM employees;

-- CTE
WITH top_users AS (
    SELECT user_id, COUNT(*) AS orders FROM orders GROUP BY user_id ORDER BY orders DESC LIMIT 10
)
SELECT u.name, t.orders FROM users u JOIN top_users t ON u.id = t.user_id;
```

## Python Client (`psycopg2`)

```bash
pip install psycopg2-binary python-dotenv
```

```python
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv

load_dotenv()

conn = psycopg2.connect(
    host=os.getenv("POSTGRES_HOST", "localhost"),
    port=int(os.getenv("POSTGRES_PORT", 5432)),
    dbname=os.getenv("POSTGRES_DB"),
    user=os.getenv("POSTGRES_USER"),
    password=os.getenv("POSTGRES_PASSWORD"),
)

with conn.cursor(cursor_factory=RealDictCursor) as cur:
    cur.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    user = cur.fetchone()
    print(dict(user))

    cur.execute(
        "INSERT INTO users (name, email) VALUES (%s, %s) RETURNING id",
        ("Bob", "bob@example.com"),
    )
    new_id = cur.fetchone()["id"]
    conn.commit()

conn.close()
```

Use **`%s`** as the placeholder. Never use f-strings with [SQL](sql.md) — [SQL injection](../../security/attacks/sql-injection.md) risk.

## Async Client (`asyncpg`)

```bash
pip install asyncpg
```

```python
import asyncpg
import os

async def main():
    conn = await asyncpg.connect(os.getenv("DATABASE_URL"))

    rows = await conn.fetch("SELECT * FROM users WHERE role = $1", "admin")
    for row in rows:
        print(dict(row))

    await conn.execute(
        "INSERT INTO users(name, email) VALUES($1, $2)",
        "Alice", "alice@example.com",
    )
    await conn.close()
```

Use `asyncpg` with [FastAPI](../../programming/python/fastapi.md) + async endpoints for best performance.

## SQLAlchemy with PostgreSQL

```bash
pip install sqlalchemy psycopg2-binary
# or async:
pip install sqlalchemy asyncpg
```

```python
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine
import os
from dotenv import load_dotenv

load_dotenv()

# Sync
engine = create_engine(os.getenv("DATABASE_URL"), pool_pre_ping=True)

# Async
async_engine = create_async_engine(
    os.getenv("DATABASE_URL").replace("postgresql://", "postgresql+asyncpg://"),
    pool_pre_ping=True,
)
```

## Environment Variables

```bash
# .env
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=mydb
POSTGRES_USER=myuser
POSTGRES_PASSWORD=secret

# Or as a single URL (preferred by most ORMs and tools)
DATABASE_URL=postgresql://myuser:secret@localhost:5432/mydb
```

## JSONB vs JSON

| | `JSON` | `JSONB` |
|---|---|---|
| Storage | Text (exact input preserved) | Binary (parsed on insert) |
| Indexing | No | Yes (GIN index) |
| Query operators | Limited | Full (`@>`, `?`, `#>`, etc.) |
| Performance | Slower to query | Faster to query |

**Always use `JSONB`** for [JSON](../../programming/fundamentals/json.md) columns you will query or index.

```sql
-- GIN index on JSONB for fast containment queries
CREATE INDEX idx_users_metadata ON users USING GIN (metadata);
```

## pgvector (Vector Search)

```bash
# Install extension (Docker image: pgvector/pgvector:pg16)
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE documents (
    id      SERIAL PRIMARY KEY,
    content TEXT,
    embedding VECTOR(1536)     -- dimension must match your model
);

-- Insert with embedding
INSERT INTO documents (content, embedding) VALUES ('Hello world', '[0.1, 0.2, ...]');

-- Similarity search (cosine distance)
SELECT content, embedding <=> '[0.1, 0.2, ...]' AS distance
FROM documents
ORDER BY distance
LIMIT 5;

-- Index for fast ANN search
CREATE INDEX ON documents USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
```

## User Management

```sql
-- Create a user
CREATE USER appuser WITH PASSWORD 'strongpassword';

-- Grant permissions
GRANT CONNECT ON DATABASE mydb TO appuser;
GRANT USAGE ON SCHEMA public TO appuser;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO appuser;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO appuser;

-- Read-only user
GRANT CONNECT ON DATABASE mydb TO readonly;
GRANT USAGE ON SCHEMA public TO readonly;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO readonly;
```

## Indexing

```sql
-- B-tree (default — equality and range queries)
CREATE INDEX idx_users_email ON users(email);

-- GIN (JSONB, arrays, full-text)
CREATE INDEX idx_users_metadata ON users USING GIN(metadata);
CREATE INDEX idx_posts_fts ON posts USING GIN(to_tsvector('english', body));

-- Partial index (only index subset of rows)
CREATE INDEX idx_active_users ON users(email) WHERE active = true;

-- Unique index
CREATE UNIQUE INDEX idx_users_email_unique ON users(email);
```

## PostgreSQL vs MySQL vs SQLite

| | PostgreSQL | [MySQL](mysql.md) | [SQLite](sqlite.md) |
|---|---|---|---|
| [JSON](../../programming/fundamentals/json.md) | JSONB (binary, indexed) | Basic [JSON](../../programming/fundamentals/json.md) | None |
| Arrays | Native `TEXT[]`, `INT[]` | No | No |
| Window functions | Full | Yes (8.0+) | Yes (3.25+) |
| Full-text search | `tsvector`, `pg_trgm` | FULLTEXT | FTS5 |
| Vector search | `pgvector` extension | No | No |
| Standards compliance | High | Moderate | Moderate |
| Best for | Production, complex queries | Web apps, broad hosting | Embedded, local, tests |

## Related Concepts

- [systemctl (systemd) Commands](../../../commands/systemctl.md) — managing the `postgresql` service itself (start/stop/restart/logs) beyond the initial `enable --now`
- [MySQL](./mysql.md) — alternative production relational database
- [SQLite](./sqlite.md) — embedded database for dev and local use
- [SQL](./sql.md) — [SQL](sql.md) fundamentals
- [ACID](./acid.md) — PostgreSQL is fully [ACID](acid.md)-compliant
- [Indexing](./indexing.md) — B-tree, GIN, GiST, BRIN index types
- [ORM](../../backend/data/orm.md) — SQLAlchemy, [Django](../../programming/python/django.md) [ORM](../../backend/data/orm.md) with PostgreSQL
- [Vector Databases](../../ai/retrieval/vector-database.md) — pgvector as a vector store option
- [Connection Pooling](connection-pooling.md) — reusing connections to avoid per-request setup cost against a Postgres server
- [PgBouncer](pgbouncer.md) — the canonical external connection pooler deployed in front of PostgreSQL specifically
