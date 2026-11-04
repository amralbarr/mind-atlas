# OCI (Open Container Initiative)

## What Is It

The **Open Container Initiative** is an open governance project under the Linux Foundation that defines vendor-neutral standards for container **image format** and **runtime behavior**. It exists so that a container image built by one tool works, unmodified, on any other compliant tool — the same way a `.zip` file opens the same regardless of which program created it.

OCI was formed in 2015, with [Docker](docker.md) donating its container format and runtime code (`runc`) as the starting point.

## The Three Specs

| Spec | Defines |
|---|---|
| **Image spec** | The on-disk/on-wire format of a container image: a manifest, a config file, and a set of filesystem layers |
| **Runtime spec** | How a container is actually started from an unpacked image — the config file format specifying namespaces, cgroups, mounts, and the process to launch |
| **Distribution spec** | How images are pushed to and pulled from a registry (what [Docker](docker.md) Hub, GitHub Container Registry, [Azure](../cloud/azure/azure.md) Container Registry, etc. all implement) |

```
OCI Image  →  unpacked into a filesystem bundle  →  run by an OCI Runtime (e.g. runc)
```

## Why It Matters

Before OCI, "container" meant "[Docker](docker.md)" — there was no standard, so tooling and images were tied to one vendor's implementation. OCI decoupled the *format* from the *tool*:

- An image pulled from [Docker](docker.md) Hub can be run by [Docker](docker.md), [Podman](podman.md), containerd, or a [Kubernetes](../distributed-systems/kubernetes/ingress.md) node's `CRI` runtime — all without rebuilding it.
- `docker build` produces an OCI image. `podman run` can run that exact same image, byte for byte.
- [Kubernetes](../distributed-systems/kubernetes/ingress.md) doesn't run "Docker containers" — it runs OCI images through whatever OCI-compliant runtime the node uses (commonly `containerd` + `runc`).

This is the standard that makes "just use Docker's image format, but a different, more secure engine" (i.e. switching to [Podman](podman.md)) a realistic option rather than a rewrite: the image doesn't need to change, only the tool that runs it does.

## Image Versioning & Registries

The distribution spec is what lets you point at *any* OCI-compliant registry — GitHub Container Registry, Docker Hub, a private registry — through configuration rather than being locked to one vendor's API. Two practices matter regardless of which registry you use:

- **Never deploy `:latest` to production.** `latest` is just a mutable tag pointing at whatever was pushed most recently — it gives you no way to know what's actually running, no way to roll back to a specific version, and no guarantee that redeploying today pulls the same image as redeploying yesterday.
- **Use immutable, meaningful tags instead** — semantic versions (`1.3.0`) or a Git commit SHA (`git-abcd123`) so a running container's tag always identifies exactly which build it is, and a rollback is just "redeploy the previous tag."

## Related

- [Docker](docker.md)
- [Container Isolation](container-isolation.md)
- [Podman](podman.md)
- [Kubernetes Basics](../distributed-systems/kubernetes/kubernetes-basics.md)
- [systemctl (systemd) Commands § Running a Docker Container as a systemd Service](../../commands/systemctl.md#running-a-docker-container-as-a-systemd-service) — applies the pinned-tag guidance above to a unit file's `ExecStartPre`
