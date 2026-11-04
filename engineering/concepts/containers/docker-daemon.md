# Docker Daemon (Docker Engine)

## What Is It

**Docker Engine** is the client-server application that makes [Docker](docker.md) work. It has three parts:

| Part | Role |
|---|---|
| **`dockerd`** (the daemon) | A long-running background process that builds images, runs containers, manages volumes/networks, and does all the actual work |
| **[REST](../backend/api/rest.md) API** | The interface `dockerd` exposes, listening on a Unix socket (`/var/run/docker.sock`) by default |
| **`docker` CLI** | The client you type commands into — it doesn't do the work itself, it just sends API requests to `dockerd` |

```
docker run nginx
     │
     ▼
docker CLI  ──(REST API call)──►  dockerd (daemon)  ──► creates and runs the container
```

Every `docker ...` command you run is really a client talking to a server over that socket. This is why `docker ps` still works to inspect containers started by a completely different terminal, script, or user — they all go through the same daemon.

## The Security Concern: Root by Default

On a standard install, `dockerd` runs **as root**, and the Unix socket it listens on is only reachable by root or members of the `docker` group.

This matters because:

- Anyone who can talk to the [Docker](docker.md) socket can effectively get root on the host — not just inside a container. Mounting the host filesystem into a container (`-v /:/host`) and `chroot`-ing into it is a one-liner root shell.
- Being in the `docker` group is **equivalent to having passwordless root**, even though it doesn't look like a privilege-escalation vector at a glance. This is a common finding in security audits and CTFs.
- If `dockerd` itself has a vulnerability, or a container escapes its isolation, the daemon's root privileges are what the attacker inherits.

```bash
# Anyone in the docker group can trivially get a root shell on the host:
docker run -v /:/host -it alpine chroot /host sh
```

## Mitigations

| Approach | What it does |
|---|---|
| **Rootless [Docker](docker.md)** | Runs `dockerd` itself as an unprivileged user, using user namespaces to remap root inside the container to a non-root UID on the host. Reduces blast radius, but has its own gaps (some kernel features, cgroup v1, and certain networking setups behave differently or aren't supported) |
| **Restrict the `docker` group** | Don't add every user or CI runner to it — treat group membership as root access |
| **Rootless-by-default alternatives** | [Podman](podman.md) skips the problem entirely by having no root daemon in the first place |
| **Least privilege inside containers** | Avoid `--privileged`, drop capabilities, don't mount `/` or the [Docker](docker.md) socket into containers unless strictly necessary |

## Why This Matters for a Single-VM Deployment

On a project like a Nextcloud deployment on one [Azure](../cloud/azure/azure.md) VM, the daemon's root requirement is the main argument for evaluating [Podman](podman.md) as a "more secure by default" alternative: same [OCI](oci.md)-compatible workflow ([OCI](oci.md)), same `docker-compose.yml`-style files, but no persistent root process listening on a socket that a compromised container or a misconfigured service could reach.

## Related

- [Docker](docker.md)
- [Container Isolation](container-isolation.md)
- [Podman](podman.md)
- [OCI (Open Container Initiative)](oci.md)
- [Secrets Management](../security/secrets/secrets-management.md)
