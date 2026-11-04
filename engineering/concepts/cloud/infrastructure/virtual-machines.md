# Virtual Machines

## What is it?

A virtual machine (VM) is a software-based computer that runs inside a real physical computer. It behaves exactly like a real machine — it has its own operating system, storage, CPU, and RAM — but it shares the physical hardware of the host machine with other VMs or the host OS.

```
Physical Machine (Host)
├── Your OS (Windows / Mac)
└── Virtual Machine (Guest)
    ├── Its own OS (e.g., Ubuntu 22.04)
    ├── Its own storage (virtual disk)
    └── Its own RAM and CPU (allocated from host)
```

## How it Works

A program called a **hypervisor** sits between the hardware and the VMs. It divides the physical CPU, RAM, and storage and gives each VM its own isolated slice.

| Term | Meaning |
|---|---|
| **Host** | The real physical machine running the hypervisor |
| **Guest** | The virtual machine running inside the host |
| **Hypervisor** | The software that creates and manages VMs (e.g., VirtualBox, Hyper-V, VMware) |
| **Snapshot** | A saved state of a VM — you can restore to it at any time |
| **Virtual disk** | A file on the host that the VM treats as its hard drive |

### Types of hypervisors

| Type | Description | Examples |
|---|---|---|
| **Type 1 (bare-metal)** | Runs directly on hardware — used in data centers | Hyper-V, VMware ESXi, KVM |
| **Type 2 (hosted)** | Runs as an app on top of your OS — used on developer machines | VirtualBox, VMware Workstation |

## VMs in This Project

This project uses virtual machines in two contexts.

### 1. Local development — VirtualBox

Team members who cannot use WSL2 run an Ubuntu 22.04 VM inside VirtualBox on their Windows or Mac machine. This VM runs [Docker](../../containers/docker.md), Bash scripts, and all Linux tools locally for development and testing.

```
Developer's Windows/Mac
└── VirtualBox (Type 2 hypervisor)
    └── Ubuntu 22.04 VM
        └── Docker → Nextcloud + PostgreSQL + AI service
```

### 2. Cloud production — Azure VM

The production environment runs on a virtual machine hosted by [Microsoft Azure](azure.md). [Azure](../azure/azure.md) is a data center running thousands of physical servers — each customer gets one or more VMs carved out of that hardware.

```
Microsoft Azure Data Center (physical servers)
└── Azure Hypervisor (Type 1)
    └── Our Ubuntu 22.04 VM (Standard_B2s)
        └── Docker → Nextcloud + PostgreSQL + AI service
```

The VM is provisioned via [Terraform](terraform.md) and sits behind the [VNet/NSG network layer](../azure/networking-vnet-nsg.md).

## VM vs Container

VMs and [Docker](../../containers/docker.md) containers are both isolation technologies but work at different levels:

| | Virtual Machine | [Docker](../../containers/docker.md) Container |
|---|---|---|
| Isolates | Full OS + hardware | Application + dependencies |
| Includes | Kernel, OS, libraries, app | Libraries + app only (shares host kernel) |
| Size | GBs | MBs |
| Startup time | Minutes | Seconds |
| Use case | Full server environment | Running individual services |

In this project: the **VM provides the Linux server**, and **[Docker](../containers/docker.md) runs inside the VM** to host individual services (see [Docker Compose](../../containers/docker-compose.md) for how they're orchestrated).

## Key VM Concepts

**RAM allocation** — the host assigns a fixed amount of RAM to the VM. If you give the VM 4 GB, those 4 GB are reserved from the host's total memory while the VM is running.

**Virtual disk** — the VM's storage is a large file on the host (e.g., `ubuntu.vdi`). It can be set to grow dynamically up to a maximum size.

**Network modes:**

| Mode | What it means |
|---|---|
| NAT | VM can reach the internet but is invisible from the host network |
| Bridged | VM gets its own IP on the local network — accessible from other machines |
| Host-only | VM can only talk to the host machine, not the internet |

**Snapshots** — a saved state of the VM at a point in time. Take a snapshot before making major changes; if something breaks, restore in seconds. A snapshot is not a substitute for a real [backup](backup-and-restore.md) of application data.

## Tips

- Always allocate at least **4 GB RAM** to the VM for this project — less will cause [Docker](../../containers/docker.md) containers to crash
- Use **Ubuntu 22.04 LTS** inside the VM — the same OS as the [Azure](../azure/azure.md) production server — so scripts behave identically in both environments
- Take a **snapshot** after completing the initial setup so you can restore quickly if the VM breaks
- Use **Bridged networking** in VirtualBox if you want to access the VM from your browser on the host machine

## Related

- [Microsoft Azure](azure.md)
- [Terraform](terraform.md)
- [Azure Networking: VNet & NSG](../azure/networking-vnet-nsg.md)
- [Backup and Restore](backup-and-restore.md)
- [Docker](../containers/docker.md)
