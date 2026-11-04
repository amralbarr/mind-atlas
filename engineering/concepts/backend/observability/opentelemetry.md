# OpenTelemetry

OpenTelemetry (OTel) is a vendor-neutral standard — an API, SDK, and wire protocol — for generating and exporting the three pillars of observability: **traces**, **metrics**, and **logs**. Application code is instrumented once against OpenTelemetry rather than against a specific backend's proprietary SDK. The same instrumented data exports to [Jaeger](jaeger.md), [Prometheus](prometheus.md), [Grafana](grafana.md), or a commercial platform by changing configuration, not code.

---

## The Three Pillars

| Pillar | What it answers | Storage backend |
|---|---|---|
| **Traces** | What happened to this specific request, across all services? | [Jaeger](jaeger.md), [Grafana](grafana.md) Tempo, [Zipkin](zipkin.md) |
| **Metrics** | How is the system behaving in aggregate right now? | [Prometheus](prometheus.md), [Grafana](grafana.md) |
| **Logs** | What was the exact event or error at this timestamp? | Loki, [Elasticsearch](../../databases/search/elasticsearch.md) |

OpenTelemetry instruments all three with one SDK and one export pipeline.

---

## Traces and Spans

A **trace** is the full journey of one request through a distributed system. A **span** is one unit of work within that trace — a single service's handling of part of the request.

```
Trace: user query → RAG pipeline
  │
  ├── Span: POST /api/query (FastAPI)           0ms → 320ms
  │     ├── Span: embed_query (sentence-transformers)  5ms → 40ms
  │     ├── Span: pgvector_search                     42ms → 180ms
  │     └── Span: llm_generate (vLLM)                185ms → 315ms
  │           └── Span: tokenize_prompt              185ms → 190ms
```

Every span carries:
- `trace_id` — same across the entire request chain
- `span_id` — unique to this span
- `parent_span_id` — links child spans to parents
- `start_time`, `end_time`
- `attributes` — key-value metadata ([HTTP](../../networking/http.md) method, DB query, model name)
- `status` — OK, ERROR
- `events` — timestamped log messages attached to the span

The `trace_id` is the correlation ID that links all spans across all services for one request.

---

## Context Propagation

Trace context travels between services via [HTTP](../../networking/http.md) headers. The parent service injects the trace context into outgoing requests; the child service extracts it and continues the same trace.

```
Service A                           Service B
  ──────────────────────────────────────────────────────
  span = tracer.start_span("call_b")
  inject headers:                  extract headers:
    traceparent: 00-{trace_id}-     traceparent →
                    {span_id}-01    parent_span_id = span_A_id
                                    new span = child of span_A
  ──────────────────────────────────────────────────────
```

OpenTelemetry handles injection/extraction automatically when using auto-instrumentation for [HTTP](../../networking/http.md) clients (requests, httpx, axios, fetch).

The standard header is `traceparent` (W3C Trace Context spec):
```
traceparent: 00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01
              ^  ^trace_id (128-bit hex)              ^span_id (64-bit)  ^flags
```

---

## Metrics

Three instrument types cover all measurement cases:

### Counter
Monotonically increasing. Measures totals.

```python
from opentelemetry import metrics

meter = metrics.get_meter("rag_service")
query_counter = meter.create_counter(
    "rag.queries.total",
    description="Total RAG queries processed",
)

# In request handler:
query_counter.add(1, {"tenant_id": tenant_id, "status": "success"})

# In Prometheus/Grafana:
# rate(rag_queries_total[1m])  →  queries per second
```

### Gauge
Current value at a point in time. Measures state, not events.

```python
gpu_memory_gauge = meter.create_observable_gauge(
    "vllm.gpu_memory_used_bytes",
    callbacks=[lambda options: [Observation(get_gpu_memory_used())]],
)
```

### Histogram
Records a distribution of values. **The correct instrument for latency.** Enables computing P50, P95, P99 from one metric.

```python
request_latency = meter.create_histogram(
    "rag.request.duration_ms",
    description="End-to-end RAG query latency",
    unit="ms",
)

start = time.time()
result = await pipeline.query(question)
duration_ms = (time.time() - start) * 1000

request_latency.record(duration_ms, {"route": "/api/query", "tenant_id": tenant_id})

# In Grafana:
# histogram_quantile(0.95, rate(rag_request_duration_ms_bucket[5m]))  →  P95 latency
```

Never record latency as a Gauge or Counter average — you lose the distribution and can never recover P95 from it.

---

## Manual Span Instrumentation

Auto-instrumentation covers [HTTP](../../networking/http.md) and DB calls. Business-meaningful units of work need manual spans:

```python
from opentelemetry import trace

tracer = trace.get_tracer("rag_service")

async def handle_query(question: str, tenant_id: str) -> QueryResult:
    with tracer.start_as_current_span("rag.handle_query") as span:
        span.set_attribute("tenant_id", tenant_id)
        span.set_attribute("question_length", len(question))

        with tracer.start_as_current_span("rag.embed_query"):
            embedding = await embed(question)

        with tracer.start_as_current_span("rag.retrieve") as retrieve_span:
            chunks = await retrieve(embedding, tenant_id)
            retrieve_span.set_attribute("chunks_retrieved", len(chunks))

        with tracer.start_as_current_span("rag.generate") as gen_span:
            answer = await generate(question, chunks)
            gen_span.set_attribute("output_tokens", count_tokens(answer))

        return QueryResult(answer=answer, sources=chunks)
```

In [Jaeger](jaeger.md), this produces a waterfall view of exactly where time was spent — embed vs retrieve vs generate — making bottlenecks immediately visible.

---

## Logging with Trace Correlation

Logs are most useful when they carry the `trace_id` of the current request — so you can jump from a [Jaeger](jaeger.md) trace to the exact log lines for that request.

```python
import logging
from opentelemetry import trace

class TraceIdFilter(logging.Filter):
    def filter(self, record):
        span = trace.get_current_span()
        ctx = span.get_span_context()
        record.trace_id = format(ctx.trace_id, "032x") if ctx.is_valid else "no-trace"
        record.span_id = format(ctx.span_id, "016x") if ctx.is_valid else "no-span"
        return True

# Log output:
# {"level": "INFO", "msg": "Retrieved 5 chunks", "trace_id": "4bf92f35...", "span_id": "00f067aa..."}
```

With `trace_id` in every log line, querying Loki/[Elasticsearch](../../databases/search/elasticsearch.md) for `trace_id=4bf92f35...` returns all log lines from that specific request across every service.

---

## Python Setup (FastAPI)

```python
# otel_setup.py — call once at application startup
from opentelemetry import trace, metrics
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
from opentelemetry.instrumentation.asyncpg import AsyncPGInstrumentor

def setup_telemetry(app, service_name: str, otel_endpoint: str):
    # Traces
    tracer_provider = TracerProvider()
    tracer_provider.add_span_processor(
        BatchSpanProcessor(OTLPSpanExporter(endpoint=otel_endpoint))
    )
    trace.set_tracer_provider(tracer_provider)

    # Metrics
    reader = PeriodicExportingMetricReader(
        OTLPMetricExporter(endpoint=otel_endpoint), export_interval_millis=15000
    )
    metrics.set_meter_provider(MeterProvider(metric_readers=[reader]))

    # Auto-instrumentation
    FastAPIInstrumentor.instrument_app(app)   # HTTP spans for every route
    HTTPXClientInstrumentor().instrument()    # Spans for outgoing HTTP calls
    AsyncPGInstrumentor().instrument()        # Spans for every DB query
```

---

## Node.js Setup (NestJS)

```typescript
// tracing.ts — imported before NestJS bootstrap
import { NodeSDK } from "@opentelemetry/sdk-node";
import { getNodeAutoInstrumentations } from "@opentelemetry/auto-instrumentations-node";
import { OTLPTraceExporter } from "@opentelemetry/exporter-trace-otlp-grpc";
import { OTLPMetricExporter } from "@opentelemetry/exporter-metrics-otlp-grpc";
import { PeriodicExportingMetricReader } from "@opentelemetry/sdk-metrics";

const sdk = new NodeSDK({
  serviceName: "api-gateway",
  traceExporter: new OTLPTraceExporter({ url: process.env.OTEL_ENDPOINT }),
  metricReader: new PeriodicExportingMetricReader({
    exporter: new OTLPMetricExporter({ url: process.env.OTEL_ENDPOINT }),
    exportIntervalMillis: 15_000,
  }),
  instrumentations: [
    getNodeAutoInstrumentations({
      "@opentelemetry/instrumentation-fs": { enabled: false }, // too noisy
    }),
  ],
});

sdk.start();
```

---

## The Collector Pattern

Services export to the Collector; the Collector routes to multiple backends:

```
Service A (Python) ──┐
Service B (Node)   ──┼──►  OTel Collector  ──►  Jaeger   (traces)
Service C (Go)     ──┘                     ──►  Prometheus (metrics)
                                           ──►  Loki      (logs)
```

```yaml
# otel-collector-config.yaml
receivers:
  otlp:
    protocols:
      grpc: { endpoint: 0.0.0.0:4317 }
      http: { endpoint: 0.0.0.0:4318 }

processors:
  batch:
    timeout: 5s

exporters:
  otlp/jaeger:
    endpoint: jaeger:4317
    tls: { insecure: true }
  prometheusremotewrite:
    endpoint: http://prometheus:9090/api/v1/write
  loki:
    endpoint: http://loki:3100/loki/api/v1/push

service:
  pipelines:
    traces:
      receivers: [otlp]
      processors: [batch]
      exporters: [otlp/jaeger]
    metrics:
      receivers: [otlp]
      processors: [batch]
      exporters: [prometheusremotewrite]
    logs:
      receivers: [otlp]
      processors: [batch]
      exporters: [loki]
```

---

## In LLM / AI Systems

[LLM](../../ai/generation/llm.md) systems have domain-specific metrics worth instrumenting explicitly:

```python
# TTFT — Time to First Token
ttft_histogram = meter.create_histogram("llm.ttft_ms", unit="ms")
ttft_histogram.record(ttft_ms, {"model": model_name, "tenant_id": tenant_id})

# TPOT — Time Per Output Token
tpot_histogram = meter.create_histogram("llm.tpot_ms", unit="ms")
tpot_histogram.record(tpot_ms, {"model": model_name})

# Token throughput
tokens_counter = meter.create_counter("llm.output_tokens_total")
tokens_counter.add(output_tokens, {"model": model_name, "tenant_id": tenant_id})

# Groundedness score (from evaluation)
groundedness_histogram = meter.create_histogram("rag.groundedness_score")
groundedness_histogram.record(score, {"tenant_id": tenant_id})
```

These flow to [Grafana](grafana.md) dashboards for GPU utilisation, inference latency percentiles, and per-tenant quality monitoring.

---

## What to Always Instrument

```
Every HTTP endpoint:   duration_ms (histogram), status_code (counter)
Every DB query:        duration_ms (histogram) — usually from auto-instrumentation
Every LLM call:        TTFT, TPOT, token count, model name
Every queue consumer:  processing_duration, lag, error rate
Every external call:   duration_ms, success/failure
Startup:               service_name, version, environment (resource attributes)
```

---

## Related

- [Jaeger](jaeger.md) — the trace storage and visualization backend
- [Grafana](grafana.md) — dashboards built on the metrics OTel exports
- [Throughput and Latency](../architecture/throughput-and-latency.md) — P95/P99 latency measured via OTel histograms
- [Secrets Management](../../cloud/infrastructure/secrets-management.md) — OTEL_ENDPOINT and credentials go in Key Vault, not config files
