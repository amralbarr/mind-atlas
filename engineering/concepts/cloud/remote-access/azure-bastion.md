# Azure Bastion

**Azure Bastion** is a fully managed PaaS service that provides browser-based [SSH](../../protocols/ssh.md)/RDP access to [Azure](../azure/azure.md) VMs through the [Azure](../azure/azure.md) Portal (or the native [SSH](../../protocols/ssh.md)/RDP client), over [TLS](../../networking/tls.md), **without the target VM needing a public IP address** and without opening any inbound [SSH](../../protocols/ssh.md)/RDP port on the VM's [NSG](../azure/azure-nsg.md).

## How it works

Bastion is deployed as its own resource inside your [VNet](../azure/azure-vnet.md), in a dedicated subnet named `AzureBastionSubnet`. It sits between the user and the target VM:

```
User's browser (portal.azure.com)
        │  HTTPS/TLS (443) to Bastion's public IP
        ▼
   Azure Bastion (in AzureBastionSubnet)
        │  SSH/RDP over the VNet's private IP space
        ▼
   Target VM (private IP only, no public IP needed)
```

- Only **Bastion itself** has a public IP — the VMs behind it never need one
- Access to Bastion (and therefore the VM) is gated by the user's [Azure](../azure/azure.md) sign-in ([Microsoft Entra ID](../azure/microsoft-entra-id.md)) and [Azure RBAC](../azure/azure-rbac.md) (`Reader` on the VM + `Virtual Machine Administrator/User Login` roles, or [NSG](../azure/azure-nsg.md)/VM read permissions depending on config) — not by an IP allowlist
- Session traffic never crosses the public internet to the VM directly; it stays inside [Azure](../azure/azure.md)'s backbone

## Why this fixes the "my IP changed" problem

An [NSG](../azure/azure-nsg.md) rule that allows [SSH](../../protocols/ssh.md) only from one admin's IP breaks the moment that person connects from a different network (home vs. office vs. mobile hotspot). Bastion sidesteps this entirely: there's no [SSH](../../protocols/ssh.md) port open to the internet at all, so there's no IP to keep updating. Anyone with the right Entra ID identity and [Azure RBAC](../azure/azure-rbac.md) role can connect from anywhere, and the [NSG](../azure/azure-nsg.md) for the target VM's subnet can deny all direct inbound [SSH](../../protocols/ssh.md)/RDP permanently.

## SKUs

| SKU | Notes |
|---|---|
| Developer | Free, limited features, no dedicated subnet required — good for dev/test |
| Basic | Standard managed Bastion, requires `AzureBastionSubnet` + public IP |
| Standard | Adds features like native client support, IP-based connection, shareable links |
| Premium | Adds session recording; supports private-only deployment (no public IP on Bastion itself) |

## Setup (Azure CLI)

```bash
# 1. Create a dedicated subnet named exactly AzureBastionSubnet (min /26)
az network vnet subnet create \
  --resource-group nextcloud-rg \
  --vnet-name nextcloud-vnet \
  --name AzureBastionSubnet \
  --address-prefixes 10.0.1.0/26

# 2. Create a public IP for Bastion
az network public-ip create \
  --resource-group nextcloud-rg \
  --name bastion-pip \
  --sku Standard

# 3. Create the Bastion host
az network bastion create \
  --resource-group nextcloud-rg \
  --name nextcloud-bastion \
  --public-ip-address bastion-pip \
  --vnet-name nextcloud-vnet \
  --sku Standard

# 4. Connect (native SSH client, requires Standard+ SKU)
az network bastion ssh \
  --name nextcloud-bastion \
  --resource-group nextcloud-rg \
  --target-resource-id <vm-resource-id> \
  --auth-type ssh-key \
  --username azureuser \
  --ssh-key ~/.ssh/id_rsa
```

Or connect entirely from the Portal: VM → Connect → Bastion → sign in with Entra ID → session opens in-browser, no [SSH](../../protocols/ssh.md) client needed.

## Bastion vs Just-in-Time access vs VPN Gateway

All three solve "how do I reach a VM without permanently exposing [SSH](../../protocols/ssh.md)/RDP to the internet," with different tradeoffs — see the [Azure secure remote access overview](../../../overviews/cloud/azure-secure-remote-access-options.md) for the full comparison.

## Related Concepts

- [Azure Just-in-Time VM Access](azure-jit-vm-access.md) — alternative: temporarily opens the [NSG](../azure/azure-nsg.md) instead of avoiding it
- [Azure VPN Gateway (Point-to-Site)](azure-vpn-gateway-point-to-site.md) — alternative: puts your machine on the [VNet](../azure/azure-vnet.md) instead
- [Azure NSG](../azure/azure-nsg.md) — the network-layer rule Bastion lets you close entirely
- [Azure RBAC](../azure/azure-rbac.md) — controls who is allowed to open a Bastion session
- [Microsoft Entra ID](../azure/microsoft-entra-id.md) — the identity Bastion authenticates against
