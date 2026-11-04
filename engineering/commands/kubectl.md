# kubectl Commands

The [Kubernetes](../concepts/distributed-systems/kubernetes/ingress.md) CLI commands used daily for inspecting and managing a cluster. See [Kubernetes Basics](../concepts/distributed-systems/kubernetes/kubernetes-basics.md) for the underlying concepts (Pod, Deployment, Service, [Ingress](../concepts/distributed-systems/kubernetes/ingress.md)) these commands operate on.

## Context & Cluster Info

```bash
kubectl cluster-info
kubectl config get-contexts                # list available clusters/contexts
kubectl config use-context <name>          # switch which cluster kubectl targets
kubectl get nodes                          # list nodes in the cluster
```

## Getting & Describing Resources

```bash
kubectl get pods                           # list pods in the current namespace
kubectl get pods -A                        # list pods across ALL namespaces
kubectl get pods -o wide                   # include node/IP columns
kubectl get deployments
kubectl get services
kubectl get all                            # pods, services, deployments, replicasets at once

kubectl get pods | grep api                # quick name search
kubectl get pods -l app=api                # the "real" way — filter by label selector, not just name text
kubectl get pods --field-selector=status.phase=Running   # filter by a resource field instead of a label

kubectl describe pod <name>                # full details + recent events — the first thing to run when a pod misbehaves
kubectl get pod <name> -o yaml             # the pod's full manifest as Kubernetes actually stored it
```

## Logs & Debugging

```bash
kubectl logs <pod>                         # a pod's stdout/stderr
kubectl logs -f <pod>                      # follow live
kubectl logs <pod> -c <container>          # a specific container, for a multi-container pod
kubectl logs <pod> --previous              # logs from the PREVIOUS instance, after a crash/restart

kubectl exec -it <pod> -- bash             # shell into a running pod
kubectl port-forward <pod> 8080:80         # tunnel a local port to a port inside the pod
```

## Applying & Managing Manifests

```bash
kubectl apply -f deployment.yaml           # create or update resources from a manifest file
kubectl apply -f ./manifests/              # apply every manifest in a directory
kubectl delete -f deployment.yaml          # delete whatever that manifest describes
kubectl delete pod <name>                  # delete a single resource directly

kubectl diff -f deployment.yaml            # preview what `apply` would change, without applying it
```

`apply` is declarative ([Kubernetes](../concepts/distributed-systems/kubernetes/ingress.md) reconciles the cluster to match the file) — see [Infrastructure as Code](../concepts/cloud/iac/infrastructure-as-code.md) for the same declarative-vs-imperative distinction applied more generally.

## Scaling & Rollouts

```bash
kubectl scale deployment <name> --replicas=5
kubectl rollout status deployment <name>   # watch a rollout's progress
kubectl rollout history deployment <name>  # see previous revisions
kubectl rollout undo deployment <name>     # roll back to the previous revision
```

## Common Questions

**Why does `kubectl get pods` sometimes show `CrashLoopBackOff`?**
> The container is starting, crashing, and being restarted repeatedly, with [Kubernetes](../concepts/distributed-systems/kubernetes/ingress.md) applying an increasing delay between restart attempts (the "backoff") instead of retrying instantly forever. `kubectl logs <pod> --previous` and `kubectl describe pod <pod>` are the two commands to run immediately — the former shows why the process actually exited, the latter shows [Kubernetes](../concepts/distributed-systems/kubernetes/ingress.md)' own view of recent events (e.g. an OOM-kill, a failed readiness probe).

## Related

- [Kubernetes Basics](../concepts/distributed-systems/kubernetes/kubernetes-basics.md)
- [Helm](../concepts/distributed-systems/kubernetes/helm.md)
- [Health, Liveness & Readiness Checks](../concepts/backend/architecture/health-liveness-readiness.md)
- [Docker Commands](docker.md)
