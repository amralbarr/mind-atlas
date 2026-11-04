# Installing Docker Desktop (macOS)

[Docker](../../concepts/containers/docker.md) Desktop is the local installation of [Docker](../../concepts/containers/docker.md) — the containerization platform that packages applications and their dependencies into portable, isolated containers. [Docker](../../concepts/containers/docker.md) Desktop includes [Docker Engine](../../concepts/containers/docker-daemon.md), [Docker Compose](../../concepts/containers/docker-compose.md), and a GUI dashboard. For the conceptual background on images, containers, volumes, and networks, see [Docker](../../concepts/containers/docker.md).

## Install

### macOS

| Chip | Method |
|---|---|
| Apple Silicon (M-series) | Download the Apple Silicon `.dmg` from [docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop/) |
| Intel | Download the Intel `.dmg` from the same page |

### Windows

Download from [docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop/) — requires the WSL2 backend.

### Linux

[Docker](../../concepts/containers/docker.md) Desktop is available on Linux but optional; installing [Docker Engine](../../concepts/containers/docker-daemon.md) directly is more common:

```bash
# Official installation script
curl -fsSL https://get.docker.com | sh

# Add your user to the docker group (so you don't need sudo)
sudo usermod -aG docker $USER
newgrp docker

# Install Docker Compose plugin
sudo apt install docker-compose-plugin
```

### Verify

```bash
docker --version          # Docker version 24.x.x or higher
docker compose version    # Docker Compose version v2.x.x or higher
docker run hello-world    # should print "Hello from Docker!"
```

## Required Settings

Open [Docker](../../concepts/containers/docker.md) Desktop → Settings:

| Setting | Value | Reason |
|---|---|---|
| Resources → Memory | At least 4 GB | Typical multi-service stacks (e.g. an app + database) require it |
| Resources → CPU | At least 2 cores | Multiple containers run simultaneously |
| General → Use WSL2 based engine | Enabled (Windows only) | Required for performance on Windows |

## Core Concepts

| Concept | What it means |
|---|---|
| **Image** | A read-only blueprint for a container (e.g. `nextcloud:27`, `postgres:15`) |
| **Container** | A running instance created from an image |
| **Volume** | Persistent storage that lives outside the container — survives restarts |
| **Network** | A virtual network connecting containers to each other |
| **Registry** | A repository of images — Docker Hub is the default public registry |

See [Docker](../../concepts/containers/docker.md) for a fuller explanation of each concept.

## Essential Docker Commands

### Container Management

```bash
docker ps                          # list running containers
docker ps -a                       # list all containers (including stopped)
docker start <name>                # start a stopped container
docker stop <name>                 # stop a running container
docker rm <name>                   # remove a container
docker logs <name>                 # view container logs
docker logs -f <name>              # follow logs in real time
docker exec -it <name> bash        # open a shell inside a running container
```

### Images

```bash
docker images                      # list local images
docker pull <image>:<tag>          # download an image
docker rmi <image>                 # remove a local image
```

### Volumes

```bash
docker volume ls                   # list all volumes
docker volume inspect <name>       # inspect a volume
docker volume rm <name>            # delete a volume (CAUTION: data is gone)
```

### Networks

```bash
docker network ls                  # list all networks
docker network inspect <name>      # inspect a network
```

## Essential Docker Compose Commands

```bash
docker compose up -d               # start all services in the background
docker compose down                # stop and remove containers (volumes kept)
docker compose down -v             # stop containers AND delete volumes (DATA LOST)
docker compose ps                  # list service status
docker compose logs                # view logs for all services
docker compose logs -f <service>   # follow logs for one service
docker compose restart <service>   # restart one service
docker compose pull                # pull latest image versions
docker compose exec <service> bash # open shell in a running service container
docker compose build               # build custom images (if using a Dockerfile)
```

> **Critical:** `docker compose down -v` permanently deletes all volume data. Always run a backup before using it — see [Backup and Restore](../../concepts/cloud/infrastructure/backup-and-restore.md).

## Image vs Data

```
Docker Image contains:
  ├── Application code
  ├── Runtime and libraries
  └── System dependencies

Docker Image does NOT contain:
  ├── User uploaded files       → stored in a named volume
  ├── Database records          → stored in a named volume
  └── Application configuration → stored in a named volume
```

A Docker image is not a backup. Data must be backed up separately from volumes.

## Tips

- Always use named volumes (not [bind mounts](../../concepts/containers/bind-mounts.md)) for application data in production.
- Never expose database or internal service ports publicly — use Docker internal networks.
- Use `.env` files with `docker compose` to keep secrets out of `docker-compose.yml`.
- Run `docker system prune` periodically to clean up unused images and containers.

## Related

- [Docker](../../concepts/containers/docker.md)
- [Docker Compose](../../concepts/containers/docker-compose.md)
- [Terraform](../../concepts/cloud/iac/terraform.md)
- [Backup and Restore](../../concepts/cloud/infrastructure/backup-and-restore.md)
- [Nextcloud RAG Case Study](../../guides/cloud/nextcloud-rag-case-study/nextcloud.md)
