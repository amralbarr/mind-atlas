# CORS (Cross-Origin Resource Sharing)

CORS is a browser-enforced security mechanism that controls whether JavaScript running on one origin is allowed to read the response of a request it made to a *different* origin. It exists to relax — in a controlled, server-opt-in way — the browser's default **same-origin policy**, which otherwise blocks a page from reading responses from any origin other than its own.

## What Counts as a Different Origin

An origin is the combination of **scheme + host + port**. Any difference makes it cross-origin:

| URL A | URL B | Same origin? |
|---|---|---|
| `https://app.example.com` | `https://api.example.com` | No — different subdomain |
| `https://example.com` | `http://example.com` | No — different scheme |
| `https://example.com` | `https://example.com:8443` | No — different port |
| `https://example.com/a` | `https://example.com/b` | Yes — path doesn't matter |

## The Common Misconception

CORS does **not** stop a cross-origin request from being *sent* — the request still reaches the server and the server still processes it. What CORS controls is whether the *browser* lets the calling JavaScript *read the response*. This is why CORS is a browser-side, JavaScript-fetch concern, not a general network security boundary — a `<form>` submission, an `<img>` tag, or a direct `curl` call are entirely unaffected by CORS, because CORS is specifically about a script reading a cross-origin response via `fetch`/`XMLHttpRequest`.

## How the Server Opts In

The server includes response headers telling the browser which origins are allowed to read the response:

```http
Access-Control-Allow-Origin: https://app.example.com
Access-Control-Allow-Credentials: true
```

If the header is missing, or names a different origin than the one that made the request, the browser blocks the calling script from reading the response (the request already happened — the browser just withholds the response body/headers from JavaScript).

## Simple Requests vs. Preflighted Requests

Not every cross-origin request triggers an extra round-trip. The browser only sends a **preflight** — an `OPTIONS` request asking permission before the real one — when the actual request isn't a "simple request":

| Simple request (no preflight) | Triggers a preflight |
|---|---|
| Method is `GET`, `HEAD`, or `POST` | Method is `PUT`, `PATCH`, `DELETE`, or anything else |
| Only "CORS-safelisted" headers (`Accept`, `Accept-Language`, `Content-Type` limited to a few values) | Custom headers present (`Authorization`, `X-Requested-With`, a custom [API key](../auth/api-key.md) header) |
| `Content-Type` is `application/x-www-form-urlencoded`, `multipart/form-data`, or `text/plain` | `Content-Type: application/json` |

Most real API calls ([JSON](../../programming/fundamentals/json.md) body, `Authorization` header, or a non-GET/POST method) end up preflighted.

## The Preflight Exchange

```http
OPTIONS /orders HTTP/1.1
Origin: https://app.example.com
Access-Control-Request-Method: PUT
Access-Control-Request-Headers: authorization, content-type
```

```http
HTTP/1.1 204 No Content
Access-Control-Allow-Origin: https://app.example.com
Access-Control-Allow-Methods: GET, POST, PUT, DELETE
Access-Control-Allow-Headers: authorization, content-type
Access-Control-Max-Age: 86400
```

Only if the preflight response allows the requested method/headers does the browser send the actual `PUT` request. `Access-Control-Max-Age` lets the browser cache that answer, avoiding a preflight on every single call for the configured duration.

## Credentialed Requests

Cookies aren't sent on a cross-origin `fetch` by default. To include them, the client must opt in explicitly, and the server must respond with an explicit (not wildcard) allowed origin:

```javascript
fetch('https://api.example.com/me', { credentials: 'include' });
```

```http
Access-Control-Allow-Origin: https://app.example.com   ← must be a specific origin
Access-Control-Allow-Credentials: true                  ← required alongside it
```

`Access-Control-Allow-Origin: *` is explicitly **not allowed** together with credentials — the spec forbids it, because a wildcard combined with cookie-forwarding would let any site read another site's authenticated data. This is one of the most common CORS misconfiguration bugs: setting the origin dynamically to reflect whatever `Origin` header the request sent (effectively `*` in disguise) while also allowing credentials.

## Setting It Up (Express/NestJS)

```typescript
// NestJS
app.enableCors({
  origin: ['https://app.example.com'],
  credentials: true,
  methods: ['GET', 'POST', 'PUT', 'DELETE'],
  allowedHeaders: ['Content-Type', 'Authorization'],
});
```

## CORS vs. CSRF

These get confused because both involve cross-origin requests, but they protect against opposite risks:

| | CORS | [CSRF](csrf.md) |
|---|---|---|
| Protects | The *response* from being read by unauthorized scripts | The server from *acting on* a forged request |
| Enforced by | The browser, per the server's response headers | The server, via tokens/`SameSite` cookies |
| Blocks what | Reading data cross-origin | Triggering state changes cross-origin |
| A loose config's risk | Data leakage to a malicious origin | Unwanted actions performed on the victim's behalf |

A wildcard CORS policy on a sensitive endpoint is dangerous specifically because it lets a malicious origin's script read data it has no business reading — a completely different failure mode from [CSRF](csrf.md), which doesn't need to read anything to do damage.

## Common Questions

**If my API returns a CORS error in the browser console, does that mean the request never reached the server?**
> No — for a simple request, the request was sent and the server processed it; the browser just hid the response from the calling script. For a preflighted request, the actual request may never be sent at all if the `OPTIONS` preflight itself is rejected.

**Why does a mobile app or Postman never hit CORS errors, but a browser does?**
> Because CORS is a browser-enforced policy, not a server-enforced one (aside from the server choosing which headers to send). Tools and native apps that don't implement the same-origin policy/CORS spec simply read whatever response comes back, regardless of origin.

**Does CORS protect an API from unauthorized use entirely?**
> No — CORS only controls which *browser-based, script-driven* origins can read responses. It does nothing to stop a server-to-server call, a curl request, or a modified/self-hosted client that ignores the browser's CORS restrictions entirely. Real [authorization](../authorization/authorization.md) must still happen server-side (auth tokens, [access control](../authorization/access-control-iam.md)) — CORS is not an [authentication](../auth/authentication.md) mechanism.

## Related

- [CSRF](csrf.md)
- [Content-Security-Policy (CSP)](content-security-policy.md)
- [postMessage & Cross-Origin Communication](../../frontend/postmessage-cross-origin.md)
- [REST](../../backend/api/rest.md)
