# systemctl (systemd) Commands

`systemctl` is the control interface for **systemd**, the init system and service manager on most modern Linux distributions (Ubuntu, Debian, RHEL/CentOS, Fedora). It's the OS-native way to run a process as a managed background service — starting it at boot, restarting it on crash, and centralizing its logs — without needing a separate tool like [PM2](pm2.md) or a container.

## Managing a Service

```bash
sudo systemctl start nginx                 # start now
sudo systemctl stop nginx                  # stop now
sudo systemctl restart nginx               # stop + start
sudo systemctl reload nginx                # re-read config without a full restart (only if the service supports it)
sudo systemctl status nginx                # is it running, recent log lines, PID, memory
```

## Boot-Time Behavior

```bash
sudo systemctl enable nginx                # start automatically on every boot
sudo systemctl disable nginx               # stop starting automatically on boot
sudo systemctl enable --now nginx          # enable AND start in one command
sudo systemctl is-enabled nginx            # check whether it's set to start on boot
sudo systemctl is-active nginx             # check whether it's currently running
```

`enable` and `start` are two independent, commonly-confused settings: `start` affects only right now; `enable` affects what happens on the *next* reboot. Running one without the other is the most common cause of "it was working, then the server rebooted and it wasn't there anymore."

## Viewing Logs (journalctl)

```bash
journalctl -u nginx                        # all logs for one service (unit)
journalctl -u nginx -f                     # follow live, like tail -f
journalctl -u nginx --since "1 hour ago"
journalctl -u nginx -n 100                 # last 100 lines
journalctl -p err                          # only error-level and above, across all units
journalctl --disk-usage                    # how much space the journal itself is consuming
```

`journalctl` is systemd's centralized log store — a service managed by systemd doesn't need its own separate log-rotation setup for stdout/stderr the way a manually-run script would.

## Listing Services

```bash
systemctl list-units --type=service               # all currently loaded services
systemctl list-units --type=service --state=running
systemctl list-unit-files --type=service           # every installed service and whether it's enabled
```

### Searching for a Specific Service

```bash
systemctl list-units --type=service | grep nginx          # loaded services matching a name
systemctl list-unit-files --type=service | grep nginx     # ALL installed services matching a name, loaded or not

systemctl status 'nginx*'                                  # wildcard works directly in status/start/stop too
```

`list-units` only shows services systemd has already loaded this boot — if a `grep` against it comes up empty for something you know is installed, check `list-unit-files` instead, which lists every unit file on disk regardless of load state.

### Going the Other Way: From a PID to Its Owning Service

The searches above assume you already know the service's *name*. Often it's the reverse — [`lsof -i :PORT`](bash.md) or `ps aux` found a process, and now you need to know which systemd unit actually manages it:

```bash
systemctl status 362869            # pass a PID directly — systemd looks up which unit owns it
```

Use the process's **main/parent PID**, not a child worker's — a multi-process service like nginx shows one master process plus several worker processes in `lsof`/`ps` output, but only the master is the one systemd actually tracks as the unit; passing a worker's PID to `systemctl status` won't resolve to the service.

The `CGroup:` section of the output makes this master/worker relationship visible directly — everything nested under it belongs to the same unit:

```text
Main PID: 362869 (nginx)
CGroup: /system.slice/nginx.service
        ├─362869 "nginx: master process /usr/sbin/nginx -g daemon on;"
        ├─1861947 "nginx: worker process"
        ├─1861948 "nginx: worker process"
        └─...
```

Every PID in that tree is part of the same `nginx.service` unit — `systemctl status` on any one worker PID won't find it, but the tree itself confirms which master PID to use instead.

## Viewing a Unit File's Content & Path

```bash
systemctl cat vllm.service                         # print the full unit file content directly
systemctl show vllm.service -p FragmentPath         # print just the unit file's path on disk
systemctl status vllm.service                       # also shows the path, on the "Loaded:" line
```

`systemctl cat` is almost always the better choice over `cat <path>` directly — it merges in any drop-in override files (`/etc/systemd/system/<name>.service.d/*.conf`) automatically, which a plain `cat` on just the base unit file would silently miss.

## Writing a Custom Unit File

```ini
# /etc/systemd/system/myapp.service
[Unit]
Description=My Node App
After=network.target

[Service]
ExecStart=/usr/bin/node /opt/myapp/dist/main.js
Restart=on-failure
RestartSec=5
User=myapp
Environment=NODE_ENV=production
EnvironmentFile=/opt/myapp/.env

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload               # required after creating/editing any unit file
sudo systemctl enable --now myapp
```

`daemon-reload` is easy to forget — without it, systemd keeps using its previously-cached copy of the unit file, so an edit appears to silently have no effect.

## Running a Docker Container as a systemd Service

A container run with `docker run -d` is detached from systemd entirely — no boot-time start, no systemd-managed restart policy, and its logs live in [Docker](../concepts/containers/docker.md)'s own log driver instead of `journalctl`. Wrapping it in a unit file gets you systemd's supervision on top of [Docker](../concepts/containers/docker.md)'s packaging, which matters most for a long-running service (an inference server, a database, a background worker) that should survive a reboot and restart itself on crash:

```ini
# /etc/systemd/system/myservice.service
[Unit]
Description=My Containerized Service
After=docker.service
Requires=docker.service

[Service]
Type=simple
User=myuser
WorkingDirectory=/home/myuser

# Clean up any leftover container from a previous run — "-" means don't fail the unit if these error
ExecStartPre=-/usr/bin/docker stop myservice
ExecStartPre=-/usr/bin/docker rm myservice

# Pull a pinned version, never `latest` — see OCI § Image Versioning & Registries
ExecStartPre=/usr/bin/docker pull myimage:1.0.0

# Run in the FOREGROUND (no -d) so systemd can actually supervise the process
ExecStart=/usr/bin/docker run --rm --name myservice \
  -p 8080:8080 \
  -e ENV_VAR=value \
  -v /data:/data \
  myimage:1.0.0

Restart=always
RestartSec=10

ExecStop=/usr/bin/docker stop myservice
ExecStopPost=-/usr/bin/docker rm myservice

TimeoutStartSec=300
TimeoutStopSec=60
KillMode=control-group

[Install]
WantedBy=multi-user.target
```

Key details that make this pattern actually work correctly, each easy to get subtly wrong:

| Directive | Why it matters |
|---|---|
| `Requires=docker.service` / `After=docker.service` | Ensures the [Docker daemon](../concepts/containers/docker-daemon.md) is up before this unit even attempts to start — without it, a fresh boot can race `dockerd` startup |
| `ExecStartPre=-...stop/rm` | The leading `-` tells systemd to ignore a non-zero exit here (there may be no leftover container to remove) — without it, a clean first start would fail immediately |
| Pinned image tag, not `latest` | Same reasoning as [OCI § Image Versioning & Registries](../concepts/containers/oci.md#image-versioning--registries) — a unit file that always pulls `latest` makes "what's actually running" unanswerable after a restart months later |
| `docker run` with **no `-d`** | `Type=simple` expects `ExecStart`'s process to keep running in the foreground — `docker run -d` would exit immediately after launching the container, and systemd would think the service crashed right after starting |
| `ExecStop=docker stop` | Without an explicit `ExecStop`, `systemctl stop` sends SIGTERM to the wrapping `docker run` process, not necessarily a clean stop signal to the container's actual process — an explicit `docker stop` guarantees a proper container shutdown |
| `TimeoutStartSec` set generously | A container pulling a large image or loading a large in-memory model (see [Model Lifecycle Management § Cold Start](../concepts/ai/infrastructure/model-lifecycle-management.md#cold-start-is-not-free--track-it)) can take minutes to become ready — systemd's default start timeout will kill and mark it failed if this is too short |
| `KillMode=control-group` | Ensures every process in the unit's cgroup gets signaled on stop, not just the top-level `docker run` process — relevant because `docker run` itself spawns a separate `containerd-shim` process tree |

## Common Questions

**Why would a project use a systemd unit instead of PM2 for a Node app?**
> systemd is OS-native — no extra runtime dependency, works identically for any kind of process (not just Node), and integrates with the rest of the OS's service ecosystem (logging via `journalctl`, dependency ordering via `After=`/`Requires=`). PM2 trades that OS-agnosticism for Node-specific conveniences (cluster mode, `pm2 reload` for zero-downtime restarts, a friendlier CLI) that systemd doesn't provide out of the box. See [PM2 Commands](pm2.md) for the fuller comparison.

**What does `Restart=on-failure` actually do?**
> It tells systemd to automatically restart the service if the process exits with a non-zero (failure) status, but NOT if it's stopped deliberately (`systemctl stop`) or exits cleanly (status 0). Combined with `RestartSec`, this gives a basic crash-loop recovery similar to what a container orchestrator's restart policy provides — see [OOM as a Scheduler Failure](../concepts/ai/infrastructure/gpu-scheduling.md#oom-as-a-scheduler-failure-not-a-crash-to-restart) for why blindly restarting forever, with no backoff, is itself a failure mode worth guarding against.

## Related

- [PM2 Commands](pm2.md)
- [Bash & Shell Commands](bash.md)
- [Docker Commands](docker.md)
- [Health, Liveness & Readiness Checks](../concepts/backend/architecture/health-liveness-readiness.md)
- [Cloudflare Tunnel (`cloudflared`) Commands](cloudflare-tunnel.md) — `cloudflared` itself is typically installed and managed as a systemd service via `cloudflared service install`
