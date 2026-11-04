# LXC / LXD

## What Is It

**LXC** (Linux Containers) is a lower-level Linux kernel feature/tooling for creating **system containers** — containers that run a full Linux operating system (init system, multiple processes, its own package manager) rather than a single application. **LXD** is a daemon built on top of LXC that manages these containers with a friendlier CLI and API, similar to how a hypervisor manages VMs.

```
LXC → the underlying mechanism for creating system containers
LXD → a management daemon built on top of LXC (easier CLI, remote API, images, snapshots)
```

## System Containers vs Application Containers

This is the core distinction from [Docker](docker.md):

| | LXC/LXD (system containers) | [Docker](docker.md) (application containers) |
|---|---|---|
| Runs | An entire OS userspace — init system, multiple services, [SSH](../protocols/ssh.md), cron, its own logs | One application process (plus maybe a couple of tightly coupled helper processes) |
| Lifespan | Long-lived, treated like a persistent mini-VM | Ephemeral by design — stop it, throw it away, start a new one from the image |
| Mental model | "A lightweight virtual machine" | "A packaged, portable process" |
| Typical use | Replacing a full VM for density/cost reasons, running legacy multi-service systems that expect a full OS | Microservices, one-container-per-process, [CI/CD](../devops/ci-cd.md) pipelines, anything meant to be rebuilt from an image rather than patched in place |
| Image ecosystem | Smaller, mostly full-distro base images (Ubuntu, Debian, etc.) | Massive — [Docker](docker.md) Hub has an image for nearly every piece of software |
| Standard compliance | Predates [OCI](oci.md); not typically [OCI](oci.md)-image-based | Native to the [OCI](oci.md) ecosystem — images are portable to [Podman](podman.md), [Kubernetes](../distributed-systems/kubernetes/ingress.md), etc. |

Both ultimately rely on the same underlying kernel primitives — [namespaces and cgroups](container-isolation.md) — the difference is *what* they use those primitives to isolate: an entire OS environment (LXC/LXD) versus a single application ([Docker](docker.md)).

## Why This Matters When Choosing a Tool

If the deployment need is "run this one application (Nextcloud, a database, a small AI service) in an isolated, reproducible, easily-updated way," that's exactly the application-container use case [Docker](docker.md) was built for — small images, versioned tags, disposable containers, a huge base-image ecosystem.

LXC/LXD earns its keep when the actual need is closer to "I want several lightweight VMs" — e.g. running a full legacy stack that expects a real init system and persistent OS state, or replacing several small VMs with denser system containers on one host. That's a heavier, different-shaped problem than packaging one application, and it's why LXC/LXD is not really a [Docker](docker.md) alternative so much as a different category of tool that happens to also be called a "container."

## Related

- [Docker](docker.md)
- [Container Isolation](container-isolation.md)
- [Virtual Machines](../cloud/infrastructure/virtual-machines.md)
- [OCI (Open Container Initiative)](oci.md)
