# API Versioning

API versioning is the practice of evolving an API's contract over time without breaking clients that are still using an older version — giving a service a way to change shape while existing consumers keep working exactly as before, until they choose to migrate.

## Why It's Needed

Once an API has real external consumers (a mobile app that can't be force-updated instantly, a third-party integration, another team's service), you can't simply change a response shape or remove a field — anything already depending on the old contract breaks. Versioning gives you a controlled way to introduce breaking changes alongside the still-working old behavior, rather than never being able to change anything at all.

## What Counts as a Breaking Change

| Breaking (needs a new version) | Non-breaking (safe to ship into the existing version) |
|---|---|
| Removing a field from a response | Adding a new optional field |
| Renaming a field | Adding a new endpoint |
| Changing a field's type (`string` → `number`) | Adding a new optional query parameter |
| Changing required request parameters | Relaxing a previously required field to optional |
| Changing status codes/error shapes for existing behavior | Fixing a bug that only affects already-broken/undocumented behavior |

A useful discipline: if any well-behaved existing client's code could start failing or misbehaving because of the change, it's breaking.

## The Main Versioning Strategies

| Strategy | Example | Trade-off |
|---|---|---|
| **URI path versioning** | `/v1/users`, `/v2/users` | Most explicit and cache-friendly (different URLs cache independently); clutters the URL space, and "the resource" arguably shouldn't include its version in its identity |
| **Query parameter** | `/users?version=2` | Easy to default (omit = latest), but easy to overlook and less RESTfully "clean" |
| **Custom header** | `Accept-Version: 2` or `X-API-Version: 2` | Keeps URLs clean/stable; less discoverable (you can't just look at a URL to know the version), harder to test by pasting a URL into a browser |
| **Content negotiation (`Accept` header)** | `Accept: application/vnd.myapi.v2+json` | The most "RESTfully correct" approach per [HTTP](../../networking/http.md)'s own content-negotiation mechanism; more complex to implement and less obvious to API consumers unfamiliar with the convention |

In practice, **URI path versioning is by far the most common** in real-world public APIs (Stripe, GitHub, Twitter/X have all used variations of it) precisely because of its simplicity and discoverability, even though header-based negotiation is arguably more "correct" per [REST](rest.md)'s own principles.

## Example: Path-Based Versioning (NestJS)

```typescript
@Controller({ path: 'users', version: '1' })
export class UsersV1Controller {
  @Get()
  findAll() {
    return this.usersService.findAllLegacyShape();
  }
}

@Controller({ path: 'users', version: '2' })
export class UsersV2Controller {
  @Get()
  findAll() {
    return this.usersService.findAllWithPagination();
  }
}
```

```typescript
app.enableVersioning({ type: VersioningType.URI }); // → /v1/users, /v2/users
```

## GraphQL's Different Approach: No Versioning at All

[GraphQL](graphql.md) sidesteps this problem largely by convention rather than solving it differently: fields are additive by default (a client only receives fields it explicitly requests, so adding new fields is always safe), and fields are marked `@deprecated` with a reason rather than removed outright, giving clients time to migrate off them before an eventual cleanup. This is one of [GraphQL](graphql.md)'s real advantages over versioned [REST](rest.md) APIs for long-lived, evolving schemas — though it requires discipline (never actually changing an existing field's meaning/type) to hold up in practice.

## Deprecation, Not Just Versioning

Shipping a new version doesn't remove the obligation to eventually retire the old one — a responsible API lifecycle includes:

1. Ship `v2` alongside the still-working `v1`.
2. Communicate a deprecation timeline for `v1` (changelog, `Deprecation`/`Sunset` [HTTP](../../networking/http.md) headers, direct outreach to known consumers).
3. Monitor actual `v1` traffic to know when it's safe to remove.
4. Remove `v1` only once traffic has genuinely dropped to zero (or an acceptable, explicitly accepted risk).

```http
HTTP/1.1 200 OK
Deprecation: true
Sunset: Sat, 31 Dec 2026 23:59:59 GMT
Link: <https://api.example.com/v2/users>; rel="successor-version"
```

## How Many Versions Should Exist at Once?

Supporting too many concurrent versions multiplies maintenance burden (bug fixes, security patches, and feature work potentially need to land in every supported version). Most mature APIs cap themselves at supporting two versions at a time — current and previous — with an explicit, communicated sunset window for anything older, rather than accumulating an ever-growing set of live versions indefinitely.

## Common Questions

**Does adding a new required field to an existing endpoint count as a breaking change?**
> Yes — any existing client that doesn't know to send the new required field will start failing. Making it optional (with a sensible default when absent) is the non-breaking alternative.

**Why do so many major APIs use URI path versioning despite header-based negotiation being more "RESTfully pure"?**
> Discoverability and simplicity win in practice — a version visible directly in the URL is trivial to document, test with a browser or curl, route with infrastructure-level rules (a [reverse proxy](../../networking/reverse-proxy.md) can route `/v1/*` and `/v2/*` to entirely different backend deployments), and reason about without reading documentation about custom headers first.

**Is semantic versioning (`v1.2.3`) the same thing as API versioning?**
> Not quite the same concept — semantic versioning is a convention for communicating the *nature* of a change (major.minor.patch) in a package or library release. API versioning as discussed here is almost always coarser (just `v1`, `v2`) because the goal is "which contract shape is this request targeting," not tracking every incremental change.

## Related

- [REST](rest.md)
- [GraphQL](graphql.md)
- [HTTP Status Codes](http-status-codes.md)
- [Pagination](pagination.md)
