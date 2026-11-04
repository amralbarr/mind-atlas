# Caching Strategies

Caching stores a copy of expensive-to-produce data somewhere faster to read than its original source, so repeat requests for the same data can be served without redoing the original work (a database query, an expensive computation, a call to a slow third-party API). The hard part isn't storing the copy — it's deciding *when* to populate it, *when* to update it, and *when* to throw it away.

## Cache-Aside (Lazy Loading)

The most common pattern: the application checks the cache first, and only goes to the source of truth (usually a database) on a miss — then writes the result back to the cache for next time.

```javascript
async function getUser(id) {
  const cached = await redis.get(`user:${id}`);
  if (cached) return JSON.parse(cached);

  const user = await db.query('SELECT * FROM users WHERE id = $1', [id]);
  await redis.set(`user:${id}`, JSON.stringify(user), 'EX', 300); // 5 min TTL
  return user;
}
```

| Pros | Cons |
|---|---|
| Only caches data that's actually requested (no wasted cache space) | First request after a miss/expiry always pays the full latency ("cache stampede" risk if many requests miss simultaneously) |
| Cache and database can fail independently — a cache outage just means more DB load, not total failure | The application owns cache-population logic — more code than a strategy the cache layer handles automatically |

Cache-aside is the default choice for read-heavy workloads where not every piece of data is equally hot.

## Write-Through

The application writes to the cache *and* the database in the same operation, keeping them always in sync:

```javascript
async function updateUser(id, data) {
  await db.query('UPDATE users SET ... WHERE id = $1', [id]);
  await redis.set(`user:${id}`, JSON.stringify(data), 'EX', 300);
}
```

| Pros | Cons |
|---|---|
| Cache is never stale — every write immediately updates it | Every write pays the latency cost of writing to both stores |
| Reads after a write are always fast and correct | Wastes effort caching data that might never be read again |

## Write-Behind (Write-Back)

The application writes to the cache immediately and returns, while the database write happens asynchronously (batched or queued) shortly after:

```text
Write → Cache (fast, synchronous)
             ↓
        Queue → Database (async, batched)
```

| Pros | Cons |
|---|---|
| Very low write latency from the caller's perspective | A cache failure before the async flush completes can lose data — a real durability risk |
| Can batch/coalesce many writes into fewer database operations | Meaningfully more complex to implement correctly (ordering, retry, failure handling) |

Write-behind trades durability guarantees for write speed — appropriate for high-write-volume data where occasional loss is tolerable (e.g. view counters, analytics events), rarely appropriate for anything transactional.

## Read-Through

Similar to cache-aside, but the cache layer itself (not the application) is responsible for loading from the source on a miss — the application only ever talks to the cache, which transparently populates itself behind the scenes. This requires a caching layer that supports a configured loader function; cache-aside is the same idea implemented explicitly in application code when the caching layer doesn't support this natively.

## TTL (Time to Live)

Every cached entry should generally expire — an unbounded cache is both a memory leak risk and a correctness risk (permanently stale data). Choosing a TTL is a real trade-off:

```text
Short TTL  → fresher data, more cache misses, more load on the source
Long TTL   → fewer misses, better performance, staler data window
```

The right TTL depends entirely on how often the underlying data actually changes and how tolerant the use case is of staleness — a product catalog might tolerate minutes of staleness; a user's current account balance might not tolerate any.

## Eviction Policies

When a cache is full and needs to make room for a new entry, an eviction policy decides what to remove:

| Policy | Removes |
|---|---|
| **LRU (Least Recently Used)** | The entry that hasn't been accessed in the longest time — the most common default (assumes recently used data is likely to be used again) |
| **LFU (Least Frequently Used)** | The entry accessed the fewest total times — better than LRU when access frequency matters more than recency |
| **FIFO** | The oldest entry by insertion time, regardless of access pattern — simplest, rarely optimal |
| **TTL-based expiry** | Not really an eviction *policy* under memory pressure, but a complementary mechanism — entries are removed once their TTL elapses regardless of memory pressure |

Most production caching systems (Redis with `maxmemory-policy`, [CDN](../../networking/cdn.md) edge caches) default to some form of LRU because it's a reasonable, low-cost approximation of "what's likely to be needed again."

## Cache Invalidation

> "There are only two hard things in computer science: cache invalidation and naming things."

Invalidation — actively removing or updating a cache entry when the underlying data changes, rather than waiting for TTL expiry — is the genuinely hard part. Common approaches:

- **Invalidate on write** — the same code path that updates the database explicitly deletes/updates the corresponding cache key (what write-through does automatically; cache-aside must do this manually).
- **Event-driven invalidation** — a change event (e.g. published via [Kafka](../../distributed-systems/messaging/kafka.md) or a [webhook](../api/webhooks.md)) triggers cache invalidation in other services that don't own the write path directly.
- **Versioned/keyed cache entries** — rather than invalidating, change the cache key itself when the underlying version changes (e.g. `user:42:v3`), so old entries simply age out via TTL without needing an active delete.

## Where Caching Happens

Caching isn't one layer — real systems cache at several levels simultaneously:

| Layer | Example |
|---|---|
| Browser | [HTTP](../../networking/http.md) `Cache-Control` headers caching static assets client-side |
| [CDN](../../networking/cdn.md) | Edge caching of static/cacheable responses close to the user |
| [Reverse proxy](../../networking/reverse-proxy.md) | [NGINX](../api-gateways/nginx.md) caching upstream responses |
| Application | Redis/Memcached caching database query results or computed values |
| Database | The database's own internal query/buffer cache |

## Common Questions

**When should you reach for write-through instead of cache-aside?**
> When reads immediately following a write must always be fast and correct, and the extra write latency is acceptable — e.g. a user's profile page that's read constantly right after being edited. Cache-aside is the better default otherwise, since it avoids caching data that's never actually read.

**What's a "cache stampede," and how is it prevented?**
> When a popular cache entry expires and many concurrent requests all miss at once, all hammering the database simultaneously to repopulate it. Common mitigations: a short lock/mutex around the recompute step (only one request repopulates, others wait briefly), or proactively refreshing hot entries just before they expire instead of waiting for a hard miss.

**Is a longer TTL always safer than a shorter one?**
> No — it just trades one risk for another. A longer TTL reduces load on the source but widens the window during which cached data can be visibly stale; the right choice depends on how tolerant the specific data is of being out of date.

## Related

- [Redis Lists](../../distributed-systems/messaging/redis-lists.md)
- [CDN](../../networking/cdn.md)
- [NGINX](../api-gateways/nginx.md)
- [Rate Limiting](rate-limiting.md)
- [Webhooks](../api/webhooks.md)
