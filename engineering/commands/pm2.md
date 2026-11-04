# PM2 Commands

PM2 is a production process manager for Node.js — it keeps a process running, restarts it on crash, and manages logs/monitoring, without needing a full container orchestrator. A common step for a Node app running on a plain VPS before (or instead of) moving to [Docker](../concepts/containers/docker.md)/[Kubernetes](../concepts/distributed-systems/kubernetes/kubernetes-basics.md).

## Install

```bash
npm install -g pm2
pm2 --version
```

## Starting Processes

```bash
pm2 start app.js                           # run a script directly
pm2 start app.js --name my-api             # give it a readable name (used in every other command below)
pm2 start npm --name my-api -- run start   # run a package.json script instead of a file directly
pm2 start app.js -i max                    # cluster mode: one worker per CPU core
pm2 start app.js -i 4                      # cluster mode: 4 workers specifically
```

Cluster mode (`-i`) runs multiple instances of the same app behind PM2's built-in load balancer — the same horizontal-scaling idea as running several containers behind a [reverse proxy](../concepts/networking/reverse-proxy.md), but on one machine with no extra infrastructure.

## Inspecting Processes

```bash
pm2 list                                   # all managed processes, status, CPU/memory, restart count
pm2 status                                 # alias for `list`
pm2 show my-api                            # full details for one process
pm2 monit                                  # live, interactive CPU/memory dashboard
pm2 list | grep api                        # search by name — PM2 has no built-in name filter, so grep is the standard way
```

## Logs

```bash
pm2 logs                                   # tail logs from every managed process
pm2 logs my-api                            # tail logs from one process
pm2 logs my-api --lines 200                # show more history
pm2 flush                                  # clear all log files
```

## Restarting, Stopping, Reloading

```bash
pm2 restart my-api                         # stop + start (brief downtime)
pm2 reload my-api                          # zero-downtime restart — only meaningful in cluster mode (-i), one worker at a time
pm2 stop my-api                            # stop but keep it in PM2's process list
pm2 delete my-api                          # stop AND remove it from PM2's process list entirely
pm2 restart all                            # restart everything PM2 manages
```

`reload` is what makes a deploy zero-downtime: it restarts cluster workers one at a time so there's always at least one instance still serving traffic — plain `restart` briefly drops all instances at once.

## Persistence Across Reboots

```bash
pm2 save                                   # snapshot the current process list
pm2 startup                                # generate (and optionally run) the OS-specific boot script
pm2 resurrect                              # manually restore the last saved process list
```

Without `pm2 save` + `pm2 startup`, every process PM2 is managing simply doesn't come back after a server reboot — this pair is the step most often forgotten when first setting up a VPS.

## Ecosystem File (Config as Code)

```javascript
// ecosystem.config.js
module.exports = {
  apps: [{
    name: "my-api",
    script: "./dist/main.js",
    instances: "max",
    exec_mode: "cluster",
    env: { NODE_ENV: "production" },
    max_memory_restart: "500M",   // restart if this process exceeds 500MB RSS
  }],
};
```

```bash
pm2 start ecosystem.config.js
pm2 reload ecosystem.config.js --env production
```

An ecosystem file is the [Infrastructure as Code](../concepts/cloud/iac/infrastructure-as-code.md) equivalent for process configuration — the same instance count, memory limits, and environment get applied identically every time, instead of being re-typed as flags each deploy.

## Common Questions

**Why would a project use PM2 instead of just [Docker](../concepts/containers/docker.md)?**
> PM2 solves process supervision (keep it running, restart on crash, basic clustering) without the overhead of containerizing an app at all — a reasonable choice for a simple Node app on a single VPS. It doesn't provide isolation, portability across environments, or the broader orchestration [Docker](../concepts/containers/docker.md)/[Kubernetes](../concepts/distributed-systems/kubernetes/ingress.md) give you; a system with multiple services or that needs to scale across machines usually outgrows PM2 into containers. See the runtime-adapter pattern in [GPU-Aware Scheduling](../concepts/ai/infrastructure/gpu-scheduling.md)'s source material, where PM2, systemd, and [Docker](../concepts/containers/docker.md) are treated as interchangeable ways to run the same underlying service.

**What actually happens on `pm2 reload` in cluster mode?**
> PM2 starts a replacement worker, waits for it to be ready, then stops one old worker — repeating one at a time until every worker is replaced. This is the same rolling-restart idea behind a [Kubernetes](../concepts/distributed-systems/kubernetes/ingress.md) rolling deployment or a load balancer's connection draining, just implemented at the single-machine process level.

## Related

- [systemctl (systemd) Commands](systemctl.md) — the OS-native process-supervision alternative to PM2
- [Docker Commands](docker.md)
- [Docker](../concepts/containers/docker.md)
- [Kubernetes Basics](../concepts/distributed-systems/kubernetes/kubernetes-basics.md)
- [Infrastructure as Code](../concepts/cloud/iac/infrastructure-as-code.md)
- [Health, Liveness & Readiness Checks](../concepts/backend/architecture/health-liveness-readiness.md)
