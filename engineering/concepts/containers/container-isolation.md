# Container Isolation (Namespaces & cgroups)

## What Is It

A container isn't a lightweight VM — it's an ordinary process on the host, made to *look* isolated using two Linux kernel features:

| Feature | What it does |
|---|---|
| **Namespaces** | Give a process its own private *view* of a system resource (its own process list, its own network interfaces, its own filesystem mounts, etc.) |
| **cgroups** (control groups) | Limit and account for *how much* of a shared resource (CPU, memory, disk [I/O](../programming/fundamentals/io.md)) a process or group of processes can use |

Namespaces answer "what can this process **see**?" cgroups answer "how much can this process **use**?" Together, they're what makes a container feel like its own machine while actually being one more process on the host's single kernel.

## The Namespace Types

| Namespace | Isolates |
|---|---|
| **PID** | Process IDs — a container's process tree starts fresh at PID 1, unaware of processes outside it |
| **Network** | Network interfaces, IP addresses, routing tables, ports — this is why two containers can both bind to port 80 without conflicting |
| **Mount** | The filesystem mount table — a container sees its own root filesystem, not the host's |
| **UTS** | Hostname and domain name — a container can have its own hostname |
| **IPC** | Inter-process communication (shared memory, [message queues](../distributed-systems/messaging/queues.md)) between processes |
| **User** | UID/GID mapping — a process can be "root" (UID 0) inside its namespace while mapping to an unprivileged UID on the host (this is what rootless containers rely on) |
| **Cgroup** | The cgroup hierarchy itself, so a container can't see or modify cgroups of processes outside it |

## Container Isolation vs a VM

This is the distinction that matters when someone asks "isn't a container just a small VM?"

| | Container (namespaces + cgroups) | Virtual Machine |
|---|---|---|
| Kernel | **Shared** with the host | Its own kernel, fully virtualized |
| Isolation boundary | Kernel-enforced views (namespaces) | Hardware-level virtualization (hypervisor) |
| Startup time | Milliseconds | Tens of seconds |
| Overhead | Near-zero — just extra kernel bookkeeping | A full guest OS running on virtualized hardware |
| Attack surface if isolation fails | Shared kernel means a kernel exploit can escape to the host | Hypervisor escape is possible but a much smaller, harder-to-reach surface |

A container is process isolation; a VM is hardware isolation. That's why containers start almost instantly and pack far more densely on a single host, but also why a kernel-level exploit is a bigger deal for containers than for VMs — every container on the box shares that one kernel.

## Why It Matters for Docker

When [Docker](docker.md) says a container is "isolated," this is the actual mechanism — [Docker](docker.md) doesn't invent isolation itself, it's a convenient interface (image format, CLI, networking, volumes) built on top of namespaces and cgroups that the Linux kernel already provides. This is also why [Docker](docker.md) containers only run natively on Linux: on macOS and Windows, [Docker](docker.md) Desktop runs a lightweight Linux VM under the hood to have a Linux kernel to create namespaces in.

Every [OCI](oci.md)-compliant runtime — [Docker](docker.md)'s `runc`, [Podman](podman.md), [LXC/LXD](lxc-lxd.md) — is ultimately just a different way of wiring up the same underlying namespaces and cgroups.

## Related

- [Docker](docker.md)
- [Docker Daemon (Docker Engine)](docker-daemon.md)
- [OCI (Open Container Initiative)](oci.md)
- [Podman](podman.md)
- [LXC / LXD](lxc-lxd.md)
- [Virtual Machines](../cloud/infrastructure/virtual-machines.md)
