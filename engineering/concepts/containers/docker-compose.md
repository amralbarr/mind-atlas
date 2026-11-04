# Docker Compose

## What Is It

Docker Compose is a tool for defining and running multi-container [Docker](docker.md) applications. Instead of manually starting each container with long `docker run` commands, you write a single `docker-compose.yml` file that describes all your services, their configuration, how they connect to each other, and where their data lives. One command starts everything.

## Docker vs Docker Compose

| | [Docker](docker.md) | Docker Compose |
|---|---|---|
| Scope | Runs one container | Runs multiple containers together |
| Config | Long `docker run` command | Clean `docker-compose.yml` file |
| Networking | Manual | Automatic internal network |
| Volumes | Specified per command | Declared centrally |
| Usage | `docker run ...` | `docker compose up -d` |

See [Docker](docker.md) for the underlying concepts (images, containers, volumes, networks).

## Key Concepts

**Image**
A read-only template (blueprint) for a container. Example: `nextcloud:latest` is the official Nextcloud image.

**Container**
A running instance of an image. The image is the recipe; the container is the meal.

**Volume**
Persistent storage that lives outside the container filesystem. Data in a volume survives `docker compose down`. Data in the container filesystem does not.

**Network**
Docker Compose creates an internal network so services can talk to each other by name (e.g. an app connects to the database using the hostname `db`, not an IP address).

**Service**
One container defined in `docker-compose.yml`. A typical stack has services like `app`, `db`, and optionally `ai`.

## The Critical Distinction: `down` vs `down -v`

```bash
docker compose down        # stops and removes containers — volumes are KEPT
docker compose down -v     # stops containers AND deletes all volumes — DATA IS LOST
```

Never run `docker compose down -v` on a live system with real data.

## Example `docker-compose.yml` Structure

```yaml
version: '3.8'

services:
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: ${POSTGRES_DB}
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - db_data:/var/lib/postgresql/data
    networks:
      - internal
    # No ports exposed — DB is internal only

  nextcloud:
    image: nextcloud:27
    depends_on:
      - db
    ports:
      - "80:80"      # or behind nginx/HTTPS proxy on 443
    environment:
      POSTGRES_HOST: db
      POSTGRES_DB: ${POSTGRES_DB}
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - nextcloud_data:/var/www/html
    networks:
      - internal

volumes:
  db_data:         # persists database data
  nextcloud_data:  # persists Nextcloud files and config

networks:
  internal:        # private network — DB not reachable from outside
```

### Persistent Volumes in This Example

| Volume | What it stores | What is lost without it |
|---|---|---|
| `nextcloud_data` | All user files, Nextcloud config, installed apps | All uploaded documents, settings |
| `db_data` | Database: users, groups, permissions, metadata | All user accounts, sharing config, audit logs |

## Common Commands

| Command | What it does |
|---|---|
| `docker compose up -d` | Start all services in the background |
| `docker compose down` | Stop all services (keep volumes) |
| `docker compose ps` | List running services and their status |
| `docker compose logs <service>` | Show logs for a service |
| `docker compose restart <service>` | Restart one service |
| `docker compose pull` | Pull latest versions of all images |

## How It Fits Together

Docker Compose defines an entire application stack as code, typically checked into version control alongside a `deploy.sh` script. Anyone with [Docker](docker.md) installed can run `docker compose up -d` and have a working instance — provided the underlying infrastructure has already been provisioned, e.g. via [Terraform](../cloud/iac/terraform.md), on a host such as [Ubuntu Server](../../guides/linux/ubuntu-server-setup.md).

## Related

- [Docker](docker.md)
- [Terraform](../cloud/iac/terraform.md)
- [Backup and Restore](../cloud/infrastructure/backup-and-restore.md)
- [Nextcloud RAG Case Study](../../guides/cloud/nextcloud-rag-case-study/nextcloud.md)
- [Ubuntu Server Setup](../../guides/linux/ubuntu-server-setup.md)
