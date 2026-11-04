# Helm

Helm is [Kubernetes](ingress.md)' package manager — it bundles a set of [YAML](../../devops/yaml.md) manifest templates plus a values file into a single versioned, installable unit called a **chart**, instead of hand-maintaining raw `kubectl apply -f` manifests per environment. See [Kubernetes Basics](kubernetes-basics.md) for the underlying primitives (Pods, Deployments, Services) a chart ultimately generates.

## Core Concepts

| Term | Meaning |
|---|---|
| **Chart** | A packaged set of [Kubernetes](ingress.md) manifest templates plus metadata (`Chart.yaml`) — the unit Helm installs, upgrades, and rolls back as one |
| **Values (`values.yaml`)** | The default configuration a chart's templates are rendered with — overridable per install/environment without editing the templates themselves |
| **Release** | A named, versioned instance of a chart installed into a cluster — the same chart can be installed multiple times under different release names |
| **Template** | A manifest with Go-template placeholders (`{{ .Values.replicaCount }}`) filled in from the values file at install time |
| **Repository** | A hosted collection of packaged charts (like npm for Node.js packages), added via `helm repo add` |

## Installing a Chart

```bash
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update

helm install my-postgres bitnami/postgresql \
  --set auth.postgresPassword=changeme \
  --set primary.persistence.size=10Gi
```

`my-postgres` is the release name; everything after `--set` overrides specific values without needing a custom values file for small overrides.

## A Values File Override

```yaml
# values-prod.yaml
replicaCount: 3
resources:
  requests:
    cpu: 500m
    memory: 512Mi
```

```bash
helm install my-app ./my-app-chart -f values-prod.yaml
```

## Upgrading and Rolling Back

```bash
helm upgrade my-app ./my-app-chart -f values-prod.yaml

helm history my-app          # list past releases
helm rollback my-app 2       # revert to revision 2
```

Because Helm tracks every release's rendered manifests as a revision, `rollback` restores the exact prior state — this is the core value over hand-applying [YAML](../../devops/yaml.md), where there's no built-in history to revert to.

## A Minimal Chart Structure

```text
my-app-chart/
├── Chart.yaml          # name, version, description
├── values.yaml         # default configuration
└── templates/
    ├── deployment.yaml # uses {{ .Values.* }} placeholders
    └── service.yaml
```

## Common Questions

**Is Helm required to use [Kubernetes](ingress.md) at all?**
> No — `kubectl apply` on raw manifests works fine for a handful of services. Helm earns its complexity once the same application needs to be deployed repeatedly across environments (dev/staging/prod) with different configuration, or when installing third-party software (databases, monitoring stacks) that ships as a pre-built chart rather than raw manifests you'd otherwise have to write yourself.

**How does Helm relate to [Argo CD](argo-cd.md)?**
> They solve different problems and are commonly used together: Helm defines *what* a release looks like (templated manifests + values); [Argo CD](argo-cd.md) decides *when* and *how* that gets applied to a live cluster, by continuously syncing the cluster to match a Git repo (which can itself reference a Helm chart and values file).

## Related

- [Kubernetes Basics](kubernetes-basics.md)
- [Argo CD](argo-cd.md)
- [Ansible](../../cloud/iac/ansible.md) — a config-management tool solving a related but distinct problem (arbitrary hosts, not [Kubernetes](ingress.md)-specific)
