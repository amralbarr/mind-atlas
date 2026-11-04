# curl Commands

The command-line [HTTP](../concepts/networking/http.md) client used constantly for testing APIs, debugging [webhooks](../concepts/backend/api/webhooks.md), and scripting deploys. See [HTTP](../concepts/networking/http.md) and [HTTP Status Codes](../concepts/backend/api/http-status-codes.md) for the protocol concepts these requests actually exercise.

## Basic Requests

```bash
curl https://api.example.com/users               # GET, prints the response body
curl -i https://api.example.com/users            # include response headers in the output
curl -v https://api.example.com/users            # verbose — show the full request/response, including TLS handshake
curl -s https://api.example.com/users            # silent — suppress the progress meter (good for scripts)
curl -o response.json https://api.example.com/users   # save the response body to a file
```

## Specifying the Method

```bash
curl -X POST https://api.example.com/users
curl -X PUT https://api.example.com/users/1
curl -X PATCH https://api.example.com/users/1
curl -X DELETE https://api.example.com/users/1
```

## Headers & Auth

```bash
curl -H "Authorization: Bearer <token>" https://api.example.com/users
curl -H "Content-Type: application/json" -H "X-Request-Id: abc123" https://api.example.com/users

curl -u username:password https://api.example.com/users   # HTTP Basic Auth
```

See [JWT](../concepts/security/auth/jwt.md) for what's actually inside that bearer token.

## Sending a Body

```bash
# JSON body (the most common case)
curl -X POST https://api.example.com/users \
  -H "Content-Type: application/json" \
  -d '{"name": "Ada", "email": "ada@example.com"}'

# Read the body from a file instead of inlining it
curl -X POST https://api.example.com/users \
  -H "Content-Type: application/json" \
  -d @payload.json

# Form-encoded body
curl -X POST https://api.example.com/login \
  -d "username=ada&password=secret"

# File upload (multipart/form-data)
curl -X POST https://api.example.com/upload \
  -F "file=@photo.jpg"
```

## Following Redirects & Handling Errors

```bash
curl -L https://example.com/old-path             # follow 3xx redirects (curl does NOT follow by default)
curl -f https://api.example.com/users            # fail silently (no body output) on 4xx/5xx, exit non-zero
curl -w "%{http_code}\n" -o /dev/null -s https://api.example.com/users   # print just the status code
```

`-f` matters most inside scripts — without it, curl exits `0` even on a `404`/`500` response, so a script checking `$?` alone would wrongly think the request succeeded.

## Timeouts & Retries

```bash
curl --connect-timeout 5 https://api.example.com/users    # max time to establish the connection
curl --max-time 30 https://api.example.com/users          # max time for the whole request
curl --retry 3 --retry-delay 2 https://api.example.com/users   # retry on transient failure
```

## Testing SSE / Streaming Endpoints

```bash
curl -N https://api.example.com/stream           # -N disables buffering, so chunks print as they arrive
```

Useful for manually watching an [SSE](../concepts/protocols/sse.md) or streaming [LLM](../concepts/ai/generation/llm.md) response endpoint without a browser.

## Debugging TLS

```bash
curl -v https://api.example.com                 # -v shows the certificate chain during the handshake
curl -k https://self-signed.example.com          # skip certificate verification (local/dev only — never in production scripts)
```

## Common Questions

**Why does `curl -X POST` sometimes silently behave like a GET?**
> If `-d`/`--data` is used without an explicit `-X POST`, curl actually infers POST automatically — but combining `-X GET` with `-d` is a common copy-paste mistake that sends a GET request with a body, which many servers either ignore or reject. When in doubt, be explicit about both the method and whether a body is intended.

**How do I see exactly what curl is about to send, without actually sending it?**
> There's no true dry-run flag, but `-v` prints the full outgoing request (method, headers, and — for most cases — enough to verify what's being sent) alongside the response, which is normally sufficient for debugging what actually went over the wire.

## Related

- [HTTP](../concepts/networking/http.md)
- [HTTP Status Codes](../concepts/backend/api/http-status-codes.md)
- [JWT](../concepts/security/auth/jwt.md)
- [SSE](../concepts/protocols/sse.md)
- [REST](../concepts/backend/api/rest.md)
- [Bash & Shell Commands](bash.md) — see "Extracting One Value From a `.env` File Without Sourcing It" for pulling a token out of a `.env` file to inline into a curl `Authorization` header
