# DNS (Domain Name System)

DNS translates human-readable domain names (`example.com`) into the IP addresses computers actually use to route traffic — effectively the internet's phone book, and one of the first things that happens before any [HTTP](http.md) request can even be sent.

## Resolution Steps (Simplified)

```text
Browser needs example.com's IP
   ↓
Check local cache (browser, OS) — if found and not expired, done
   ↓
Ask a Recursive Resolver (often the ISP's, or a public one like 1.1.1.1/8.8.8.8)
   ↓
Resolver asks a Root Server → "who handles .com?"
   ↓
Resolver asks the .com TLD Server → "who handles example.com?"
   ↓
Resolver asks example.com's Authoritative Nameserver → "what's the IP?"
   ↓
Answer flows back down and gets cached at each level along the way
```

In practice, caching at the browser, OS, and resolver level means this full chain rarely runs on every lookup — it's the fallback path when nothing cached is still valid.

## Common Record Types

| Record | Purpose |
|---|---|
| `A` | Maps a domain to an IPv4 address |
| `AAAA` | Maps a domain to an IPv6 address |
| `CNAME` | Aliases one domain to another (e.g. `www.example.com` → `example.com`) |
| `MX` | Specifies mail servers responsible for the domain |
| `TXT` | Arbitrary text — commonly used for domain ownership verification and email anti-spoofing (SPF/DKIM/DMARC) |
| `NS` | Specifies which nameservers are authoritative for the domain |

## TTL and Propagation Delay

Every DNS record has a **TTL** (time-to-live) telling resolvers how long to cache it before re-checking. This is why DNS changes (pointing a domain at a new server, updating a subdomain) don't take effect everywhere instantly — every resolver that already cached the old value keeps serving it until that TTL expires. Lowering a record's TTL *before* a planned change (so the old, short-lived value expires everywhere quickly once the change is made) is a common practice ahead of a migration or cutover.

## Why This Matters Beyond "Just Making Domains Work"

- **[CDN](cdn.md) routing** — a [CDN](cdn.md) (see [CDN](cdn.md)) often works by having DNS resolve to the *nearest* edge server's IP based on the requester's location, making DNS itself part of the performance/routing strategy, not just a lookup step.
- **Latency** — a DNS lookup adds real time before a connection can even begin; this is part of why keeping a connection alive/reused (see [HTTP](http.md), [TCP](tcp.md)) avoids paying that cost on every single request to the same host.
- **Outage blast radius** — because so much infrastructure depends on DNS resolving correctly, a DNS provider outage can make an otherwise-healthy service completely unreachable, even though the service's own servers are running fine.

## Common Questions

**Why can a domain still resolve to an old IP hours after being updated?**
> Cached TTLs at various resolvers along the chain haven't expired yet — this is expected behavior, not a misconfiguration, and is why DNS changes are usually planned with propagation delay in mind rather than assumed to be instant.

**Is DNS itself encrypted?**
> Traditionally no — plain DNS queries are sent unencrypted, which is one of the metadata leaks possible even over an otherwise-[HTTPS](https.md) connection (see [HTTPS](https.md)). DNS-over-[HTTPS](https.md) (DoH) and DNS-over-[TLS](tls.md) (DoT) are newer standards that encrypt the query itself, though adoption varies by resolver and client.

## Related

- [dig Commands](../../commands/dig.md)
- [HTTP](http.md)
- [HTTPS](https.md)
- [CDN](cdn.md)
- [TCP](tcp.md)
