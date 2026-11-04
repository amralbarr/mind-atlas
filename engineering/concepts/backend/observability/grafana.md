# Grafana

Grafana is a visualization and dashboarding tool — it doesn't collect or store data itself; it queries other systems ([Prometheus](prometheus.md) for metrics, [Loki](grafana-loki.md) for logs, [Jaeger](jaeger.md)/Tempo for traces, or a plain [SQL](../../databases/relational/sql.md) database) and renders the results as dashboards, graphs, and alerts, so operators have one consistent UI across otherwise separate data sources. See [Microservices Technology Stack](../../../overviews/backend/microservices-tech-stack.md#observability-logs-metrics-traces) for how it fits alongside the systems it visualizes.

## Core Concepts

| Term | Meaning |
|---|---|
| **Data source** | A configured connection to a backend Grafana can query ([Prometheus](prometheus.md), Loki, [Elasticsearch](../../databases/search/elasticsearch.md), [PostgreSQL](../../databases/relational/postgresql.md), and dozens more) |
| **Dashboard** | A collection of panels, each backed by a query against one or more data sources |
| **Panel** | A single visualization (a graph, a table, a gauge, a log stream view) |
| **Variable** | A dashboard-level dropdown (e.g. select environment/service) that templates into every panel's query, letting one dashboard serve many services/environments |
| **Alert rule** | A condition evaluated on a schedule against a data source query, notifying a channel (Slack, email, PagerDuty) when it fires |

## Adding a Prometheus Data Source (Provisioning)

```yaml
# provisioning/datasources/prometheus.yml
apiVersion: 1
datasources:
  - name: Prometheus
    type: prometheus
    url: http://prometheus:9090
    isDefault: true
```

Provisioning data sources and dashboards as version-controlled [YAML](../../devops/yaml.md)/[JSON](../../programming/fundamentals/json.md) (rather than clicking through the UI) is the standard pattern once Grafana setup needs to be reproducible across environments.

## A Dashboard Panel Query (Prometheus Data Source)

```promql
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket{service="$service"}[5m]))
```

`$service` here is a dashboard variable — the same panel serves every service without duplicating the dashboard per service.

## Correlating Logs and Metrics

A common pattern: a Grafana dashboard panel showing an error-rate spike (from [Prometheus](prometheus.md)) links directly to a Loki log panel filtered to the same time range and service label — going from "something's wrong" to "here are the actual error log lines" without leaving Grafana or manually correlating timestamps across two separate tools.

## Common Questions

**Does Grafana compete with Kibana?**
> They overlap in role (visualization/dashboards) but differ in scope: Kibana is built specifically for [Elasticsearch](../../databases/search/elasticsearch.md) data. Grafana is data-source-agnostic — one Grafana instance commonly visualizes [Prometheus](prometheus.md) metrics, Loki logs, and trace data side by side, which is why it's the more common choice once a system uses more than one observability backend.

**Is Grafana itself required to use [Prometheus](prometheus.md)?**
> No — [Prometheus](prometheus.md) has its own basic built-in graphing UI for ad-hoc queries, sufficient for quick debugging. Grafana is what's used for the persistent, shared, polished dashboards a team actually relies on day to day.

## Related

- [Microservices Technology Stack](../../../overviews/backend/microservices-tech-stack.md)
- [Prometheus](prometheus.md)
- [Grafana Loki](grafana-loki.md)
- [ELK/EFK Stack](elk-stack.md)
