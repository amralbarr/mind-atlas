# Module: Databases & Caching

**Category:** Backend · **Typical duration:** 2 weeks (15–20 hrs/week) · **Prerequisite modules:** [Programming Fundamentals](../foundations/programming-fundamentals.md)

## Goal

Model and query data correctly in a relational database, know when a document store or cache fits better, and avoid the classic data-layer mistakes (N+1 queries, missing indexes, cache stampedes).

## Core topics

- [ ] [SQL](../../../engineering/concepts/databases/relational/sql.md): SELECT/JOIN/GROUP BY, indexes, transactions, normalization
- [ ] An [ORM](../../../engineering/concepts/backend/data/orm.md) and its migration tool for your stack
- [ ] A document/NoSQL store, and when it beats a relational one
- [ ] Caching: TTLs, invalidation strategies, cache-aside pattern, [pub/sub](../../../engineering/concepts/distributed-systems/messaging/publish-subscribe.md)
- [ ] Full-text/vector search basics, if the job touches search or retrieval
- [ ] [Connection pooling](../../../engineering/concepts/databases/relational/connection-pooling.md), [read replicas](../../../engineering/concepts/databases/relational/read-replicas.md), and when to reach for them

## Resources

- An interactive free SQL tutorial, then your chosen database's own official docs
- Your ORM's migration-tool docs
- A caching library's own "introduction to caching" guide

## Milestone deliverable

Add a persistence layer to the [APIs & Backend Services](apis-and-services.md) milestone project: a normalized schema with migrations, plus a caching layer for at least one expensive read path.

## Related concepts

SQL, [PostgreSQL](../../../engineering/concepts/databases/relational/postgresql.md), Indexing, ORM, [MongoDB](../../../engineering/concepts/databases/nosql/mongodb.md), [Caching Strategies](../../../engineering/concepts/backend/architecture/caching-strategies.md), [Elasticsearch](../../../engineering/concepts/databases/search/elasticsearch.md)
