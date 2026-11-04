# HTTPS (HTTP over TLS)

HTTPS is plain [HTTP](http.md) sent over an encrypted **[TLS](tls.md)** ([Transport Layer Security](tls.md)) connection — the request/response model, methods, and headers are all identical to [HTTP](http.md); [TLS](tls.md) just wraps the connection so a third party on the network path can't read or tamper with the traffic. See [TLS](tls.md) for the handshake, certificates/CAs, and what [TLS](tls.md) does and doesn't protect — none of that is [HTTP](http.md)-specific, it applies equally to a [TLS](tls.md)-secured database connection or message broker. This file covers what's specific to running [HTTP](http.md) over it.

Without [TLS](tls.md), a network intermediary (a public Wi-Fi hotspot, an ISP, anyone on the same network segment) can read every header, cookie, and body — including credentials sent over plain [HTTP](http.md).

## HSTS (HTTP Strict Transport Security)

A response header (`Strict-Transport-Security: max-age=...`) that tells the browser "always use HTTPS for this domain from now on, even if a link or bookmark points to plain [HTTP](http.md)" — closing a window where a first plain-[HTTP](http.md) request could be intercepted and downgraded before a redirect to HTTPS ever happens.

## Related

- [TLS](tls.md) — the handshake, certificates, metadata-leak caveats, and what's NOT protected (all moved here, since none of it is [HTTP](http.md)-specific)
- [HTTP](http.md)
- [DNS](dns.md)
- [Access Control & IAM](../security/authorization/access-control-iam.md)
- [Cloudflare Tunnel (`cloudflared`) Commands](../../commands/cloudflare-tunnel.md) — an architecture where [TLS](tls.md) is terminated at Cloudflare's edge instead of on the origin server
