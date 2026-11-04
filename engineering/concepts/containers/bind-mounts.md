# Bind Mounts

A **bind mount** maps a specific path on the **host machine** into a container. The container sees the host directory as if it were its own filesystem at that path — reads and writes go directly to the host, with no copying or caching layer. Changes made inside the container are immediately visible on the host, and vice versa.

## Bind Mount vs Named Volume

| | Bind Mount | Named Volume |
|---|---|---|
| Source | A specific host path you control | A [Docker](docker.md)-managed directory |
| Location on host | Wherever you specify | `/var/lib/docker/volumes/<name>/` |
| Pre-population | Container uses whatever is on the host | [Docker](docker.md) copies image content into empty volume |
| Portability | Tied to host path | Portable across environments |
| Best for | Dev (live code reload), config files, log sharing | Production data, databases |

Use **bind mounts** in development. Use **named volumes** in production.

## Syntax

### Docker CLI

```bash
# Long form (explicit and readable — preferred)
docker run \
  --mount type=bind,source=/host/path,target=/container/path \
  myimage

# Short form (-v)
docker run \
  -v /host/path:/container/path \
  myimage

# Read-only bind mount
docker run \
  --mount type=bind,source=/host/config,target=/app/config,readonly \
  myimage

# Using current directory (common in dev)
docker run \
  --mount type=bind,source=$(pwd),target=/app \
  myimage
```

### Docker Compose

```yaml
services:
  app:
    image: myapp
    volumes:
      # Short syntax
      - ./src:/app/src
      - ./config/app.yaml:/app/config.yaml:ro   # :ro = read-only

      # Long syntax (explicit)
      - type: bind
        source: ./data
        target: /app/data
        read_only: false
```

## Common Use Cases

### Live code reload (development)

Mount your source code into the container so changes are reflected instantly without rebuilding the image:

```yaml
services:
  api:
    build: .
    volumes:
      - .:/app                        # entire project into /app
    command: uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Config files

```yaml
services:
  nginx:
    image: nginx:alpine
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro   # read-only config
```

### Log collection

```yaml
services:
  app:
    volumes:
      - /var/log/myapp:/app/logs      # host collects logs; fail2ban / log shippers read them
```

### Sharing a socket (Docker-in-Docker, Traefik)

```yaml
services:
  traefik:
    image: traefik
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro
```

### Database init scripts

```yaml
services:
  postgres:
    image: postgres:16
    volumes:
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql:ro
```

## Path Rules

- **Absolute paths** — always safe and explicit:  
  `source=/home/user/project` or `source=$(pwd)/src`

- **Relative paths** — only supported in [Docker Compose](docker-compose.md) (resolved relative to the `docker-compose.yml` location); not valid in `docker run`:  
  `source: ./src`

- The **target path** is always an absolute path inside the container.

## File Ownership & Permissions

The container process runs as a specific UID/GID. If the host file's ownership doesn't match, you may get permission errors.

```bash
# Check container user
docker run --rm myimage id

# Fix: run container as your host user
docker run --user $(id -u):$(id -g) -v $(pwd):/app myimage

# Fix in Compose
services:
  app:
    user: "${UID}:${GID}"    # set UID/GID in .env
    volumes:
      - .:/app
```

```bash
# .env
UID=1000
GID=1000
```

## Read-Only Mounts

Prevent the container from modifying host files:

```yaml
volumes:
  - ./config:/app/config:ro
  # or long syntax:
  - type: bind
    source: ./config
    target: /app/config
    read_only: true
```

## Bind Mounts on Windows / WSL2

On Windows with [Docker](docker.md) Desktop + WSL2:

- Paths inside WSL2 (`/home/user/project`) work seamlessly
- Windows paths (`C:\Users\...`) work but are slower due to cross-filesystem overhead
- **Always keep project files inside the WSL2 filesystem** for best performance

```bash
# Good (inside WSL2)
docker run -v /home/user/project:/app myimage

# Slow (Windows path via WSL2)
docker run -v /mnt/c/Users/user/project:/app myimage
```

## Bind Mount vs tmpfs

```bash
# tmpfs — in-memory only, not persisted anywhere, not shared with host
docker run --mount type=tmpfs,target=/tmp myimage
```

Use `tmpfs` for ephemeral scratch space (e.g. secrets that should never touch disk).

## Inspect Mounts on a Running Container

```bash
docker inspect <container_id> --format '{{ json .Mounts }}' | jq
```

Output shows `Type`, `Source` (host path), `Destination` (container path), `Mode` (ro/rw), and `RW` flag.

## Gotchas

| Gotcha | Fix |
|---|---|
| Empty host directory overwrites container content | Pre-populate the host dir, or use a named volume for pre-populated paths |
| `.dockerignore` does not affect bind mounts | Only affects `COPY` during build |
| Relative paths in `docker run -v` fail silently | Always use absolute paths in `docker run`; relative only in Compose |
| Windows line endings (`\r\n`) in scripts | Add `dos2unix` to Dockerfile or set `autocrlf=false` in `.gitattributes` |

## Related Concepts

- [Docker Compose](./docker-compose.md) — orchestrate services with bind mounts
- [Fail2ban Docker](../security/attacks/fail2ban.md) — mount log directories from containers to host
- [SMB / NFS](../protocols/smb-nfs.md) — network filesystems that can also be bind-mounted into containers
