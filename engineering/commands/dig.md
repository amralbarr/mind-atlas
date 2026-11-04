# dig Commands

`dig` (Domain Information Groper) is the standard command-line tool for querying [DNS](../concepts/networking/dns.md) directly — resolving a hostname, inspecting specific record types, and diagnosing propagation or misconfiguration issues without going through a browser or any caching layer you don't control.

## Basic Lookup

```bash
dig example.com                  # full, verbose output — the ANSWER SECTION has what you actually want
dig example.com +short           # just the resolved IP(s), nothing else — the one to use in scripts
```

**`dig` takes a bare hostname — never a URL.** `dig https://example.com` doesn't strip the scheme for you; it queries for a (nonexistent) domain literally named `https://example.com` and returns `NXDOMAIN`, which looks exactly like a real [DNS](../concepts/networking/dns.md) failure but isn't one. This is one of the most common `dig` mistakes — always pass just `example.com`, never `https://example.com` or `example.com/path`.

## Querying a Specific Record Type

```bash
dig example.com A                # IPv4 address (the default if no type is given)
dig example.com AAAA             # IPv6 address
dig example.com CNAME            # what this hostname is aliased to
dig example.com MX               # mail server records
dig example.com TXT              # text records (SPF, domain verification, etc.)
dig example.com NS               # authoritative nameservers for this domain
dig example.com ANY              # request everything at once (many resolvers now ignore/limit this)
```

## Combining Type + Short Output

```bash
dig service.example.com CNAME +short     # e.g. confirming a Cloudflare Tunnel CNAME actually exists
```

This is the fastest way to confirm a hostname is routed the way you expect — an empty result means no record exists for that exact hostname (see [Cloudflare Tunnel Commands](cloudflare-tunnel.md) for using this to confirm `cloudflared tunnel route dns` actually took effect).

## Querying a Specific Nameserver Directly

```bash
dig example.com @8.8.8.8          # bypass your local resolver, ask Google's DNS directly
dig example.com @1.1.1.1          # ask Cloudflare's resolver directly
```

Useful for distinguishing "the record doesn't exist yet" from "it exists, but hasn't propagated to your local resolver/ISP's cache yet" — see [DNS § TTL and Propagation Delay](../concepts/networking/dns.md#ttl-and-propagation-delay).

## Reverse Lookup (IP → Hostname)

```bash
dig -x 8.8.8.8                    # what hostname does this IP resolve back to?
```

## Trace the Full Resolution Path

```bash
dig +trace example.com            # follow the lookup from the root nameservers down, hop by hop
```

Useful when a domain resolves incorrectly and you need to find exactly which nameserver in the chain is returning the wrong answer, rather than just seeing the final (wrong) result.

## Common Questions

**Why does `dig` sometimes return a different answer than my browser shows?**
> Your browser (and OS) may be using a cached [DNS](../concepts/networking/dns.md) entry, or a resolver with a different cache state than whatever `dig` queried. Query a specific public resolver directly (`dig example.com @1.1.1.1`) to rule out local caching, and check the returned record's TTL to see how long that cached answer is expected to live.

**What's the difference between `dig` and `nslookup`?**
> Both query [DNS](../concepts/networking/dns.md); `dig` gives more complete, more script-friendly output (especially with `+short`) and is generally preferred in modern Linux/macOS environments, while `nslookup` is older and its output format varies more across platforms. `host` is a third, even terser option for a quick lookup.

## Related

- [DNS (Domain Name System)](../concepts/networking/dns.md)
- [Cloudflare Tunnel Commands](cloudflare-tunnel.md)
- [HTTP](../concepts/networking/http.md)
