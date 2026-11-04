# Zipkin

Zipkin is a distributed tracing system, originally built at Twitter — one of the earliest widely-adopted tools for the same problem [Jaeger](jaeger.md) solves: collecting and visualizing traces (a request's path across every service it touched) tied together by a shared trace ID. See [Microservices Technology Stack](../../../overviews/backend/microservices-tech-stack.md#observability-logs-metrics-traces) for how tracing fits alongside logs and metrics.

## Core Concepts

| Term | Meaning |
|---|---|
| **Trace** | The full path of one request across services |
| **Span** | One timed unit of work within a trace (a service call, a DB query), with a parent span linking it into the trace tree |
| **B3 propagation** | Zipkin's own trace-context header format (`X-B3-TraceId`, `X-B3-SpanId`) — predates the W3C `traceparent` standard [OpenTelemetry](opentelemetry.md) uses, though modern setups can bridge between the two |
| **Reporter** | The client-side component that batches and sends completed spans to the Zipkin collector |
| **Storage backend** | Where Zipkin persists spans for querying — in-memory (dev only), [MySQL](../../databases/relational/mysql.md), [Elasticsearch](../../databases/search/elasticsearch.md), or [Cassandra](../../databases/nosql/cassandra.md) for production |

## Running It (Docker, In-Memory Storage)

```bash
docker run -d --name zipkin -p 9411:9411 openzipkin/zipkin
```

The UI is at `http://localhost:9411` — search traces by service name, span name, duration, or tags, and view a trace's full timeline/waterfall view across services.

## Instrumenting a Service (via OpenTelemetry, Exporting to Zipkin)

```javascript
const { NodeSDK } = require('@opentelemetry/sdk-node');
const { ZipkinExporter } = require('@opentelemetry/exporter-zipkin');

const sdk = new NodeSDK({
  traceExporter: new ZipkinExporter({ url: 'http://zipkin:9411/api/v2/spans' }),
});
sdk.start();
```

As with [Jaeger](jaeger.md), new instrumentation typically goes through [OpenTelemetry](opentelemetry.md) rather than Zipkin's own older native client libraries, so the choice of Zipkin vs. [Jaeger](jaeger.md) becomes primarily a backend/storage decision rather than something baked into application code.

## Reading a Trace

```text
[orders-service: POST /orders]  ─── 180ms total
   ├── [orders-service: validate]           ─ 5ms
   ├── [payment-service: charge]             ─ 120ms  ← the actual bottleneck
   └── [notification-service: send email]    ─ 15ms
```

A trace view like this is what turns "this request was slow" into "this request was slow *specifically because of the payment-service call*" — without it, each service's logs would show the delay independently with no way to connect them into one story.

## Common Questions

**Is Zipkin considered legacy compared to [Jaeger](jaeger.md)?**
> Not exactly legacy, but generally less actively differentiated — many teams now default to [Jaeger](jaeger.md) for new setups given its more active development and richer feature set, while Zipkin remains common in systems that adopted it early and haven't had a reason to migrate. Functionally, for the core "record and view traces" use case, they're close to interchangeable.

**Do Zipkin and [Jaeger](jaeger.md) require separate instrumentation in application code?**
> Not with [OpenTelemetry](opentelemetry.md) — code is instrumented once against [OpenTelemetry](opentelemetry.md)'s vendor-neutral API, and the exporter configuration (pointing at Zipkin vs. Jaeger vs. a commercial backend) is a deployment-level decision, not an application-code rewrite.

## Related

- [Microservices Technology Stack](../../../overviews/backend/microservices-tech-stack.md)
- [Jaeger](jaeger.md)
- [OpenTelemetry](opentelemetry.md)
