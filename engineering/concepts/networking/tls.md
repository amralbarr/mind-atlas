# TLS (Transport Layer Security)

**TLS** is the protocol that wraps a network connection in encryption, integrity checking, and server [authentication](../security/auth/authentication.md) — a general-purpose security layer sitting between an application protocol and the raw [TCP](tcp.md) connection beneath it. [HTTPS](https.md) (HTTP over TLS) is its best-known use, but TLS secures far more than web traffic: database connections, message brokers, email (SMTPS), and most service-to-service traffic inside a modern system all commonly run over TLS as well.

## What TLS Actually Guarantees

| Property | What it means |
|---|---|
| **Encryption** | Traffic content is unreadable to anyone intercepting it in transit |
| **Integrity** | Any tampering with data in transit is detectable |
| **[Authentication](../security/auth/authentication.md)** | The client can verify it's actually talking to the server it thinks it is (via the server's certificate), not an impersonator |

Without TLS, a network intermediary (a public Wi-Fi hotspot, an ISP, anyone on the same network segment) can read every byte of a connection in plain text — including credentials.

## The TLS Handshake (Simplified)

```text
Client → Server: "Hello, here are the TLS versions/ciphers I support"
Server → Client: "Here's my certificate + chosen cipher"
Client verifies the certificate against a trusted Certificate Authority (CA)
Client and server derive a shared encryption key for this session
   ↓
Encrypted application traffic flows from here on (HTTP, a DB protocol, anything)
```

This handshake happens once per connection (or is resumed cheaply for a reused connection) — which is exactly why [connection pooling](../databases/relational/connection-pooling.md) matters: paying the handshake cost on every single request, instead of reusing an already-established encrypted connection, is a real and measurable source of latency under load. Modern TLS (1.3) reduces the handshake to fewer round-trips than older versions, further cutting that per-connection cost.

## Certificates & Certificate Authorities

A **certificate** binds a domain name (or service identity) to a public key, signed by a **Certificate Authority (CA)** the client already trusts. The client checks: is this certificate signed by a CA I trust, is it for the identity I'm actually connecting to, and has it not expired? Free automated certificate issuance (e.g. Let's Encrypt) removed cost as a reason not to run TLS everywhere — there's essentially no excuse for a production service to accept plain, unencrypted connections today.

## What TLS Does NOT Protect

- **Data at rest** — TLS only protects data *in transit* between two endpoints; data stored in a database or on disk needs its own protection (encryption at rest, access controls) entirely independent of whether the connection that delivered it was encrypted.
- **Metadata** — the destination IP/domain (via [DNS](dns.md) lookups, and in older TLS the unencrypted SNI field), the approximate size and timing of traffic, and which certificate was presented can all still leak even over an encrypted connection. TLS hides *content*, not the fact that a connection happened.
- **Application-layer vulnerabilities** — TLS secures the pipe, not what flows through it; a [SQL injection](../security/attacks/sql-injection.md) or an [XSS](../security/attacks/xss.md) vulnerability is just as exploitable over an encrypted connection as a plain one.

## TLS vs. a Separately Encrypted Protocol (SSH)

[SSH](../protocols/ssh.md) is sometimes assumed to "use TLS," but it doesn't — [SSH](../protocols/ssh.md) implements its own, entirely separate encryption and key-exchange protocol. Both achieve the same high-level goal (encrypt a connection, authenticate the remote party), but they're independent protocol stacks: a server can run TLS-secured [HTTPS](https.md) on port 443 and [SSH](../protocols/ssh.md) on port 22 without either depending on the other.

## Related

- [HTTPS](https.md) — [HTTP](http.md) specifically run over TLS; HSTS and [HTTP](http.md)-specific framing live there
- [TCP](tcp.md) — the transport layer TLS wraps
- [SSH](../protocols/ssh.md) — a separately encrypted protocol, often confused with TLS but not built on it
- [Connection Pooling](../databases/relational/connection-pooling.md) — why reusing an already-handshaked TLS connection matters for latency
- [DNS](dns.md) — the SNI metadata-leak caveat
- [Authentication](../security/auth/authentication.md) — the certificate-based server-identity check TLS performs
- [Secrets Management](../security/secrets/secrets-management.md)
