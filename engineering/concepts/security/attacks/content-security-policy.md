# Content-Security-Policy (CSP)

CSP is a response header that tells the browser which sources of content (scripts, frames, connections) a page is allowed to load or be loaded into — a second line of defense against [XSS](xss.md) and clickjacking that works even if application code has a bug.

## Key Directives

| Directive | Controls |
|---|---|
| `default-src` | Fallback for any directive not explicitly set |
| `script-src` | Which scripts may execute |
| `frame-ancestors` | Which origins may embed *this* page in an `<iframe>` — replaces the older `X-Frame-Options` header |
| `object-src` | Plugins (`<object>`, `<embed>`) — usually `'none'` |
| `base-uri` | Restricts `<base>` tag targets, preventing a relative-URL-hijack attack |
| `form-action` | Which URLs a `<form>` may submit to |
| `connect-src` | Which URLs `fetch`/`XHR`/WebSocket may reach |

## `frame-ancestors` vs. `X-Frame-Options`

`X-Frame-Options` only supports `DENY`, `SAMEORIGIN`, or (inconsistently, deprecated) a single allowed origin. `frame-ancestors` supports a list of origins and checks **every ancestor frame**, not just the immediate parent — needed the moment an embed can be nested more than one frame deep (host page → host's own iframe wrapper → your embedded page). A [reverse proxy](../../networking/reverse-proxy.md) or [CDN](../../networking/cdn.md) that sets a blanket `X-Frame-Options: DENY` across every route can silently override an application-level `frame-ancestors` that was configured correctly — always check the full request path (app, [reverse proxy](../../networking/reverse-proxy.md), [CDN](../../networking/cdn.md)) for conflicting legacy headers, not just the application code.

## Nonce-Based `script-src` for Server-Rendered Apps

`script-src 'self'` alone blocks a framework's own inline bootstrap scripts on frameworks that inject them at render time. The standard fix is a **per-request nonce**: the server generates a random value per response, includes it in the CSP header (`script-src 'nonce-{value}' 'strict-dynamic'`) and stamps the same value onto each `<script>` tag it renders. This requires the route to render dynamically (a nonce can't be baked into a statically-generated page, since it must differ per request) — a real deployment-mode constraint, not just a header string to copy in.

## Real-World Example

A real third-party embeddable-widget design documents both traps above concretely: the initial design fetched an allowed-origins list from a public endpoint at load time (removed — the route is already tenant/app-scoped, so the server can compute `frame-ancestors` directly at render time from data it already has), and the doc separately calls out checking the [reverse proxy](../../networking/reverse-proxy.md) for a blanket `X-Frame-Options` that could silently block the new embed origin even with `frame-ancestors` configured correctly at the application layer. It also documents the Next.js nonce/`'strict-dynamic'` requirement for a server-rendered embed page's own framework scripts.

## Common Questions

**Why does a page need `frame-ancestors` if it never gets embedded anywhere?**
> Setting it to `'self'` (or `'none'`) explicitly is cheap defense-in-depth against clickjacking, even for pages that were never designed to be embedded — the absence of the header is a silent "any origin may frame this," not "no origin may."

**Where does the list of allowed framing origins come from for a multi-tenant embed product?**
> It should be computed server-side, per request, from the specific tenant/customer the route is already resolving (e.g. from a URL path segment identifying which customer's embed this is) — not from a public, unauthenticated lookup endpoint that would let anyone enumerate which origins a given customer has configured.

## Related

- [postMessage & Cross-Origin Communication](../../frontend/postmessage-cross-origin.md)
- [Access Control & IAM](../authorization/access-control-iam.md)
- [CDN](../../networking/cdn.md)
- [XSS](xss.md)
- [CORS](cors.md)
