# Pagination

Pagination splits a large result set into smaller chunks ("pages") returned one request at a time, instead of sending an entire table's worth of rows back in a single response — necessary both for performance (a query and payload of unbounded size doesn't scale) and for usability (a client rarely needs a million rows rendered at once).

## Offset-Based Pagination

The client asks for a page by specifying how many rows to skip and how many to return:

```http
GET /orders?offset=40&limit=20
```

```sql
SELECT * FROM orders ORDER BY created_at DESC LIMIT 20 OFFSET 40;
```

| Pros | Cons |
|---|---|
| Simple to implement and understand | `OFFSET` gets progressively slower on large tables — the database must still scan and discard every skipped row before it can start returning results |
| Client can jump directly to an arbitrary page (`page=50`) | Unstable under concurrent writes: if a row is inserted/deleted between page requests, the client can see duplicate or skipped rows (the whole result set shifts under the offset) |

Offset pagination is fine for smallish, relatively static datasets (an admin dashboard with a few thousand rows) but degrades badly and becomes correctness-risky at real scale.

## Cursor-Based (Keyset) Pagination

Instead of a page number, the client passes an opaque cursor pointing to *where it left off* — typically derived from the last item's sort key:

```http
GET /orders?limit=20&cursor=eyJpZCI6MTIzLCJjcmVhdGVkX2F0IjoiMjAyNi0wOS0wMSJ9
```

```sql
SELECT * FROM orders
WHERE created_at < '2026-09-01' OR (created_at = '2026-09-01' AND id < 123)
ORDER BY created_at DESC, id DESC
LIMIT 20;
```

The cursor encodes the last row's sort-key values, so the query can jump straight to "everything after this point" using an index, without scanning and discarding earlier rows.

| Pros | Cons |
|---|---|
| Consistent performance regardless of how deep into the dataset you are — no growing `OFFSET` to scan past | Can't jump to an arbitrary page number (`page=50`) — only "next" and "previous" relative to a cursor |
| Stable under concurrent writes — new rows inserted don't shift already-fetched pages | Slightly more complex to implement (encoding/decoding cursors, composite sort keys for tie-breaking) |
| Scales to very large datasets — this is what most high-scale APIs (Twitter/X, Slack, Stripe) actually use | The cursor is opaque, so the client can't compute it themselves — it must always come from the previous response |

The tie-breaking column (`id` in the example above) matters: sorting by `created_at` alone breaks if two rows share the exact same timestamp — the secondary key on a genuinely unique column guarantees a stable, total order.

## Page-Number Pagination (a UI-Facing Variant of Offset)

```http
GET /orders?page=3&per_page=20
```

This is really offset pagination with a friendlier API shape (`page` × `per_page` computes the same `OFFSET`/`LIMIT` internally) — it shares offset pagination's exact performance and consistency trade-offs, just with a more human-readable parameter for building page-number UI controls (`1 2 3 ... 10`).

## Comparison

| | Offset / Page Number | Cursor / Keyset |
|---|---|---|
| Jump to arbitrary page | Yes | No — sequential only |
| Performance on large tables | Degrades with depth (`OFFSET` cost grows) | Consistent regardless of depth |
| Stable under concurrent inserts/deletes | No — results can shift | Yes |
| Implementation complexity | Low | Moderate |
| Typical use | Admin UIs, small-to-medium datasets, "jump to page N" needs | Infinite scroll, activity feeds, high-scale public APIs |

## GraphQL's Cursor Convention: Relay-Style Connections

[GraphQL](graphql.md) formalized cursor pagination into a widely adopted convention:

```graphql
query {
  orders(first: 20, after: "cursor123") {
    edges {
      cursor
      node { id, total }
    }
    pageInfo {
      hasNextPage
      endCursor
    }
  }
}
```

`first`/`after` (forward) and `last`/`before` (backward) pagination arguments, plus a `pageInfo` block reporting whether more pages exist — this shape is common enough across [GraphQL](graphql.md) APIs that it's often just assumed rather than re-designed per API.

## Common Questions

**Why does `OFFSET` get slower the deeper you paginate?**
> Most databases implement `OFFSET` by scanning and discarding rows from the start of the result set until reaching the offset, then returning the next `LIMIT` rows — so `OFFSET 100000` genuinely does more work than `OFFSET 100`, even though both return the same number of final rows.

**If cursor pagination is better at scale, why does anything still use offset pagination?**
> Offset pagination supports jumping directly to an arbitrary page number, which some UIs genuinely need (page-number controls, "go to page 7"). Cursor pagination only supports moving forward/backward relative to a known position — a real feature trade-off, not just a legacy habit.

**Is a cursor the same thing as the row's [primary key](../../databases/relational/primary-key.md)?**
> Often derived from it (or from the sort key plus [primary key](../../databases/relational/primary-key.md) as a tie-breaker), but typically base64-encoded or otherwise opaque so the client treats it as an opaque token rather than relying on its internal structure — this also gives the API room to change what the cursor encodes internally without breaking clients.

## Related

- [REST](rest.md)
- [GraphQL](graphql.md)
- [API Versioning](api-versioning.md)
- [Database Indexing](../../databases/relational/indexing.md)
