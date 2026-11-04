# Argo CD

Argo CD is a GitOps continuous-delivery tool for [Kubernetes](ingress.md) — it continuously watches a Git repository for the desired cluster state and automatically (or on approval) syncs the live cluster to match, so a deployment happens by merging a Git commit rather than running `kubectl apply` or a CI script by hand. See [Kubernetes Basics](kubernetes-basics.md) for the primitives it's ultimately reconciling.

## Core Concepts

| Term | Meaning |
|---|---|
| **GitOps** | The practice of treating a Git repo as the single source of truth for a system's desired state, with automation reconciling reality to match it |
| **Application** | Argo CD's core resource — points at a Git path (which can be raw manifests, a [Helm](helm.md) chart, or a Kustomize overlay) and a target cluster/namespace |
| **Sync** | The act of applying the difference between Git's desired state and the cluster's actual state |
| **Sync policy** | `manual` (a human clicks/approves sync) or `automated` (Argo CD applies changes as soon as they land in Git, optionally with `selfHeal` to also revert manual `kubectl` drift) |
| **Drift** | Any difference between what's declared in Git and what's actually running in the cluster — Argo CD's UI surfaces this directly, which plain CI-based deployment doesn't |

## Defining an Application

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: my-app
  namespace: argocd
spec:
  project: default
  source:
    repoURL: https://github.com/org/my-app-manifests.git
    targetRevision: main
    path: k8s/production
  destination:
    server: https://kubernetes.default.svc
    namespace: production
  syncPolicy:
    automated:
      prune: true      # delete resources removed from Git
      selfHeal: true    # revert any manual drift back to Git's state
```

```bash
kubectl apply -f application.yaml
argocd app sync my-app     # manual sync, if not automated
argocd app get my-app      # current sync/health status
```

## Why This Changes the Deployment Flow

```text
Without GitOps:
Developer → CI pipeline → kubectl apply / helm upgrade → cluster
(the cluster's actual state lives only in whoever/whatever last ran a command)

With Argo CD:
Developer → git push → Argo CD notices the diff → syncs cluster to match
(the cluster's state is always derivable by reading the Git repo)
```

A rollback becomes `git revert` instead of remembering and re-running the prior deployment command — and because Argo CD is a controller actively watching the cluster (not a one-shot CI job), it can also detect and correct someone manually patching a resource with `kubectl edit` (`selfHeal`).

## Common Questions

**How is this different from a CI pipeline that runs `kubectl apply` on merge?**
> A CI-triggered apply is a one-shot push at merge time — nothing continues watching afterward. Argo CD is a long-running controller that keeps comparing Git to the live cluster on an ongoing basis, catching both new commits *and* out-of-band drift, and it exposes a live diff/health view per application rather than only a pipeline log.

**Does adopting Argo CD require [Helm](helm.md)?**
> No — an Argo CD `Application` can point at plain [YAML](../../devops/yaml.md) manifests, a Kustomize overlay, or a [Helm](helm.md) chart interchangeably. [Helm](helm.md) and Argo CD solve different layers of the problem and are commonly combined, but neither requires the other.

## Related

- [Kubernetes Basics](kubernetes-basics.md)
- [Helm](helm.md)
- [Ansible](../../cloud/iac/ansible.md)
