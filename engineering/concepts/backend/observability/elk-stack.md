# ELK / EFK Stack

The ELK Stack — [Elasticsearch](../../databases/search/elasticsearch.md), Logstash, Kibana (EFK swaps Logstash for Fluentd/Fluent Bit) — is the classic self-hosted centralized-logging pipeline: logs from every service are shipped to one place, indexed for full-text search, and explored through a shared dashboard, instead of SSHing into individual hosts to grep log files. See [Microservices Technology Stack](../../../overviews/backend/microservices-tech-stack.md#observability-logs-metrics-traces) for how this fits alongside metrics and tracing.

## Core Concepts

| Component | Role |
|---|---|
| **[Elasticsearch](../../databases/search/elasticsearch.md)** | The search/storage engine — indexes every log line as a document, enabling fast full-text search and aggregation across huge volumes of logs |
| **Logstash** | A log-processing pipeline: ingests raw logs, parses/enriches/filters them (e.g. extracting fields from an unstructured line via a grok pattern), then forwards to [Elasticsearch](../../databases/search/elasticsearch.md) |
| **Fluentd / Fluent Bit** | Lighter-weight log collectors/forwarders — the "F" in EFK; Fluent Bit especially is popular as a low-overhead per-node log shipper (e.g. a [Kubernetes](../../distributed-systems/kubernetes/ingress.md) DaemonSet) feeding into [Elasticsearch](../../databases/search/elasticsearch.md) |
| **Kibana** | The web UI for searching, visualizing, and building dashboards over data stored in [Elasticsearch](../../databases/search/elasticsearch.md) |
| **Beats** | Lightweight, single-purpose shippers (Filebeat for logs, Metricbeat for metrics) — often used instead of a full Logstash pipeline when minimal processing is needed |

## The Pipeline

```text
Service logs (stdout / log files)
        ↓
Filebeat / Fluent Bit (lightweight shipper, one per host/node)
        ↓
Logstash / Fluentd (parsing, filtering, enrichment — optional)
        ↓
Elasticsearch (indexed storage)
        ↓
Kibana (search, dashboards, alerts)
```

## Running It (Docker Compose, Minimal)

```yaml
services:
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.15.0
    environment:
      - discovery.type=single-node
      - xpack.security.enabled=false
    ports: ["9200:9200"]

  kibana:
    image: docker.elastic.co/kibana/kibana:8.15.0
    environment:
      - ELASTICSEARCH_HOSTS=http://elasticsearch:9200
    ports: ["5601:5601"]
```

A minimal Filebeat config to ship container logs into Elasticsearch directly (skipping Logstash entirely for simple cases):

```yaml
# filebeat.yml
filebeat.inputs:
  - type: container
    paths: ["/var/lib/docker/containers/*/*.log"]
output.elasticsearch:
  hosts: ["elasticsearch:9200"]
```

## Querying in Elasticsearch (Kibana Query Language)

```text
service.name: "orders-service" AND log.level: "error" AND @timestamp >= "now-1h"
```

## Common Questions

**Why is this called ELK sometimes and EFK other times?**
> Same role, different collector: Logstash is heavier and more feature-rich for parsing/enrichment (the "L"); Fluentd/Fluent Bit are lighter-weight alternatives more common in [Kubernetes](../../distributed-systems/kubernetes/ingress.md) (the "F"), especially as a per-node DaemonSet where resource overhead per node matters. Elasticsearch and Kibana stay the same either way.

**How does this compare to [Grafana Loki](grafana-loki.md) for logs?**
> Elasticsearch indexes the full text of every log line, which is powerful but storage/compute-heavy at scale. [Loki](grafana-loki.md) only indexes metadata (labels) and stores log content compressed and unindexed, trading some full-text search flexibility for dramatically lower cost — see [Grafana Loki](grafana-loki.md) for the fuller comparison.

## Related

- [Microservices Technology Stack](../../../overviews/backend/microservices-tech-stack.md)
- [Grafana Loki](grafana-loki.md)
- [Prometheus](prometheus.md)
- [Grafana](grafana.md)
- [OpenTelemetry](opentelemetry.md)
