# Azure Networking: VNet & NSG

## Overview

The [Azure](azure.md) network layer controls how the VM communicates with the Internet and how internal services communicate with each other. Getting this right is critical for security — a misconfigured network can expose the database or AI service to the public Internet.

## Azure Networking Components

### Virtual Network (VNet)

A [VNet](azure-vnet.md) is a private, isolated network inside [Azure](azure.md) — similar to a corporate LAN, but in the cloud. All [Azure](azure.md) resources that belong to this project are placed inside the same [VNet](azure-vnet.md) so they can communicate securely.

```
Azure Region
  └── VNet: 10.0.0.0/16
        └── Subnet: 10.0.1.0/24
              └── VM (private IP: 10.0.1.4)
                  └── Public IP: 20.x.x.x (Internet-facing)
```

**CIDR notation:**
- `10.0.0.0/16` means the [VNet](azure-vnet.md) can contain addresses from 10.0.0.0 to 10.0.255.255 (65,536 addresses)
- `10.0.1.0/24` means the subnet can contain addresses from 10.0.1.0 to 10.0.1.255 (256 addresses)

### Subnet

A subnet is a subdivision of the VNet. Resources ([VMs](../infrastructure/virtual-machines.md)) are placed in subnets. In this project, one subnet is sufficient. Separate subnets would be used in larger projects to isolate different tiers (web, database, etc.).

### Public IP Address

A public IP is the Internet-facing address assigned to the VM. Users access Nextcloud through this IP via [HTTPS](../../networking/https.md). The public IP is assigned to the VM's network interface.

### Network Security Group (NSG)

An [NSG](azure-nsg.md) is a firewall for the subnet or VM. It contains a list of rules that allow or deny traffic based on:
- Direction: inbound (coming into the VM) or outbound (leaving the VM)
- Source IP / destination IP
- Port
- Protocol ([TCP](../../networking/tcp.md), UDP)

Rules are evaluated in order of priority (lower number = higher priority). The first matching rule wins.

## NSG Rules for This Project

### Inbound rules

| Priority | Name | Source | Port | Protocol | Action | Reason |
|---|---|---|---|---|---|---|
| 100 | Allow-[HTTPS](../../networking/https.md) | Internet | 443 | [TCP](../../networking/tcp.md) | Allow | Nextcloud web access |
| 110 | Allow-[SSH](../../protocols/ssh.md) | Your IP only | 22 | [TCP](../../networking/tcp.md) | Allow | Administration |
| 200 | Allow-[HTTP](../../networking/http.md) | Internet | 80 | [TCP](../../networking/tcp.md) | Allow | Redirect to [HTTPS](../../networking/https.md) |
| 4096 | Deny-All | Any | Any | Any | Deny | Block everything else |

### Outbound rules

- Allow all outbound by default (VM can reach the Internet for updates, API calls, etc.)

### What must NOT be exposed

| Service | Port | Rule |
|---|---|---|
| [PostgreSQL](../../databases/relational/postgresql.md) database | 5432 | Never exposed — internal [Docker](../../containers/docker.md) network only |
| Redis (if used) | 6379 | Never exposed — internal [Docker](../../containers/docker.md) network only |
| AI service (Ollama) | 11434 | Never exposed — internal [Docker](../../containers/docker.md) network only |
| [Docker Engine](../../containers/docker-daemon.md) API | 2376 | Never exposed |

## Defense in Depth

This project uses two layers of firewall protection:

```
Internet
   ↓
Azure NSG (Layer 1 — network level)
   ↓ Only ports 443, 22, 80 pass through
Ubuntu UFW Firewall (Layer 2 — OS level)
   ↓ Same rules enforced at the OS
Docker internal network
   ↓ DB, Redis, AI service — not reachable from outside Docker
Application
```

Even if one layer is misconfigured, the other provides protection. Access to [Azure](azure.md) resources themselves (portal, CLI, resource management) is a separate concern — see [Access Control & IAM](../../security/authorization/access-control-iam.md).

## SSH Security

[SSH](../../protocols/ssh.md) (port 22) is restricted to specific source IPs:
- Only the team's IP addresses or a VPN range can connect
- Key-based [authentication](../../security/auth/authentication.md) only (no passwords)
- Root login disabled

[Terraform](../iac/terraform.md) [NSG](azure-nsg.md) rule for restricted [SSH](../../protocols/ssh.md):

```hcl
security_rule {
  name                       = "Allow-SSH"
  priority                   = 110
  direction                  = "Inbound"
  access                     = "Allow"
  protocol                   = "Tcp"
  source_port_range          = "*"
  destination_port_range     = "22"
  source_address_prefix      = var.admin_ip   # only your IP
  destination_address_prefix = "*"
}
```

## Port Exposure Matrix (Full)

| Service | Internal Port | External Port | Internet Exposed | Reason |
|---|---|---|---|---|
| Nextcloud (nginx) | 80 | 443 | Yes ([HTTPS](../../networking/https.md)) | User file access |
| Nextcloud ([HTTP](../../networking/http.md) redirect) | 80 | 80 | Yes (redirect) | Redirect to [HTTPS](../../networking/https.md) |
| [SSH](../../protocols/ssh.md) | 22 | 22 | Restricted | Admin access |
| [PostgreSQL](../../databases/relational/postgresql.md) | 5432 | — | No | Internal [Docker](../../containers/docker.md) only |
| Redis | 6379 | — | No | Internal [Docker](../../containers/docker.md) only |
| Ollama / AI API | 11434 | — | No | Internal [Docker](../../containers/docker.md) only |

## How it Fits in This Project

Networking is owned by Member 4 (Computer Engineering / Networking). The VNet, Subnet, [NSG](azure-nsg.md), and [VM](../infrastructure/virtual-machines.md) are all defined in [Terraform](terraform.md). Member 4 also writes the port matrix and validates from an external perspective that no unauthorized ports are reachable. Member 2 (Cybersecurity) reviews the [NSG](azure-nsg.md) rules as part of the security review.

## Related

- [Microsoft Azure](azure.md)
- [Azure Virtual Network (VNet)](azure-vnet.md) — the general concept this file applies as a concrete single-VM [NSG](azure-nsg.md) rule set
- [Azure Network Security Group (NSG)](azure-nsg.md) — the full, general NSG reference this file's project-specific rules are one instance of
- [Terraform](terraform.md)
- [Virtual Machines](../infrastructure/virtual-machines.md)
- [Access Control & IAM](../../security/authorization/access-control-iam.md)
- [Nextcloud RAG Case Study](../../../guides/cloud/nextcloud-rag-case-study/nextcloud.md)
