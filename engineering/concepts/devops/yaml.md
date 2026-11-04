# YAML

## What Is It

YAML (YAML Ain't Markup Language) is a human-readable data [serialization](../programming/fundamentals/serialization.md) format used almost universally for configuration files. It is a superset of [JSON](../programming/fundamentals/json.md) — every valid [JSON](../programming/fundamentals/json.md) document is valid YAML — but its indentation-based syntax is far easier to read and write by hand.

You will encounter YAML in virtually every layer of the modern engineering stack: [CI/CD](ci-cd.md) pipeline definitions, [Docker Compose](../containers/docker-compose.md) files, [Kubernetes](../distributed-systems/kubernetes/ingress.md) manifests, [Ansible](../cloud/iac/ansible.md) playbooks, [OpenAPI](../backend/api/openapi.md) specs, [Helm](../distributed-systems/kubernetes/helm.md) charts, and pre-commit configuration.

## Core Syntax

**Mappings (key-value pairs)**

```yaml
name: my-service
port: 8080
debug: false
```

**Sequences (lists)**

```yaml
dependencies:
  - fastapi
  - uvicorn
  - pydantic
```

**Nested structures**

```yaml
database:
  host: localhost
  port: 5432
  name: mydb
```

**Multi-line strings**

```yaml
# Literal block (| preserves newlines)
script: |
  echo "step 1"
  echo "step 2"

# Folded block (> folds newlines into spaces)
description: >
  This is a long description
  that wraps across lines.
```

**Anchors and aliases (DRY reuse)**

```yaml
defaults: &defaults
  image: python:3.12
  restart: unless-stopped

service-a:
  <<: *defaults
  ports:
    - "8001:8000"

service-b:
  <<: *defaults
  ports:
    - "8002:8000"
```

## Common Gotchas

**Bare boolean-like values** — YAML 1.1 (used by many tools) parses `yes`, `no`, `on`, `off`, `true`, `false` as booleans. This silently breaks things like country codes or feature-flag strings. Quote them if you mean a string:

```yaml
country: "NO"   # without quotes, parsed as false in YAML 1.1
enabled: "yes"  # without quotes, parsed as true
```

**Tabs are not valid indentation** — YAML requires spaces. A tab character in indentation causes a parse error. Most editors enforce this automatically for `.yaml`/`.yml` files.

**Indentation level matters** — shifting a block one space to the left or right changes its meaning entirely. Always use a consistent indent width (2 spaces is the universal convention).

**Strings that look like other types** — version numbers (`1.0`), port numbers (`8080`), and ISO dates (`2024-01-01`) may be coerced to float, int, or date depending on the parser. Quote them when you need them treated as strings.

## .yaml vs .yml — File Extension

**The one-line answer:** no functional difference. `.yaml` and `.yml` are the same format; only the extension differs.

**Why two extensions exist:**
- `.yml` is a legacy shorthand from the DOS/Windows 8.3 filename era (max 3-character extensions)
- `.yaml` is the full extension preferred by the official YAML spec at yaml.org
- Every YAML parser accepts both without configuration

**Convention by tool — follow the tool's own default, never mix within a project:**

| Tool | Default extension | Notes |
|---|---|---|
| [GitHub Actions](github-actions.md) | `.yml` | `/.github/workflows/*.yml` |
| [Docker](../containers/docker.md) Compose | `.yml` | `docker-compose.yml` |
| [Kubernetes](../distributed-systems/kubernetes/ingress.md) manifests | `.yaml` | Official docs use `.yaml` |
| [Ansible](../cloud/iac/ansible.md) playbooks | `.yml` | Community convention |
| [OpenAPI / Swagger](../backend/api/openapi.md) spec | `.yaml` | Official examples use `.yaml` |
| [Helm](../distributed-systems/kubernetes/helm.md) charts | `.yaml` | `templates/*.yaml` |
| pre-commit config | `.yaml` | `.pre-commit-config.yaml` |

**Rule of thumb:** match whatever the tool ecosystem or your team already uses. If starting from scratch, `.yaml` is more explicit and readable; `.yml` is more common in CI tooling.

## Related

- [CI/CD](ci-cd.md) — YAML is the primary syntax for defining [CI/CD](ci-cd.md) pipelines
- [GitHub Actions](github-actions.md) — workflow files are YAML (`.github/workflows/*.yml`)
- [Docker Compose](../containers/docker-compose.md) — service definitions live in a YAML file
- [Kubernetes Basics](../distributed-systems/kubernetes/kubernetes-basics.md) — all resource manifests are YAML
- [Helm](../distributed-systems/kubernetes/helm.md) — chart templates and values files are YAML
- [Ansible](../cloud/iac/ansible.md) — playbooks and inventory are YAML
