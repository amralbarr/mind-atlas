# MongoDB

MongoDB is a distributed document database — data is stored as [JSON](../../programming/fundamentals/json.md)-like documents (BSON) with a flexible schema, and it scales horizontally through built-in replication and [sharding](../distributed/sharding.md) rather than requiring a bolted-on clustering layer. See [Distributed Databases](../distributed/distributed-databases.md) for how it compares to distributed [SQL](../relational/sql.md) and other NoSQL options.

## Core Concepts

| Term | Meaning |
|---|---|
| **Document** | A single record, stored as BSON (binary [JSON](../../programming/fundamentals/json.md)) — fields can vary between documents in the same collection, unlike a fixed [SQL](../relational/sql.md) schema |
| **Collection** | A group of documents — roughly analogous to a [SQL](../relational/sql.md) table, but without an enforced schema by default |
| **Replica set** | A primary node plus secondary nodes holding copies of the same data — writes go to the primary, reads can be served from secondaries, and a secondary is automatically promoted if the primary fails |
| **Shard** | A subset of a collection's data, held on one shard server — [sharding](../distributed/sharding.md) splits (not copies) data across multiple servers for horizontal scale |
| **Shard key** | The field(s) MongoDB uses to decide which shard a given document belongs to — chosen carefully, since a poor shard key creates uneven load across shards |

## Replica Sets (High Availability)

```text
Primary (accepts writes) ──replicates──► Secondary 1
                          ──replicates──► Secondary 2

If Primary fails → an election promotes a Secondary to Primary automatically
```

```javascript
// Connecting with a replica set-aware connection string
const client = new MongoClient(
  "mongodb://host1:27017,host2:27017,host3:27017/?replicaSet=rs0"
);
```

## Sharding (Horizontal Scale)

```text
Shard 1 → Users A-F
Shard 2 → Users G-M
Shard 3 → Users N-Z
```

```javascript
sh.shardCollection("myapp.users", { userId: "hashed" });
```

A **hashed** shard key spreads documents evenly across shards regardless of the underlying value's natural distribution — a common choice when the field itself (e.g. a sequential ID) would otherwise concentrate load on one shard.

## Basic CRUD (Node.js Driver)

```javascript
const db = client.db("myapp");
const users = db.collection("users");

await users.insertOne({ name: "Amr", role: "engineer" });
const user = await users.findOne({ name: "Amr" });
await users.updateOne({ name: "Amr" }, { $set: { role: "senior engineer" } });
```

## Common Questions

**Does MongoDB's flexible schema mean no structure at all?**
> Not in practice — most production MongoDB usage still enforces structure at the application layer (via an [ORM](../../backend/data/orm.md)/ODM like Mongoose, or MongoDB's own [JSON](../../programming/fundamentals/json.md) Schema validation), it's just not a rigid, migration-gated schema the database itself enforces the way [SQL](../relational/sql.md) does. The flexibility is most valuable for evolving schemas or genuinely variable document shapes.

**What consistency model does MongoDB use?**
> Reads from the primary are strongly consistent by default; reads from secondaries can return slightly stale data depending on configured read preference/concern — see [Distributed Databases](../distributed/distributed-databases.md#consistency) for the general strong-vs-[eventual consistency](../../distributed-systems/patterns/eventual-consistency.md) tradeoff this reflects.

## Related

- [Distributed Databases](../distributed/distributed-databases.md)
- [Cassandra](cassandra.md)
- [ACID](../relational/acid.md)
- [ORM](../../backend/data/orm.md)
