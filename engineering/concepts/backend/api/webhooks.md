# Webhooks

A webhook is a way for one system to notify another about an event, in real time, by having the *notifying* system make an outbound [HTTP](../../networking/http.md) request to a URL the *receiving* system provided in advance — inverting the usual client-polls-server model into "the server calls you when something happens."

## The Core Idea: Inverted Polling

Without webhooks, finding out about a remote event means repeatedly asking:

```text
Client: "Any new orders?" → Server: "No"
Client: "Any new orders?" → Server: "No"
Client: "Any new orders?" → Server: "Yes! Here's one"
```

This wastes requests on "no" answers and adds latency (you only find out up to one polling interval late). A webhook flips it:

```text
1. Client registers a URL: "POST new orders to https://myapp.com/webhooks/orders"
2. An order is created
3. The server immediately POSTs the event to that URL — no polling needed
```

The receiving side stops asking and simply waits to be called.

## A Concrete Example (Stripe-Style Payment Webhook)

```http
POST /webhooks/stripe HTTP/1.1
Content-Type: application/json
Stripe-Signature: t=1699999999,v1=5257a869e7...

{
  "type": "payment_intent.succeeded",
  "data": {
    "object": { "id": "pi_123", "amount": 2000 }
  }
}
```

```javascript
app.post('/webhooks/stripe', (req, res) => {
  const event = req.body;
  if (event.type === 'payment_intent.succeeded') {
    fulfillOrder(event.data.object.id);
  }
  res.status(200).send(); // acknowledge receipt — see below
});
```

## Verifying Authenticity

Since a webhook endpoint is a public URL accepting POST requests, anything on the internet can technically send it a request — the receiver must verify the request actually came from the expected sender, not forge one. The standard mechanism is a **signature header**: the sender computes an [HMAC](../../security/secrets/hashing-vs-encryption.md) of the payload using a shared secret, and the receiver recomputes it and compares:

```javascript
const crypto = require('crypto');

function verifySignature(payload, signatureHeader, secret) {
  const expected = crypto.createHmac('sha256', secret).update(payload).digest('hex');
  return crypto.timingSafeEqual(Buffer.from(expected), Buffer.from(signatureHeader));
}
```

`timingSafeEqual` matters here for the same reason it matters anywhere comparing secrets — a naive `===` string comparison can leak timing information about how many leading characters matched, in principle allowing an attacker to guess the correct signature byte by byte.

## Acknowledge Fast, Process Later

A webhook receiver should respond quickly (a `2xx` status) to confirm receipt, then do the actual processing asynchronously — most webhook senders (Stripe, GitHub, Twilio) will **retry** delivery if they don't get a timely `2xx` response, and a slow handler risks the sender timing out and re-sending a duplicate before the first attempt even finishes:

```text
Receive webhook
     ↓
Verify signature
     ↓
Enqueue event for processing (see Queues)
     ↓
Respond 200 immediately
     ↓
(separately) Worker processes the queued event
```

## Idempotency: Handling Duplicate Deliveries

Because senders retry on failure/timeout, a receiver **will** eventually see the same event more than once — this isn't an edge case, it's an expected part of the contract. Every webhook payload should include a unique event ID, and the receiver should record processed IDs to skip duplicates:

```javascript
if (await alreadyProcessed(event.id)) return res.status(200).send();
await markProcessed(event.id);
await handleEvent(event);
```

See [Idempotency & Race Conditions](../../programming/fundamentals/idempotency-and-race-conditions.md) for the general principle this is a specific instance of.

## Webhooks vs. Polling vs. Pub/Sub

| | Polling | Webhooks | [Pub/Sub](../../distributed-systems/messaging/publish-subscribe.md) |
|---|---|---|---|
| Who initiates | The consumer, repeatedly | The producer, once per event | The producer publishes; a broker fans out to subscribers |
| Latency | Up to one polling interval | Near-real-time | Near-real-time |
| Wasted requests | Yes — most polls find nothing new | No — only fires on real events | No |
| Works across organizational boundaries (e.g. Stripe → your server)? | Yes, but inefficient | Yes — the standard way third-party SaaS products notify external systems | Rare — [pub/sub](../../distributed-systems/messaging/publish-subscribe.md) brokers are typically internal infrastructure, not exposed to external companies |
| Requires the receiver to have a public, reachable endpoint | No | Yes | No — the broker mediates |

Webhooks are essentially how two *separate organizations'* systems do event-driven communication across the open internet, where a shared internal broker like [Kafka](../../distributed-systems/messaging/kafka.md) or [RabbitMQ](../../distributed-systems/messaging/rabbitmq.md) isn't an option — you can't ask Stripe to publish onto your internal message queue, but you can give it a URL to POST to.

## Local Development: Webhooks Need a Public URL

A webhook sender needs to reach the receiver's URL over the public internet, which is awkward when developing locally (`localhost` isn't reachable from Stripe's servers). Tunneling tools (ngrok, Cloudflare Tunnel) expose a local dev server through a temporary public URL specifically to make webhook development possible without deploying first.

## Common Questions

**What happens if a webhook receiver is down when an event fires?**
> Most reputable webhook senders retry with backoff for a period (Stripe retries for up to three days, for example) and often provide a dashboard to inspect/manually redeliver failed events — but this isn't guaranteed by the [HTTP](../../networking/http.md) protocol itself, only by the sender's own retry policy, so a receiver shouldn't assume delivery is bulletproof without checking the specific provider's guarantees.

**Why can't the receiver just trust that a request to its webhook URL is legitimate?**
> Because the URL is often guessable or discoverable, and it accepts arbitrary POST bodies from the internet — without signature verification, anyone could forge a fake "payment succeeded" event and trigger whatever action the receiver takes on it (e.g. fraudulently marking an order as paid).

**Is a webhook the same thing as a callback URL in an OAuth flow?**
> Related in spirit (both are "give me a URL to call back to") but different purposes — an OAuth redirect URI is a one-time, user-browser-driven redirect as part of an auth flow; a webhook is a server-to-server, repeated, asynchronous event notification unrelated to any specific user's browser session.

## Related

- [API](api.md) — the general contract concept webhooks invert the direction of
- [Publish-Subscribe](../../distributed-systems/messaging/publish-subscribe.md)
- [Idempotency & Race Conditions](../../programming/fundamentals/idempotency-and-race-conditions.md)
- [Queues](../../distributed-systems/messaging/queues.md)
- [Hashing vs. Encryption](../../security/secrets/hashing-vs-encryption.md)
- [REST](rest.md)
