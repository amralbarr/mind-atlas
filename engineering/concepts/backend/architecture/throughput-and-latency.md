# Throughput and Latency

Two independent measurements of system performance that are often confused and frequently trade off against each other.

---

## Throughput

How many requests (or jobs, tokens, messages) the system completes per unit of time.

```
Throughput = requests / second
```

Think of it as the **width of a pipe** — how much can flow through at once.

```
10 users send requests simultaneously
System processes all 10 in 1 second  →  Throughput = 10 req/s

Same system under 100 simultaneous users takes 20 seconds total
→  Throughput = 5 req/s  (degrading under load)
```

High throughput = the system handles many requests efficiently.
Throughput drops when a resource is saturated — CPU, memory, DB connections, thread pool, network bandwidth.

---

## Latency

How long a single request takes from the moment it is sent to the moment the response is received.

```
Latency = time from request sent → response received  (ms or seconds)
```

Think of it as the **length of the pipe** — how long one item takes to travel through.

---

## Percentile Latency — P50, P95, P99

Average latency hides the worst cases. Percentiles expose them.

**P95 latency** means: 95% of requests completed faster than this time. The remaining 5% took longer — these are the "tail."

```
Sort 100 request durations from fastest to slowest:
  #1  – #50  :  20ms – 80ms
  #51 – #94  :  80ms – 300ms
  #95 – #99  :  300ms – 800ms
  #100       :  2000ms          ← single worst request

P50  =  80ms    — half of all requests are faster than this (the median)
P95  =  300ms   — 95% of requests are faster than this
P99  =  800ms   — 99% of requests are faster than this
P99.9 = 2000ms  — 99.9% of requests are faster than this
```

### Why not just use average?

```
9 requests take 10ms
1 request  takes 1000ms

Average = (9 × 10 + 1000) / 10 = 109ms  ← sounds acceptable
P99     = 1000ms                          ← 1 in 100 users waits 1 second
```

In a system handling 1000 req/s, P99 = 1s means **10 users every second** experience a 1-second wait. Average latency would never reveal this.

### Which percentile to use

| Metric | Meaning | Typical use |
|---|---|---|
| P50 | Typical user experience (median) | Baseline health check |
| P95 | What most users see at worst | SLA targets, alert thresholds |
| P99 | Near-worst case | Catching bad tail latency |
| P99.9 | Extreme outliers | Payments, safety-critical, high-stakes APIs |

P95 is the most common SLA metric — e.g. "95% of requests complete in under 500ms."

---

## The Throughput / Latency Trade-off

Improving throughput often increases latency for individual requests, and vice versa.

The clearest example is **batching**:

```
Without batching:
  Request arrives → process immediately → respond in 20ms
  Throughput: 50 req/s (limited by single-request processing)

With batching (wait for 10 requests, process together):
  Request arrives → wait up to 50ms for 9 more → process batch → respond
  Latency: 20ms + up to 50ms wait = up to 70ms per request
  Throughput: 10× more work per processing cycle → much higher req/s
```

Batching is exactly the trade-off [vLLM](../../ai/infrastructure/vllm.md) makes for [LLM](../../ai/generation/llm.md) inference — it queues incoming requests and processes them together on the GPU (continuous batching), dramatically increasing token throughput at the cost of slightly higher P95 latency for the first request in each batch.

---

## In AI / LLM Systems

[LLM](../../ai/generation/llm.md) systems have two additional latency metrics specific to streaming:

| Metric | Definition |
|---|---|
| **TTFT** (Time to First Token) | How long from request sent until the first token arrives — what the user perceives as "responsiveness" |
| **TPOT** (Time Per Output Token) | How long each subsequent token takes — determines how fast text streams on screen |
| **Token throughput** | Total tokens generated per second across all concurrent requests |

A well-tuned [vLLM](../../ai/infrastructure/vllm.md) deployment optimises for token throughput (GPU utilisation) while keeping TTFT low enough that streaming feels responsive.

---

## In Monitoring (Grafana / OpenTelemetry)

When instrumenting a service, always record:

```python
# Track latency as a histogram — not a gauge or counter
# A histogram lets you compute any percentile from one metric
histogram.record(response_time_ms, attributes={"route": "/api/query"})

# Throughput is derived from request count over time
counter.add(1, attributes={"route": "/api/query", "status": "200"})
# rate(request_count[1m]) in Prometheus/Grafana gives req/s
```

Record latency as a **histogram**, not an average. An average stored as a gauge loses the distribution — you can never recover P95 from it later.

---

## Related

- [Observability](../observability/opentelemetry.md) — how to instrument latency histograms and throughput counters
- [Grafana](../observability/grafana.md) — dashboards for visualising P95/P99 latency and req/s
- [Caching Strategies](caching-strategies.md) — the primary lever for reducing latency on read-heavy paths
- [Exponential Backoff and Jitter](../resilience/exponential-backoff-and-jitter.md) — why a request deadline should be sized off P95/P99, not the average
