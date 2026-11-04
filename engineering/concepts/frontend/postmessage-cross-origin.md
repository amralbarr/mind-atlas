# postMessage & Cross-Origin Communication

`window.postMessage()` is the standard way for two windows/frames on *different origins* to talk to each other in the browser — the mechanism an embedding host page and an embedded `<iframe>` use to exchange data safely, since same-origin JS APIs (directly reading `iframe.contentWindow`'s DOM) are blocked cross-origin by design.

## The Basic Shape

```javascript
// Sender
targetWindow.postMessage(payload, targetOrigin);

// Receiver
window.addEventListener('message', (event) => {
  // event.origin, event.source, event.data
});
```

`targetOrigin` should always be an exact origin, never `"*"` — `"*"` means "deliver this to whatever origin is currently loaded there," which defeats the purpose if the frame ever navigates somewhere else.

## Validating an Incoming Message — All Four Checks

A `message` event listener receives events from *anything* that can reach that window, not just the intended sender — a malicious page in another tab, or a compromised third-party script, can call `postMessage` against the same target. A safe listener validates all of:

| Check | Rules out |
|---|---|
| `event.origin === expectedOrigin` (exact match, not a prefix/substring check) | A message from an unrelated origin |
| `event.source === expectedWindowReference` (e.g. `window.parent`) | A message that happens to share the expected origin but was relayed from a different frame/tab under that same origin |
| A message-format/version field | An old cached script (yours, from a previous deploy) sending a payload the current code no longer expects |
| Schema validation of the payload (e.g. via a runtime validator) | Malformed or unexpected fields being best-effort parsed instead of rejected |

Skipping the `event.source` check specifically is a common, subtle gap — origin alone doesn't prove the message came from the specific frame relationship you expect.

## Handshake Ordering Matters

A frequent race condition: the parent page posts an "init" message before the embedded iframe's own JavaScript has finished loading and attached its listener — the message is sent into the void and silently lost. The robust pattern is for the *embedded* side to post a "ready" message first, once its own listener is attached, and have the parent reply only after receiving that signal — removing the race entirely rather than papering over it with a delay/timeout.

## Never Trust Sensitive Data From the Message Itself

If an [authorization](../security/authorization/authorization.md) decision (which resource this session may access, what it's allowed to do) is available both from a previously-issued, signed token *and* from a field in a `postMessage` payload, the token must always win — treat the message payload as UI configuration (theme, locale, "which tab to open") at most, never as an [authorization](../security/authorization/authorization.md) input. A `postMessage` payload is just JavaScript data with no cryptographic guarantee of integrity beyond the origin/source checks above; a signed, previously-issued token guarantees the value hasn't been altered since a trusted party issued it.

## Why Not Just Use a Query-String Token?

Passing an auth token via the iframe's URL (`?token=...`) is tempting but leaks it into browser history, the host's own server access logs, and the `Referer` header of any request the iframe subsequently makes to a third party — all persistent, harder-to-audit exposure surfaces compared to a token that only ever exists in an in-memory JS variable and a `postMessage` payload.

## Real-World Example

A real third-party embeddable-widget design hardens exactly this protocol for a third-party-embeddable widget: all four validation checks above (origin, source, version, schema), the embedded page posting "ready" first to remove the hydration race, a `resource` field deliberately dropped from the handshake payload because the [authorization](../security/authorization/authorization.md)-relevant value must come only from the previously-issued token, and an explicit decision to keep the token in memory only (never `localStorage`) with the host's own page treated as the realistic [XSS](../security/attacks/xss.md) threat surface.

## Common Questions

**Should the token received via postMessage be stored in `localStorage` for persistence across reloads?**
> Generally no for an embedded, third-party-hosted context — an [XSS](../security/attacks/xss.md) vulnerability on the *host's* page is a realistic threat model, and `localStorage` is readable by any script running on that origin. Keeping the token in memory only means a page reload always re-requests a fresh token via the handshake rather than trusting a persisted one that could have been read by an attacker's script in the meantime.

**How should the two sides recover if the token is about to expire mid-session?**
> The embedded side should post a "token expiring soon" event *before* expiry, giving the host time to mint a new one and re-send it through the same handshake — avoiding a hard reload or a visible interruption for the end user.

## Related

- [Content-Security-Policy (CSP)](../security/attacks/content-security-policy.md)
- [JWT](../security/auth/jwt.md)
- [Event Loop](../programming/javascript/event-loop.md)
- [CORS](../security/attacks/cors.md)
- [CSRF](../security/attacks/csrf.md)
- [XSS](../security/attacks/xss.md)
