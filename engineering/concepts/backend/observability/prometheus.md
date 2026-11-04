# Prometheus

Prometheus is the de facto standard open-source metrics collection and storage system for cloud-native systems — it **pulls** (scrapes) metrics from services on a schedule, stores them as time series, and provides a query language (PromQL) for aggregating and alerting on them. See [Microservices Technology Stack](../../../overviews/backend/microservices-tech-stack.md#observability-logs-metrics-traces) for how metrics fit alongside logs and traces.

## Core Concepts

| Term | Meaning |
|---|---|
| **Scraping** | Prometheus polls each configured target's `/metrics` [HTTP](../../networking/http.md) endpoint on an interval and stores the returned samples — a pull model, unlike most logging pipelines, which push |
| **Metric types** | **Counter** (only increases, e.g. total requests), **Gauge** (goes up/down, e.g. current memory), **Histogram** (buckets observations, e.g. request latency distribution), **Summary** (similar to histogram, with client-side quantile calculation) |
| **Label** | A key-value pair on a metric (e.g. `method="POST", status="500"`) — the dimension PromQL slices and aggregates by |
| **PromQL** | Prometheus's query language for selecting, filtering, and aggregating time series |
| **Alertmanager** | A separate component that receives alerts fired by Prometheus rules and handles routing/deduplication/silencing to Slack, PagerDuty, email, etc. |

## Exposing Metrics (Node.js, prom-client)

```javascript
const client = require('prom-client');
const register = new client.Registry();

const httpRequestDuration = new client.Histogram({
  name: 'http_request_duration_seconds',
  help: 'HTTP request duration in seconds',
  labelNames: ['method', 'route', 'status'],
  registers: [register],
});

app.get('/metrics', async (req, res) => {
  res.set('Content-Type', register.contentType);
  res.end(await register.metrics());
});
```

## Scrape Configuration

```yaml
# prometheus.yml
scrape_configs:
  - job_name: 'orders-service'
    scrape_interval: 15s
    static_configs:
      - targets: ['orders-service:3000']
```

In [Kubernetes](../../distributed-systems/kubernetes/ingress.md), targets are typically discovered automatically via `kubernetes_sd_configs` rather than a static list, so newly deployed pods get scraped without manual config changes.

## PromQL Examples

```promql
# Requests per second over the last 5 minutes, by status code
sum(rate(http_request_duration_seconds_count[5m])) by (status)

# 95th-percentile request latency
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))

# Alert condition: error rate above 5% over 5 minutes
sum(rate(http_request_duration_seconds_count{status=~"5.."}[5m]))
  / sum(rate(http_request_duration_seconds_count[5m])) > 0.05
```

## An Alerting Rule

```yaml
groups:
  - name: orders-service
    rules:
      - alert: HighErrorRate
        expr: |
          sum(rate(http_request_duration_seconds_count{status=~"5.."}[5m]))
          / sum(rate(http_request_duration_seconds_count[5m])) > 0.05
        for: 5m
        labels:
          severity: critical
```

## Common Questions

**Why does Prometheus pull metrics instead of services pushing them?**
> Pulling means Prometheus itself controls scrape timing and can detect a target that's down (a failed scrape is itself a signal), and services don't need to know where Prometheus lives or handle delivery/retry logic for pushing metrics out. Short-lived jobs that don't live long enough to be scraped use the separate **Pushgateway** component as an exception to this model.

**Does Prometheus replace the need for a dashboard tool?**
> No — Prometheus includes a basic built-in expression browser, but real dashboards are almost always built in [Grafana](grafana.md), which queries Prometheus (and other data sources) and renders the visualizations Prometheus itself doesn't provide.

## Related

- [Microservices Technology Stack](../../../overviews/backend/microservices-tech-stack.md)
- [Grafana](grafana.md)
- [Grafana Loki](grafana-loki.md)
- [OpenTelemetry](opentelemetry.md)
- [GPU-Aware Scheduling](../../ai/infrastructure/gpu-scheduling.md)
