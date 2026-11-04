# Managed Connection Pooling

Managed connection pooling is when the database **provider itself** runs and operates the pooling layer — a managed service or a built-in feature of the managed database — instead of the application team standing up and operating their own [external pooler](connection-pooling.md) like [PgBouncer](pgbouncer.md). The pattern solves the exact same problem as self-hosted pooling (too many application instances/serverless invocations opening too many real database connections), but the pooler process itself is provisioned, scaled, patched, and kept highly available by the provider rather than by whoever runs the application.

## Where It Shows Up

| Provider | What it offers | Underlying mechanism |
|---|---|---|
| **[AWS](../../cloud/infrastructure/aws.md)** | [RDS Proxy](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/rds-proxy.html) — a fully managed, highly available proxy in front of [RDS](postgresql.md)/Aurora | Proprietary [AWS](../../cloud/infrastructure/aws.md) proxy; pools and multiplexes connections per transaction by default, with IAM auth integration and automatic failover handling |
| **Supabase** | A built-in pooler reachable on a separate port, backed by [Supavisor](https://github.com/supabase/supavisor) (their own cloud-native, multi-tenant pooler, which replaced an earlier [PgBouncer](pgbouncer.md)-based setup) | Supavisor is written in Elixir, built for multi-tenancy, and can scale to very high connection counts (Supabase has publicly benchmarked it at roughly a million client connections on one cluster) while running at close to [PgBouncer](pgbouncer.md)'s throughput |
| **Neon** | Every Neon compute includes a managed [PgBouncer](pgbouncer.md) pooler automatically — reached by appending `-pooler` to the connection hostname | Literally [PgBouncer](pgbouncer.md) itself, just operated by Neon rather than self-deployed; defaults to transaction-pooling mode |
| **Google Cloud [SQL](sql.md)** | Managed Connection Pooling — a newer, opt-in server-side pooling layer that sits between clients and the database server | Google-operated pooler cluster; historically Cloud [SQL](sql.md) relied on client-side pooling only (via the driver/[ORM](../../backend/data/orm.md), often alongside the Cloud [SQL](sql.md) Auth Proxy, which itself does not pool) |
| **[Azure](../../cloud/azure/azure.md) Database for [PostgreSQL](postgresql.md) (Flexible Server)** | Built-in [PgBouncer](pgbouncer.md), enabled as an optional per-server feature, reachable on port 6432 | Also literally [PgBouncer](pgbouncer.md), defaulting to transaction-pooling mode, with a default pool size of 50 server connections per user/database pair |

A recurring detail worth noticing: several of these "managed poolers" are not a novel pooling technology at all — Neon's and [Azure](../../cloud/azure/azure.md)'s offerings are [PgBouncer](pgbouncer.md) itself, just operated on the customer's behalf. Supabase's Supavisor and [AWS](../../cloud/infrastructure/aws.md)'s RDS Proxy are the exceptions, each a purpose-built proxy with its own implementation rather than a hosted [PgBouncer](pgbouncer.md) instance.

## Managed Pooling vs. Self-Hosting PgBouncer

| | Managed pooling | Self-hosted pooler (e.g. [PgBouncer](pgbouncer.md)) |
|---|---|---|
| **Operational burden** | None — the provider provisions, patches, monitors, and fails it over | The application team owns deployment, upgrades, monitoring, and failover of the pooler process itself |
| **Scaling / HA** | Handled by the provider, often transparently (e.g. RDS Proxy automatically routes around a failed database instance; Supavisor's cluster scales independently of any one database) | The team must run the pooler itself in a highly-available configuration (multiple instances behind a load balancer, or accept it as a single point of failure) |
| **Control over pooling mode/config** | Limited to whatever knobs the provider exposes — [Azure](../../cloud/azure/azure.md) and Neon expose basic [PgBouncer](pgbouncer.md) settings like pool size and mode, but not the full `pgbouncer.ini` surface; RDS Proxy and Supavisor expose their own more opinionated config surface | Full control — every [PgBouncer](pgbouncer.md) setting (`pool_mode`, `max_client_conn`, per-database pool sizes, auth methods, `server_reset_query`, etc.) is available to tune |
| **Vendor lock-in** | Tied to that specific managed database offering — migrating off the provider (or even just moving from, say, Cloud SQL to self-managed Postgres on a VM) means losing the pooling layer too and having to stand up a replacement | Portable — the same [PgBouncer](pgbouncer.md) config and deployment pattern works in front of any [PostgreSQL](postgresql.md) instance, self-hosted or managed, on any cloud |
| **Cost** | Usually a separate line item on top of the database itself — RDS Proxy, for example, bills per vCPU-hour of the underlying database (around $0.015/vCPU-hour in US East as of this writing, with a 2-vCPU minimum), so an 8-vCPU database pays roughly $85-90/month just for the proxy | Infra cost of running the pooler's own small compute footprint (often negligible — [PgBouncer](pgbouncer.md) is lightweight enough to run on a small instance or even a sidecar container), but that cost is visible and controlled directly rather than billed by the provider |
| **Operational visibility** | Limited to whatever metrics/logs the provider surfaces through its own console/CloudWatch-equivalent | Full access to the pooler's own logs, `SHOW POOLS`/`SHOW STATS` admin console, and metrics scraping |

## When Teams Reach for Managed Pooling

Managed pooling tends to win when the team is already deep in one provider's managed-database ecosystem and wants one less piece of infrastructure to operate — serverless/edge workloads in particular (Neon, Supabase) are built around the assumption that every function invocation can safely open a pooled connection with zero pooler of their own to run. It's also attractive when the team lacks the operational capacity or expertise to run [PgBouncer](pgbouncer.md) itself reliably, or when the provider's managed option (like RDS Proxy's IAM-integrated auth and automatic failover routing) adds capabilities a self-hosted pooler wouldn't have for free.

Self-hosting [PgBouncer](pgbouncer.md) (or an equivalent) still wins when the team needs full control over pooling mode and configuration details the managed option doesn't expose, is running on infrastructure that spans providers or includes self-managed [PostgreSQL](postgresql.md), wants to avoid the extra per-vCPU or per-instance cost of a managed proxy, or is sensitive to adding another vendor-specific dependency that complicates a future migration. In practice, many teams on AWS specifically weigh RDS Proxy's convenience against just running their own [PgBouncer](pgbouncer.md) container next to the application — a self-hosted instance is often cheaper and more configurable, at the cost of someone owning its uptime.

## Common Questions

**If a managed pooler like Neon's or Azure's is literally [PgBouncer](pgbouncer.md) underneath, what's actually different from self-hosting it?**
> Who operates it. The pooling mode, multiplexing behavior, and the session-state caveats of transaction pooling (`SET`, prepared statements, `LISTEN`/`NOTIFY`, session-scoped temp tables — see [PgBouncer](pgbouncer.md)'s own notes on this) are identical either way, since it's the same software. The difference is entirely operational: provisioning, scaling, patching, and failover become the provider's job instead of the application team's.

**Does using a provider's managed pooler remove the need for an application-level pool too?**
> No — exactly as with self-hosted [PgBouncer](pgbouncer.md), the application (or its [ORM](../../backend/data/orm.md)/driver) typically still keeps its own small in-process pool, just pointed at the managed pooler's endpoint instead of the database's direct endpoint. The managed pooler's job is collapsing fan-out across many application instances/invocations, not replacing pooling at the application layer.

**Why would a team pick RDS Proxy over just running [PgBouncer](pgbouncer.md) on AWS themselves?**
> Mainly for the pieces a self-hosted pooler doesn't give for free on RDS/Aurora specifically: automatic failover awareness (RDS Proxy keeps serving connections and reroutes them during a primary failover without the application needing to reconnect), IAM-based [authentication](../../security/auth/authentication.md) instead of managing pooler-level credentials separately, and not having to run and patch the proxy process themselves. The tradeoff is the per-vCPU-hour cost and less granular control than a `pgbouncer.ini` would offer.

## Related

- [Connection Pooling](connection-pooling.md) — the general concept (why pooling exists, application-level vs. external pooler) that this note specializes to the provider-managed case
- [PgBouncer](pgbouncer.md) — the self-hosted pooler this note contrasts against, and literally the software underneath Neon's and Azure's "managed" offerings
- [PostgreSQL](postgresql.md) — the database most of these managed poolers (RDS Proxy for Aurora/RDS Postgres, Supavisor, Neon's pooler, Azure's built-in [PgBouncer](pgbouncer.md)) sit in front of
- [Read Replicas](read-replicas.md) — another provider-operated scaling feature often offered alongside managed pooling, addressing read throughput rather than connection count
