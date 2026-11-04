# Podman

## What Is It

**Podman** is an [OCI](oci.md)-compliant container engine developed by Red Hat, built as a **rootless, daemonless** alternative to [Docker](docker.md). It runs the same [OCI](oci.md) images, understands the same `docker-compose.yml`-style files (via `podman-compose` or its own Compose support), and its CLI is close enough to [Docker](docker.md)'s that `alias docker=podman` works for most day-to-day commands.

## The Two Architectural Differences from Docker

| | [Docker](docker.md) | Podman |
|---|---|---|
| **Daemon** | `dockerd` runs as a persistent background process; the CLI is a client talking to it over a socket | No daemon — `podman run` forks the container directly as a child process of your shell |
| **Root** | Daemon runs as root by default (see [Docker Daemon](docker-daemon.md)) | Rootless by default — containers run under your normal user account, using [user namespaces](container-isolation.md) to map "root" inside the container to your unprivileged UID on the host |

Because there's no long-lived root daemon and no socket that grants full container control to anyone who can reach it, Podman removes the specific attack surface described in [Docker Daemon](docker-daemon.md): there's no single process whose compromise hands over the whole host, and no `docker` group membership that's quietly equivalent to root.

## Why It's OCI-Compatible, Not a Different Ecosystem

Podman doesn't invent its own image format — it consumes and produces standard [OCI](oci.md) images. In practice this means:

- Images pulled from [Docker](docker.md) Hub run unchanged under Podman.
- A `Dockerfile` builds under Podman with no changes (`podman build`).
- Existing `docker-compose.yml` files work via `podman-compose` (or Podman's native Compose support in recent versions), with the same service/volume/network structure described in [Docker Compose](docker-compose.md).

This is why it's fairly called a **drop-in replacement** rather than a competing tool with its own learning curve — the mental model (images, containers, volumes, networks, compose files) carries over directly.

## Trade-offs

| Podman gives you | What you give up or need to check |
|---|---|
| No root daemon, smaller default attack surface | Slightly younger tooling ecosystem than [Docker](docker.md)'s; fewer third-party integrations assume Podman by default |
| Rootless containers by default | Rootless mode has known gaps around some networking modes and older cgroup v1 hosts — worth testing for the specific stack before relying on it |
| systemd integration (`podman generate systemd`) — containers managed like native services | No built-in [Docker](docker.md) Desktop-style GUI on macOS/Windows (though Podman Desktop exists) |

## Why It Comes Up for a Single-VM Deployment

When the question is "why Docker and not something else" for a project like a Nextcloud stack on one [Azure](../cloud/azure/azure.md) VM, Podman is the direct answer to "isn't there a more secure option?" — same [OCI](oci.md)-compatible images, same Compose-style orchestration, no root daemon. Docker was still chosen here because it's the default assumption in almost every tutorial, base image, and community troubleshooting thread, which matters more for a small, single-VM deployment than the daemon's root requirement does in practice (mitigated by not exposing the Docker socket and not adding untrusted users to the `docker` group).

## Related

- [systemctl (systemd) Commands](../../commands/systemctl.md) — the unit-file/service-management commands behind `podman generate systemd`
- [Docker](docker.md)
- [Docker Daemon (Docker Engine)](docker-daemon.md)
- [OCI (Open Container Initiative)](oci.md)
- [Container Isolation](container-isolation.md)
- [Docker Compose](docker-compose.md)
