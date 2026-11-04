# Azure Secure Remote Access Options (SSH/RDP to a VM)

There are several ways to reach an [Azure](../../concepts/cloud/azure/azure.md) VM's management ports ([SSH](../../concepts/protocols/ssh.md) 22, RDP 3389) without permanently exposing them to the entire internet. They solve overlapping problems but at different layers and with different tradeoffs — this overview summarizes each and links to its atomic note.

## Why this comes up

A common trap: a VM's [NSG](../../concepts/cloud/azure/azure-nsg.md) allows [SSH](../../concepts/protocols/ssh.md) only from one admin's current IP address. This is a **network-layer** control. Meanwhile, team access to *manage* the VM (start/stop, view, configure) is often granted through [Microsoft Entra ID](../../concepts/cloud/azure/microsoft-entra-id.md) groups + an [Azure RBAC](../../concepts/cloud/azure/azure-rbac.md) role assignment on the resource group — an **identity-layer** control. These are separate systems: fixing the [RBAC](../../concepts/security/authorization/rbac.md)/group assignment does nothing to fix "my IP changed and the [NSG](../../concepts/cloud/azure/azure-nsg.md) rule no longer matches me," because [RBAC](../../concepts/security/authorization/rbac.md) governs the [Azure](../../concepts/cloud/azure/azure.md) control plane (portal/CLI/API) while the [NSG](../../concepts/cloud/azure/azure-nsg.md) governs the network data plane (what packets reach the VM). The options below are the actual fixes for the network-layer problem.

## The options

| Option | What it does | Identity-gated? | VM ever internet-facing? | Best for |
|---|---|---|---|---|
| **[NSG](../../concepts/cloud/azure/azure-nsg.md) IP allowlist** (baseline) | Only allows [SSH](../../concepts/protocols/ssh.md)/RDP from one specific IP | No — IP-based | Yes, to that IP | Simplest setup; breaks whenever the admin's IP changes |
| **[Azure Bastion](../../concepts/cloud/remote-access/azure-bastion.md)** | Browser/native-client [SSH](../../concepts/protocols/ssh.md)/RDP via a managed jump host in the [VNet](../../concepts/cloud/azure/azure-vnet.md); VM never gets a public IP or open port | Yes (Entra ID + [RBAC](../../concepts/security/authorization/rbac.md)) | Never | Regular admin access without a VPN client, especially for small teams |
| **[Just-in-Time (JIT) VM access](../../concepts/cloud/remote-access/azure-jit-vm-access.md)** | Defender for Cloud opens the [NSG](../../concepts/cloud/azure/azure-nsg.md) port temporarily, per request, per IP, per time window | Yes ([RBAC](../../concepts/security/authorization/rbac.md) checked per request) | Briefly, per request | Occasional access where Bastion's dedicated subnet/host isn't wanted |
| **[VPN Gateway (Point-to-Site)](../../concepts/cloud/remote-access/azure-vpn-gateway-point-to-site.md)** | Client VPN tunnel puts your machine on the [VNet](../../concepts/cloud/azure/azure-vnet.md); reach resources by private IP | Yes (cert or Entra ID) | Never | Teams needing ongoing private access to many [VNet](../../concepts/cloud/azure/azure-vnet.md) resources, not just one VM's [SSH](../../concepts/protocols/ssh.md) port |

## Recommendation for a small team with a changing-IP problem

[Azure Bastion](../../concepts/cloud/remote-access/azure-bastion.md) is generally the best fix when the actual complaint is "the [NSG](../../concepts/cloud/azure/azure-nsg.md) only trusts one IP and that IP keeps changing": it removes the IP dependency entirely and reuses the same Entra ID sign-in the team already has, rather than trading one maintenance burden (updating an IP rule) for another (managing certificates or JIT requests).

## Related

- [Azure RBAC](../../concepts/cloud/azure/azure-rbac.md) — identity-based control-plane access, not a substitute for any option above
- [Azure NSG](../../concepts/cloud/azure/azure-nsg.md) — the network-layer rule all of these options interact with
- [Microsoft Entra ID](../../concepts/cloud/azure/microsoft-entra-id.md) — the identity provider behind [RBAC](../../concepts/security/authorization/rbac.md), Bastion, and Entra-based P2S auth
- [Cloud Providers](cloud-providers.md)
