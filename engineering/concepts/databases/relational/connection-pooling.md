# Connection Pooling

Opening a database connection is expensive — a [TCP](../../networking/tcp.md) handshake, [TLS](../../networking/tls.md) negotiation if encrypted, [authentication](../../security/auth/authentication.md), and session setup on the database side. A connection pool avoids paying that cost on every query by keeping a set of already-open connections ready to be reused, handing one out to whichever part of the application needs it and returning it to the pool when done, instead of opening and closing a fresh connection per request.

## Without a Pool

```text
Request 1: open connection → run query → close connection
Request 2: open connection → run query → close connection
Request 3: open connection → run query → close connection
```

Every single request pays the full connection-setup cost, which can easily dominate the actual query time for a simple, fast query — and under real concurrent load, a database can only handle so many simultaneous connection *establishments* before that overhead alone becomes the bottleneck.

## With a Pool

```text
Pool: [conn1] [conn2] [conn3] ... [connN]   (opened once, kept alive)

Request 1: borrow conn1 → run query → return conn1 to pool
Request 2: borrow conn2 → run query → return conn2 to pool
Request 3: borrow conn1 (now free again) → run query → return
```

Connections are established once (or lazily, up to the pool's configured size) and reused across many requests — the setup cost is paid a handful of times total, not once per request.

## Key Configuration Parameters

| Parameter              | What it controls                                                                                                                                                                                              |
| ---------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Min pool size**      | The minimum number of connections kept open even when idle, so a burst of traffic doesn't have to pay connection-setup cost from zero                                                                         |
| **Max pool size**      | The hard ceiling on concurrent connections — protects the database from being overwhelmed by more simultaneous connections than it (or its licensing/resource limits) can handle                              |
| **Idle timeout**       | How long an unused connection stays open before being closed, freeing resources during quiet periods                                                                                                          |
| **Connection timeout** | How long a request will wait for a free connection before giving up — if every connection is busy and the pool is at max size, new requests queue up to this limit                                            |
| **Max lifetime**       | Forces even a healthy connection to be recycled periodically, guarding against subtle long-lived-connection issues (stale [DNS](../../networking/dns.md)/load-balancer routing, memory growth on the DB side) |

```javascript
// node-postgres (pg) pool example
const { Pool } = require('pg');
const pool = new Pool({
  host: 'db.example.com',
  max: 20,               // max concurrent connections
  idleTimeoutMillis: 30000,
  connectionTimeoutMillis: 2000,
});

const result = await pool.query('SELECT * FROM users WHERE id = $1', [id]);
// the pool automatically borrows a connection, runs the query, and returns it
```

## Why Max Pool Size Isn't "Bigger Is Always Better"

It's tempting to assume a larger pool always helps under load, but a database has finite CPU, memory, and lock capacity — beyond a certain point, more concurrent connections just means more contention for the same underlying resources, and can make overall throughput *worse*, not better, as the database spends more time context-switching between connections than doing actual work. A commonly cited (though workload-dependent) rule of thumb: the optimal pool size is often surprisingly small, closer to `(number of CPU cores × 2) + effective spindle count` for the database server, not the number of application instances or expected concurrent users.

## Pooling at Two Levels: Application vs. External Pooler

|                   | Application-level pooling                | External connection pooler                                                                                                                                                              |
| ----------------- | ---------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Where it runs     | Inside each application process/instance | A separate service between the application and database (e.g. **[PgBouncer](pgbouncer.md)** for [PostgreSQL](postgresql.md))                                                            |
| Problem it solves | Reuse within one application instance    | Reuse *across* many application instances/servers, which each having their own in-process pool would otherwise multiply into far more total DB connections than the database can handle |
| Common when       | A single service, moderate scale         | Many service instances (microservices, serverless functions each opening their own connections) hitting one database                                                                    |

This distinction matters a lot for serverless/lambda-style backends, where each function invocation could otherwise open its own fresh connection — with high concurrency, that alone can exhaust a database's max-connection limit; an external pooler sitting in front absorbs that fan-out.

An external pooler doesn't have to be self-hosted, either — most managed database providers now offer [managed connection pooling](managed-connection-pooling.md) as a built-in feature or add-on service ([AWS](../../cloud/infrastructure/aws.md) RDS Proxy, Supabase's Supavisor, Neon's and [Azure](../../cloud/azure/azure.md)'s built-in [PgBouncer](pgbouncer.md)), trading some control over pooling configuration for not having to operate the pooler yourself.

## Connection Pooling and ORMs

Most [ORMs](../../backend/data/orm.md) manage a connection pool internally and expose its size as a configuration option (`connection_limit` in Prisma, `pool` options in TypeORM/Sequelize) — a common production issue is leaving this at a default that's mismatched with the actual database's connection limit or the number of running application instances, leading to either connection exhaustion under load or unnecessarily idle connections sitting unused.

## Common Questions

**Why not just open a new connection per query and let the OS handle it?**
> Connection establishment ([TCP](../../networking/tcp.md) handshake, [TLS](../../networking/tls.md), auth) is orders of magnitude slower than a typical fast query — under any real concurrent load, paying that cost per query would dominate total latency and could exhaust the database's own connection-handling capacity long before it becomes a query-throughput problem.

**What happens when every connection in the pool is busy and a new request comes in?**
> It waits, up to the pool's configured connection timeout — if a free connection doesn't become available in time, the request fails with a timeout error rather than waiting indefinitely. This is a deliberate signal that the pool is undersized (or the database itself is the actual bottleneck) rather than a bug to silently work around by just raising the timeout.

**Does connection pooling help with database-side query performance too?**
> Not directly — pooling only removes connection-*setup* overhead. A slow query is still slow regardless of how the connection running it was obtained; that's a separate problem addressed by [indexing](indexing.md), query optimization, and [read replicas](read-replicas.md) for read-heavy scaling.

## Related

- [ORM](../../backend/data/orm.md)
- [Read Replicas](read-replicas.md)
- [The N+1 Query Problem](../../backend/data/n-plus-1-problem.md)
- [PostgreSQL](postgresql.md) — the database most commonly fronted by an external pooler in this ecosystem
- [PgBouncer](pgbouncer.md) — the canonical external connection pooler for [PostgreSQL](postgresql.md), the concrete example of the "external pooler" row above
- [Managed Connection Pooling](managed-connection-pooling.md) — the provider-operated variant of the "external pooler" row above, used instead of self-hosting [PgBouncer](pgbouncer.md) or an equivalent
- [Singleton](../../programming/design-patterns/singleton.md) — the design pattern a shared pool is a real-world instance of
- [Python Assistant API Deep Dive](../../../interview/interview-01/20-python-assistant-api-deep-dive.md) — a worked example applying this same pattern to a shared [HTTP](../../networking/http.md) client, not just a database
- [Database Scaling Strategies](../../../overviews/databases/database-scaling-strategies.md) — the overview placing connection pooling as the first, cheapest rung on the broader database-scaling ladder
