# Grafana Loki

Loki is [Grafana](grafana.md) Labs' log-aggregation system, built around a deliberately different tradeoff than [Elasticsearch](../../databases/search/elasticsearch.md): instead of indexing the full text of every log line, Loki only indexes a small set of **labels** (service name, environment, log level) and stores the raw log content compressed and unindexed. Queries filter by label first, then grep the matching compressed chunks — much cheaper to run at scale, at the cost of some full-text search flexibility. See [ELK/EFK Stack](elk-stack.md) for the alternative it's most often compared against.

## Core Concepts

| Term | Meaning |
|---|---|
| **Label** | A key-value pair attached to a log stream (e.g. `app="orders-service"`, `env="prod"`) — this is what Loki actually indexes, not the log text itself |
| **Stream** | The set of all logs sharing an identical label set |
| **LogQL** | Loki's query language — a label selector, optionally piped through text filters/parsers/aggregations, deliberately similar in shape to [Prometheus](prometheus.md)'s PromQL |
| **Promtail / [Grafana](grafana.md) Alloy** | The log-shipping agent that reads logs (files, systemd journal, [Docker](../../containers/docker.md)/[Kubernetes](../../distributed-systems/kubernetes/ingress.md) container logs) and pushes them to Loki, attaching labels along the way |
| **Chunk** | A compressed block of log lines for one stream, stored in [object storage](../../cloud/infrastructure/object-storage.md) (S3, [GCS](../../cloud/infrastructure/gcs.md), or local disk) — this is what keeps Loki's storage cost low relative to [Elasticsearch](../../databases/search/elasticsearch.md) |

## Running It (Docker Compose)

```yaml
services:
  loki:
    image: grafana/loki:3.0.0
    ports: ["3100:3100"]

  promtail:
    image: grafana/promtail:3.0.0
    volumes:
      - /var/log:/var/log
      - ./promtail-config.yml:/etc/promtail/config.yml
    command: -config.file=/etc/promtail/config.yml
```

```yaml
# promtail-config.yml
clients:
  - url: http://loki:3100/loki/api/v1/push
scrape_configs:
  - job_name: system
    static_configs:
      - targets: [localhost]
        labels:
          job: varlogs
          __path__: /var/log/*.log
```

## Querying with LogQL

```logql
{app="orders-service", env="prod"} |= "error"
```

Filters the `orders-service` / `prod` stream to lines containing "error" — the label selector narrows down which streams to scan *before* any text matching happens, which is why Loki queries stay cheap even over huge log volumes, as long as labels are chosen with reasonable cardinality.

```logql
sum(rate({app="orders-service"} |= "error" [5m])) by (env)
```

Counts error-line rate per environment over a 5-minute window — the [Prometheus](prometheus.md)-like aggregation syntax is deliberate, since Loki is designed to live alongside [Prometheus](prometheus.md)/[Grafana](grafana.md) in the same dashboards.

## Common Questions

**Why not just use [Elasticsearch](../../databases/search/elasticsearch.md) for everything?**
> [Elasticsearch](../../databases/search/elasticsearch.md)'s full-text indexing of every log line is expensive to store and compute at high log volume. If most real queries start from "which service/environment" rather than free-text search across everything, Loki's label-first, mostly-unindexed approach is dramatically cheaper for the same log volume — see [ELK/EFK Stack](elk-stack.md).

**What's the risk with Loki labels?**
> High-cardinality labels (e.g. putting a unique request ID or user ID directly in a label instead of the log line) create a huge number of small streams, which defeats Loki's efficiency model — labels should stay low-cardinality (service, environment, log level), with anything higher-cardinality left in the unindexed log text and filtered with LogQL instead.

## Related

- [Microservices Technology Stack](../../../overviews/backend/microservices-tech-stack.md)
- [ELK/EFK Stack](elk-stack.md)
- [Prometheus](prometheus.md)
- [Grafana](grafana.md)
