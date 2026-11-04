# Jaeger

Jaeger is a distributed tracing system, originally built at Uber — it collects, stores, and visualizes **traces**: the full path one request took across every service it touched, tied together by a shared trace ID, so a slow or failing request across five services can be inspected as one connected timeline instead of five unrelated log entries. See [Microservices Technology Stack](../../../overviews/backend/microservices-tech-stack.md#observability-logs-metrics-traces) for how tracing fits alongside logs and metrics.

## Core Concepts

| Term | Meaning |
|---|---|
| **Trace** | The complete record of one request's journey across every service it passed through |
| **Span** | One unit of work within a trace — e.g. "Order Service calls Payment Service" — with a start time, duration, and metadata (tags, logs) |
| **Trace context propagation** | The trace ID and current span ID are passed along in request headers (`traceparent` in the W3C standard) from service to service, which is what actually links spans back into one trace |
| **Sampling** | Recording every single trace is often too expensive at scale — Jaeger supports sampling strategies (e.g. record 1% of traces, or always record traces that hit an error) to control volume |
| **Jaeger Agent / Collector** | The Agent runs alongside a service (or as a sidecar) and batches/forwards spans to the Collector, which stores them (commonly in [Elasticsearch](../../databases/search/elasticsearch.md) or [Cassandra](../../databases/nosql/cassandra.md)) for querying in the UI |

## Instrumenting a Service (via OpenTelemetry)

Modern Jaeger deployments receive spans via the [OpenTelemetry](opentelemetry.md) protocol rather than Jaeger's own older client libraries:

```javascript
const { NodeSDK } = require('@opentelemetry/sdk-node');
const { OTLPTraceExporter } = require('@opentelemetry/exporter-trace-otlp-http');

const sdk = new NodeSDK({
  traceExporter: new OTLPTraceExporter({ url: 'http://jaeger:4318/v1/traces' }),
});
sdk.start();
```

## Running Jaeger (Docker, All-in-One for Local Dev)

```bash
docker run -d --name jaeger \
  -p 16686:16686 \
  -p 4318:4318 \
  jaegertracing/all-in-one:latest
```

`16686` serves the UI (`http://localhost:16686`) where traces can be searched by service, operation, duration, or tags; `4318` receives OTLP trace data.

## Manually Creating a Span

```javascript
const tracer = require('@opentelemetry/api').trace.getTracer('orders-service');

async function createOrder(data) {
  return tracer.startActiveSpan('createOrder', async (span) => {
    span.setAttribute('order.id', data.id);
    try {
      // ... business logic
    } finally {
      span.end();
    }
  });
}
```

## Common Questions

**How is Jaeger different from [Zipkin](zipkin.md)?**
> They solve the same problem and are largely interchangeable at a conceptual level — Jaeger has generally become the more actively developed and CNCF-graduated option, with somewhat richer UI/sampling features, while [Zipkin](zipkin.md) is simpler to run and still common in existing deployments. Since both now commonly receive data via [OpenTelemetry](opentelemetry.md), switching between them is mostly a backend/storage choice rather than a re-instrumentation effort.

**Do I need Jaeger's own client libraries, or does [OpenTelemetry](opentelemetry.md) replace them?**
> For new instrumentation, use [OpenTelemetry](opentelemetry.md) — it's the vendor-neutral standard, and Jaeger's own older native clients are effectively legacy at this point. [OpenTelemetry](opentelemetry.md) can export to Jaeger, [Zipkin](zipkin.md), [Prometheus](prometheus.md), or a commercial backend without re-instrumenting code if the backend changes later.

## Related

- [Microservices Technology Stack](../../../overviews/backend/microservices-tech-stack.md)
- [Zipkin](zipkin.md)
- [OpenTelemetry](opentelemetry.md)
- [Prometheus](prometheus.md)
