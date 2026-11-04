# WAF (Web Application Firewall)

A **Web Application Firewall (WAF)** inspects the actual content of [HTTP](../../networking/http.md) requests — URLs, headers, query parameters, request bodies — against known attack signatures, and blocks or flags anything matching before it ever reaches the application. It sits at Layer 7, which is what distinguishes it from a network firewall or [NSG](../../cloud/azure/azure-nsg.md): a network firewall decides *whether a connection is allowed at all* based on IP/port/protocol; a WAF decides *whether this specific request's content looks like an attack*, regardless of whether the connection itself is perfectly legitimate.

## What It Actually Checks

A WAF runs the request content against a ruleset — almost always built on, or compatible with, the **OWASP Core Rule Set (CRS)**, the standard open-source baseline covering the OWASP Top 10 attack classes:

| Pattern it looks for | Attack class it's defending against |
|---|---|
| `' OR '1'='1`, `UNION SELECT`, [SQL](../../databases/relational/sql.md) keywords in unexpected places | [SQL Injection](sql-injection.md) |
| `<script>`, `javascript:`, `onerror=` in input fields | [XSS](xss.md) |
| `../../../etc/passwd`, encoded path traversal sequences | Path traversal |
| Known exploit strings for specific CVEs in headers/user-agent | Exploitation of known vulnerabilities |
| Abnormal request rate from one source | Brute-force / scraping (often paired with [rate limiting](../../backend/architecture/rate-limiting.md) rather than the WAF's own ruleset) |

This is fundamentally **signature and pattern matching**, not an understanding of what the application actually does — a WAF has no idea what a "valid order" looks like for a specific e-commerce app; it only knows what a [SQL injection](sql-injection.md) string typically looks like in general.

## What It Catches Well, and What It Doesn't

| | |
|---|---|
| **Catches well** | Known, common attack patterns arriving as part of the request itself — a classic SQLi string in a form field, a `<script>` tag in a comment body, a scanner probing for a known vulnerable path |
| **Does not catch** | [DOM-based XSS](xss.md) — the payload never touches the server at all, so a server-side WAF has nothing to inspect; business-logic flaws (a correctly-authenticated user misusing legitimate functionality in a way the app never validated); novel attack patterns that don't match any existing signature; an attack that's syntactically identical to normal use (a legitimate user's search query that happens to contain [SQL](../../databases/relational/sql.md)-like text) |

The standard framing — already used elsewhere in this handbook for [SQL Injection](sql-injection.md#defenses) — is that a WAF is **a backstop, not a fix**: it catches obviously malicious traffic at the edge, cheaply, before it costs the application anything, but it is never a substitute for parameterized queries, output encoding, or the actual application-level defense the attack class requires. An application with no [SQL injection](sql-injection.md) defense other than a WAF is one crafted payload away from a breach the moment it doesn't match an existing rule.

## False Positives and Tuning

Because detection is pattern-based, a WAF can block entirely legitimate traffic that happens to resemble an attack signature — a user's free-text message that contains the literal words "select" and "from," a developer's support ticket that includes a real [SQL](../../databases/relational/sql.md) error message for debugging purposes. This is why WAFs are deployed in stages, not switched straight to blocking:

1. **Detection/log-only mode** — the WAF logs what it *would* have blocked, without actually blocking anything, so false positives surface against real traffic before enforcement begins
2. **Tuning** — specific rules get exceptions (allowlisting a known-safe field, or a known-safe pattern) based on what detection mode revealed
3. **Blocking mode** — only after tuning, with monitoring kept on to catch any new false positive that shows up under real traffic patterns

Skipping straight to blocking mode on day one is a common, avoidable cause of a WAF breaking a legitimate feature in production.

## Deployment Models

| Model | Example | Trade-off |
|---|---|---|
| **Managed, edge/[CDN](../../networking/cdn.md)-integrated** | [Azure](../../cloud/azure/azure.md) Front Door WAF, Cloudflare WAF, [AWS](../../cloud/infrastructure/aws.md) WAF | No infrastructure to run; rules managed by the provider, updated automatically against emerging attack patterns |
| **Reverse-proxy module** | ModSecurity on [NGINX](../../backend/api-gateways/nginx.md) | Self-hosted, full control over rules, but the operational burden (patching, rule updates, tuning) is now the team's own |
| **Dedicated appliance/service** | [Azure](../../cloud/azure/azure.md) Firewall (at the network perimeter, broader than just L7 [HTTP](../../networking/http.md) inspection) | Centralized, organization-wide egress control — see [NSG vs. Azure Firewall](../../cloud/azure/azure-nsg.md#nsg-vs-azure-firewall) for where this overlaps and differs from a WAF specifically |

A cloud-edge WAF (Front Door, Cloudflare) is the common default for a public-facing web application precisely because it needs no infrastructure and inherits the provider's continuously-updated ruleset — the same reasoning that makes a managed [API gateway](../../backend/api-gateways/azure-api-management.md) attractive over a self-hosted one for the same category of reason (less to operate, provider-managed updates).

## Common Questions

**If a WAF blocks known [SQL injection](sql-injection.md) patterns, do I still need parameterized queries?**
> Yes, unconditionally — the WAF is a backstop against *known* patterns; parameterized queries are what makes the application actually immune to the attack class regardless of whether the payload matches any known signature. Relying on the WAF alone means a single novel-enough payload (or one the WAF has a rule gap for) reaches a genuinely vulnerable code path.

**Where does a WAF sit relative to a load balancer or API gateway?**
> Upstream of both, typically — WAF inspection usually happens at the very edge, before traffic even reaches a load balancer or [API gateway](../../backend/api-gateways/azure-api-management.md), so that obviously malicious requests are rejected as cheaply as possible, before consuming any further infrastructure. See the query flow in [the Azure RAG platform map](../../../interview/interview-01/22-azure-rag-platform-map.md) for a concrete ordering (WAF → API Management → application).

**Does a WAF protect against DDoS?**
> Only incidentally, and only for application-layer (L7) request floods it can rate-limit or pattern-match — volumetric network-layer DDoS needs separate scrubbing infrastructure upstream of the WAF entirely, the same distinction already covered in [Rate Limiting](../../backend/architecture/rate-limiting.md#common-questions).

## Related

- [SQL Injection](sql-injection.md) — one of the primary attack classes a WAF's ruleset targets, and why it's a backstop, not a fix
- [XSS](xss.md) — another primary target, and the specific case (DOM-based [XSS](xss.md)) a server-side WAF structurally cannot catch
- [fail2ban](fail2ban.md) — a related but distinct edge defense: log-based IP banning rather than per-request content inspection
- [NSG](../../cloud/azure/azure-nsg.md) — the network-layer (L3/L4) firewall a WAF's application-layer (L7) inspection complements, not replaces
- [Rate Limiting](../../backend/architecture/rate-limiting.md) — the request-volume defense often deployed alongside a WAF at the same edge layer
- [Azure API Management](../../backend/api-gateways/azure-api-management.md) — commonly sits just behind the WAF in a real request path
- [Azure RAG Platform Map](../../../interview/interview-01/22-azure-rag-platform-map.md) — shows WAF's concrete position in a full enterprise request flow
