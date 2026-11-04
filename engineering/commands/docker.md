# Docker Commands

The [Docker](../concepts/containers/docker.md) CLI commands used daily for running, debugging, and cleaning up containers and images. See [Docker](../concepts/containers/docker.md) for the underlying concepts and [Docker Compose](../concepts/containers/docker-compose.md) for the multi-container equivalent of most of these.

## Images

```bash
docker build -t myapp:1.0 .                # build an image from a Dockerfile in the current dir
docker images                              # list local images
docker rmi <image>                         # remove an image
docker pull nginx:latest                   # download an image without running it
docker push myrepo/myapp:1.0               # upload an image to a registry
docker tag myapp:1.0 myrepo/myapp:1.0      # add a tag pointing at an existing image
```

See [OCI § Image Versioning & Registries](../concepts/containers/oci.md#image-versioning--registries) for why `:latest` should never be the tag actually deployed to production.

## Running Containers

```bash
docker run nginx                           # run in the foreground, attached
docker run -d nginx                        # run detached (background) — for a long-running service that needs boot-time start and crash restarts, see systemd supervision below instead
docker run -p 8080:80 nginx                # map host port 8080 to container port 80
docker run -v /host/path:/container/path nginx   # bind-mount a host directory in
docker run --env-file .env myapp           # load environment variables from a file
docker run --rm myapp                      # auto-remove the container when it exits
docker run -it ubuntu bash                 # interactive terminal session inside a container
```

## Inspecting Running Containers

```bash
docker ps                                  # running containers
docker ps -a                               # all containers, including stopped ones
docker ps --filter "name=api"              # only containers whose name matches "api"
docker ps -a | grep nginx                  # equivalent, quick-and-dirty name search across all containers
docker images | grep myapp                 # same idea, searching images instead of containers
docker logs <container>                    # view a container's stdout/stderr
docker logs -f <container>                 # follow logs live
docker exec -it <container> bash           # open a shell inside a running container
docker inspect <container>                 # full JSON details (network, mounts, env, etc.)
docker stats                               # live CPU/memory usage per container
```

### Running a One-off Query Without an Interactive Shell

`docker exec -it <container> bash` (above) drops you into an interactive shell. To run a single command non-interactively — e.g. from a script, or piped into another tool — pass it straight to `sh -c` instead:

```bash
docker exec -it meshsa-postgres sh -c 'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c '"'"'SELECT count(*) FROM "Product" WHERE "isPublished" = true;'"'"''
```

This runs `psql` inside the `meshsa-postgres` container, using the container's own `$POSTGRES_USER`/`$POSTGRES_DB` env vars (set by the official postgres image) rather than hardcoding credentials. The double-quoted identifiers (`"Product"`, `"isPublished"`) preserve Postgres's case-sensitive column/table names — Postgres folds unquoted identifiers to lowercase.

The odd `'"'"'` sequences are a shell-quoting workaround, not a typo: the whole command is wrapped in single quotes for `sh -c`, but the [SQL](../concepts/databases/relational/sql.md) passed to `psql -c` also needs single quotes around it — and single quotes can't nest inside single quotes in bash. `'"'"'` closes the outer quote (`'`), inserts a literal single quote as a double-quoted string (`"'"`), then reopens the outer quote (`'`). It's the standard trick for embedding a `'` inside a single-quoted string. When you don't need it to survive an outer `sh -c` layer, it's simpler to swap the outer/inner quote styles instead, e.g.:

```bash
docker exec -it meshsa-postgres psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "SELECT count(*) FROM \"Product\" WHERE \"isPublished\" = true;"
```

## Stopping & Cleaning Up

```bash
docker stop <container>                    # graceful shutdown (SIGTERM, then SIGKILL after a timeout)
docker kill <container>                    # immediate SIGKILL
docker rm <container>                      # remove a stopped container
docker rm -f <container>                   # stop and remove in one step

docker system prune                        # remove stopped containers, unused networks, dangling images
docker system prune -a                     # also remove all unused images, not just dangling ones
docker volume prune                        # remove unused volumes — irreversible if they held real data
```

Run `docker volume prune` with real caution — see [Backup and Restore § The Critical Distinction](../concepts/cloud/infrastructure/backup-and-restore.md#the-critical-distinction-docker-image--backup) for why a volume, not the image, is where actual application data lives.

## Volumes

```bash
docker volume ls
docker volume create mydata
docker volume inspect mydata
```

## Networks

```bash
docker network ls
docker network create mynet
docker network connect mynet <container>
```

## Docker Compose

```bash
docker compose up -d                       # start all services in the background
docker compose down                        # stop and remove containers (keeps volumes)
docker compose down -v                     # also remove volumes — deletes data, see warning above
docker compose logs -f <service>
docker compose exec <service> bash
docker compose build                       # rebuild images defined in compose.yaml
docker compose ps
```

## Related

- [Docker](../concepts/containers/docker.md)
- [Docker Compose](../concepts/containers/docker-compose.md)
- [OCI (Open Container Initiative)](../concepts/containers/oci.md)
- [Backup and Restore](../concepts/cloud/infrastructure/backup-and-restore.md)
- [kubectl Commands](kubectl.md)
- [systemctl (systemd) Commands § Running a Docker Container as a systemd Service](systemctl.md#running-a-docker-container-as-a-systemd-service) — alternative to `docker run -d` for boot-time start and automatic crash restart
