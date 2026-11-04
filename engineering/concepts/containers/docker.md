# Docker

## What Is It

Docker is a platform for packaging, distributing, and running applications in isolated environments called **containers**. A container bundles the application code together with everything it needs to run — runtime, libraries, configuration — so it works consistently on any machine regardless of the underlying OS or installed software.

## The Problem Docker Solves

Without Docker, "it works on my machine but not on the server" is a common problem because different environments have different software versions, configurations, and dependencies.

With Docker, the container carries its own environment. The same container runs identically on a developer's laptop, a test server, and a production VM.

## Key Concepts

**Image**
A read-only template that defines what a container contains. Think of it as a blueprint or a snapshot of a configured application.

```
nextcloud:27   ← image name and version tag
```

**Container**
A running instance created from an image. Multiple containers can run from the same image simultaneously.

**Dockerfile**
A text file with instructions to build a custom image. Projects that only need official images (e.g. Nextcloud, [PostgreSQL](../databases/relational/postgresql.md)) don't need custom Dockerfiles.

**Registry**
A repository of images. Docker Hub (hub.docker.com) is the public registry where official images are published.

**Volume**
Storage that is mounted into the container but lives on the host filesystem. Volumes persist data beyond the container's lifecycle. See [Docker Compose](docker-compose.md) for details.

**Network**
Docker creates virtual networks. Containers on the same network can reach each other by service name. Containers on different networks are isolated.

## Why Docker

| Benefit | Explanation |
|---|---|
| **No manual installation** | Services run from pre-built images — no manual `apt-get` chains |
| **Isolation** | Internal services (e.g. a database) are not accessible from outside the Docker network |
| **Repeatability** | Any host with Docker installed can run the same stack |
| **Easy updates** | Change the image tag in `docker-compose.yml` and pull the new version |
| **Clean teardown** | `docker compose down` removes all containers cleanly |

## Docker Image vs Data Backup

This is a critical distinction: a Docker image is not a backup of your data.

```
Docker Image contains:
  ├── Application code
  ├── Runtime (e.g. PHP, Apache)
  └── System libraries

Docker Image does NOT contain:
  ├── User files (uploaded documents)
  ├── Database records (users, permissions, metadata)
  └── Application configuration (custom settings)
```

Data lives in volumes and must be backed up separately. See [Backup and Restore](../cloud/infrastructure/backup-and-restore.md).

## Common Docker Commands

| Command | What it does |
|---|---|
| `docker ps` | List running containers |
| `docker ps -a` | List all containers (including stopped) |
| `docker logs <name>` | View logs for a container |
| `docker exec -it <name> bash` | Open a shell inside a running container |
| `docker images` | List locally available images |
| `docker pull <image>:<tag>` | Download an image |
| `docker volume ls` | List all volumes |
| `docker network ls` | List all networks |

## How It Fits Together

Docker is the containerization layer that typically runs on a Linux server (see [Ubuntu Server Setup](../../guides/linux/ubuntu-server-setup.md)). Services run as Docker containers, orchestrated by [Docker Compose](docker-compose.md), with infrastructure often provisioned via [Terraform](../cloud/iac/terraform.md).

## Related

- [Docker Compose](docker-compose.md)
- [Docker Daemon (Docker Engine)](docker-daemon.md) — how the daemon works, and why it running as root matters
- [Container Isolation](container-isolation.md) — the namespaces/cgroups mechanism underneath "isolation"
- [OCI (Open Container Initiative)](oci.md) — the standard that makes Docker images portable to other runtimes
- [Podman](podman.md) — rootless, daemonless alternative engine
- [PM2 Commands](../../commands/pm2.md) — process-manager alternative for a simple app on a single VPS, without containerizing at all
- [LXC / LXD](lxc-lxd.md) — system containers, a different category from Docker's application containers
- [Terraform](../cloud/iac/terraform.md)
- [Backup and Restore](../cloud/infrastructure/backup-and-restore.md)
- [Nextcloud RAG Case Study](../../guides/cloud/nextcloud-rag-case-study/nextcloud.md)
- [Docker Commands](../../commands/docker.md)
- [Ubuntu Server Setup](../../guides/linux/ubuntu-server-setup.md)
- [Secrets Management](../security/secrets/secrets-management.md)
