# CSRF (Cross-Site Request Forgery)

CSRF is an attack that tricks a logged-in user's browser into sending an unwanted, state-changing request to a site they're authenticated on — the request carries the victim's own valid session cookie, so the server has no way to tell it apart from a request the user actually meant to make.

## How the Attack Works

```text
1. User logs into bank.com — browser stores a session cookie for bank.com
2. Without logging out, the user visits evil.com
3. evil.com's page auto-submits a hidden form:
     <form action="https://bank.com/transfer" method="POST">
       <input name="to" value="attacker">
       <input name="amount" value="10000">
     </form>
     <script>document.forms[0].submit()</script>
4. The browser attaches bank.com's cookie automatically — it doesn't know
   the request "came from" evil.com in a way the server can reject on cookie
   presence alone
5. bank.com sees a valid session cookie and processes the transfer
```

The attacker never sees the victim's cookie or credentials — they don't need to. They just need the victim's browser to *send* a request, and cookies are attached automatically by the browser to any request targeting the cookie's domain, regardless of which page triggered it.

## Why It Works: Ambient Authority

CSRF is possible because cookies are **ambient authority** — the browser attaches them to a request based purely on the destination domain, not on which page or script initiated the request. Anything that relies solely on a cookie for [authentication](../auth/authentication.md) is vulnerable unless something else in the request proves the request actually originated from the site's own pages.

## Defenses

| Defense | How it works |
|---|---|
| **CSRF tokens (synchronizer token pattern)** | Server embeds a random, per-session (or per-request) token in every form/page; the request must include it back as a header or body field. An attacker's cross-origin page can't read this token (same-origin policy blocks it), so it can't forge a valid request. |
| **`SameSite` cookies** | `SameSite=Lax` or `Strict` tells the browser not to attach the cookie on cross-site requests at all (Lax still allows top-level GET navigations; Strict blocks even those). Since modern browsers default new cookies to `SameSite=Lax`, this alone blocks the classic auto-submitting-POST-form attack. |
| **Checking `Origin`/`Referer` headers** | The server rejects state-changing requests whose `Origin` or `Referer` header doesn't match its own domain — a defense-in-depth backstop, not a primary defense (these headers can be absent in some legitimate cases). |
| **Requiring custom headers for state-changing requests** | A [JSON](../../programming/fundamentals/json.md) API that requires e.g. `X-Requested-With` on POST/PUT/DELETE incidentally blocks CSRF, since a plain HTML form can't set arbitrary headers — only `fetch`/`XHR` can, and those are subject to [CORS](cors.md), which blocks a malicious origin from sending it with credentials unless explicitly allowed. |

## CSRF Token Flow

```text
GET /transfer-form
  → server renders form with a hidden field: <input type="hidden" name="_csrf" value="a1b2c3...">

POST /transfer
  body: { to: "friend", amount: 100, _csrf: "a1b2c3..." }
  → server checks the token matches the one issued for this session
  → if missing or mismatched: reject with 403
```

## CSRF vs. XSS

These are frequently confused but solve entirely different problems:

| | CSRF | [XSS](xss.md) |
|---|---|---|
| What's exploited | The browser automatically attaching credentials to a request | The server rendering attacker-controlled content as executable code/HTML |
| Attacker needs | The victim to visit a malicious page while authenticated elsewhere | To inject a script that runs *on the vulnerable site itself* |
| Can it steal data directly? | No — it can only trigger actions, not read responses (same-origin policy blocks the attacker page from reading the response) | Yes — a successful [XSS](xss.md) payload runs with full access to the page's DOM, cookies (unless `HttpOnly`), and can exfiltrate anything |
| Primary defense | CSRF tokens, `SameSite` cookies | Output encoding, [CSP](content-security-policy.md), input sanitization |

Note [XSS](xss.md) can be used to *defeat* CSRF defenses (an [XSS](xss.md) payload running on the legitimate site can read the CSRF token directly out of the DOM and forge a valid request) — this is why the two are often discussed together: a site fully immune to CSRF can still be compromised via an [XSS](xss.md) hole that reads its own tokens.

## Why Token-Based APIs (JWT in a Header) Are Naturally Less CSRF-Exposed

If an API requires the client to send an `Authorization: Bearer <token>` header instead of relying on a cookie, CSRF mostly disappears as a concern — a plain HTML form (the classic CSRF vector) cannot set custom headers, and a `fetch`/`XHR` call that could set one is bound by [CORS](cors.md), which blocks a cross-origin page from making an authenticated call unless the server's [CORS](cors.md) policy explicitly allows it. This is one reason many SPA/mobile-API architectures store the access token client-side and send it as a header rather than relying purely on a session cookie — though this trades one risk for another (a token readable by JavaScript is now exposed to [XSS](xss.md) instead).

## Common Questions

**Does [HTTPS](../../networking/https.md) protect against CSRF?**
> No. [HTTPS](../../networking/https.md) only encrypts the connection — it does nothing to prevent the browser from attaching a valid cookie to a forged request. CSRF and [TLS](../../networking/tls.md) are orthogonal concerns.

**Is a GET-based CSRF attack possible?**
> Yes, if a state-changing action is exposed via GET (a [REST](../../backend/api/rest.md) anti-pattern anyway — see [REST](../../backend/api/rest.md)'s cacheable/safe-method conventions). A malicious `<img src="https://bank.com/transfer?to=attacker&amount=10000">` triggers the request the moment the victim's browser loads the image, no script required. This is exactly why state-changing operations should never be exposed via GET.

**Do modern frameworks handle CSRF automatically?**
> Many do to some degree — e.g. [Django](../../programming/python/django.md) and Rails ship built-in CSRF-token [middleware](../../backend/middleware.md) for form submissions. Pure [JSON](../../programming/fundamentals/json.md) APIs consumed by SPAs more often rely on `SameSite` cookies plus [CORS](cors.md) rather than the classic synchronizer-token pattern, since there's no server-rendered `<form>` to embed a hidden token into.

## Related

- [XSS](xss.md)
- [CORS](cors.md)
- [Content-Security-Policy (CSP)](content-security-policy.md)
- [JWT](../auth/jwt.md)
- [HTTPS](../../networking/https.md)
