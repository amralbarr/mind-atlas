# PgBouncer

PgBouncer is a lightweight, open-source **external connection pooler** for [PostgreSQL](postgresql.md) — a small, single-purpose proxy process that sits between application clients and the real Postgres server. Instead of the application connecting straight to `postgres:5432`, it connects to `pgbouncer:5432` instead; PgBouncer holds a small pool of real backend connections to Postgres and multiplexes a much larger number of client connections onto them, adding roughly half a millisecond of latency per hop in exchange for protecting Postgres from being overwhelmed by connection count.

This is the "external connection pooler" row from the [connection pooling](connection-pooling.md) note's application-level-vs-external comparison — PgBouncer is the canonical example for Postgres specifically.

## Why It Exists

Every Postgres connection is backed by its own OS process on the server, each consuming real memory (often several MB) whether or not it's actively running a query. Each application instance opening its own in-process pool multiplies: 10 app containers × 20 connections each = 200 real Postgres connections, even if most sit idle most of the time. This gets worse with background workers — a [Celery](../../distributed-systems/messaging/celery.md) deployment typically runs several worker processes *in addition to* the web app, and each one can hold its own pool, multiplying the total further. PgBouncer collapses all of that fan-out onto a small, fixed-size pool of real connections that Postgres can comfortably sustain.

```text
Without PgBouncer:
  app (20 conns) ─┐
  celery worker 1 (10 conns) ─┤
  celery worker 2 (10 conns) ─┼──> Postgres (needs 40+ real connections)
  celery beat (5 conns) ─────┘

With PgBouncer:
  app ─┐
  celery worker 1 ─┤
  celery worker 2 ─┼──> PgBouncer ──> Postgres (needs only ~15-20 real connections)
  celery beat ─────┘
```

## Pooling Modes

PgBouncer's `pool_mode` setting controls *when* a client connection gets detached from its backend Postgres connection and returned to the pool for someone else to use:

| Mode | Backend connection held for | Compatibility | Multiplexing |
|---|---|---|---|
| **Session** (default) | The entire client session, until it disconnects | Full — behaves just like connecting directly to Postgres | None — 1:1, same connection count as no pooler at all |
| **Transaction** | A single transaction, returned to the pool the moment it commits/rolls back | Breaks session-scoped features (see below) | High — hundreds of clients can share a handful of backend connections |
| **Statement** | A single statement, no multi-statement transactions allowed | Most restrictive; only for simple autocommit workloads (e.g. PL/Proxy) | Highest, but rarely usable for normal application code |

**Transaction pooling** is the mode almost everyone actually wants in production — it's the one that delivers the real multiplexing win — but it comes with a real cost: because the backend connection can be handed to a *different* client between transactions, anything that relies on server-side session state stops working reliably:

- `SET`/session-level config changes (`SET statement_timeout = ...`)
- `PREPARE`/named prepared statements (unless `max_prepared_statements` is configured)
- `LISTEN`/`WITH HOLD` cursors
- Session-level advisory locks
- Temp tables that are expected to outlive one transaction

Most ORMs and frameworks are fine under transaction pooling as long as each unit of work is a self-contained transaction — which is already the norm — but it's worth checking an app's actual connection usage (migrations in particular often need a direct, unpooled connection, since `CREATE INDEX CONCURRENTLY` and some DDL don't tolerate running through a pooled, multiplexed connection the same way).

## Self-Hosting PgBouncer vs. Using a Provider's Managed Pooler

Several managed [PostgreSQL](postgresql.md) providers now ship PgBouncer itself as a built-in, provider-operated feature rather than something the application team deploys — Neon includes a managed PgBouncer pooler on every compute automatically, and [Azure](../../cloud/azure/azure.md) Database for [PostgreSQL](postgresql.md) Flexible Server offers it as an optional per-server feature on port 6432. In both cases it's the exact same software described on this page, just run by the provider instead of self-hosted — see [Managed Connection Pooling](managed-connection-pooling.md) for the fuller comparison against self-hosting, including other providers ([AWS](../../cloud/infrastructure/aws.md) RDS Proxy, Supabase's Supavisor) that solve the same problem with their own non-PgBouncer implementations instead.

## Minimal Configuration

```ini
# pgbouncer.ini
[databases]
mydb = host=postgres port=5432 dbname=mydb

[pgbouncer]
listen_addr = 0.0.0.0
listen_port = 5432
auth_type = scram-sha-256
auth_file = /etc/pgbouncer/userlist.txt

pool_mode = transaction
max_client_conn = 1000       # how many clients PgBouncer itself will accept
default_pool_size = 20       # real backend connections per database/user pair
```

```text
# userlist.txt — "username" "password-hash-or-plaintext"
"myapp" "SCRAM-SHA-256$4096:..."
```

## Docker Compose Example

A common production pattern — exactly the shape of putting PgBouncer in front of Postgres for an app plus [Celery](../../distributed-systems/messaging/celery.md) workers sharing one database:

```yaml
services:
  postgres:
    image: postgres:16
    environment:
      POSTGRES_USER: myapp
      POSTGRES_PASSWORD: secret
      POSTGRES_DB: mydb
    volumes:
      - postgres_data:/var/lib/postgresql/data

  pgbouncer:
    image: edoburu/pgbouncer
    environment:
      DATABASE_URL: postgres://myapp:secret@postgres:5432/mydb
      POOL_MODE: transaction
      MAX_CLIENT_CONN: 1000
      DEFAULT_POOL_SIZE: 20
    depends_on:
      - postgres
    ports:
      - "6432:5432"

  app:
    build: .
    environment:
      # app connects to pgbouncer, never directly to postgres
      DATABASE_URL: postgres://myapp:secret@pgbouncer:5432/mydb
    depends_on:
      - pgbouncer

  celery-worker:
    build: .
    command: celery -A tasks worker --loglevel=info
    environment:
      DATABASE_URL: postgres://myapp:secret@pgbouncer:5432/mydb
    depends_on:
      - pgbouncer

volumes:
  postgres_data:
```

## Common Questions

**Does PgBouncer replace an application-level pool, or sit alongside it?**
> Alongside — the application (or its [ORM](../../backend/data/orm.md)/driver) typically still keeps its own small in-process pool, but that pool's connections point at PgBouncer instead of Postgres directly. PgBouncer's job is collapsing the *fan-out across many app/worker processes*, not eliminating pooling at the application layer entirely.

**Why would [Celery](../../distributed-systems/messaging/celery.md) workers specifically need to go through PgBouncer?**
> Each [Celery](../../distributed-systems/messaging/celery.md) worker process (and `celery beat`) opens its own database connections independently of the web app, just like a separate application instance would. Without a shared pooler in front, a deployment with several worker processes plus the web app can easily multiply total Postgres connections past what the server is configured (or licensed) to handle — routing everything through PgBouncer caps that regardless of how many worker processes are running.

**What breaks if I just assume transaction pooling behaves like a direct connection?**
> Code that calls `SET` to change a session setting, relies on a prepared statement persisting across requests, or opens a `LISTEN` channel and expects to keep receiving on the same backend connection will behave inconsistently — the backend connection underneath can change between any two transactions. This is the single most common PgBouncer production surprise, and it's why migrations/DDL are often pointed at Postgres directly rather than through the pooled connection.

## Related

- [Connection Pooling](connection-pooling.md) — the general concept PgBouncer is the canonical Postgres-specific implementation of
- [PostgreSQL](postgresql.md) — the database PgBouncer sits in front of and proxies connections to
- [Celery](../../distributed-systems/messaging/celery.md) — a common source of extra connection fan-out (worker processes + beat) that PgBouncer collapses
- [Read Replicas](read-replicas.md) — another database-scaling technique often deployed alongside PgBouncer, addressing read throughput rather than connection count
- [Managed Connection Pooling](managed-connection-pooling.md) — covers Neon and [Azure](../../cloud/azure/azure.md)'s provider-operated PgBouncer offerings, plus the non-PgBouncer alternatives ([AWS](../../cloud/infrastructure/aws.md) RDS Proxy, Supabase's Supavisor) and the tradeoffs vs. self-hosting PgBouncer directly
