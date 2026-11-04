# Azure VPN Gateway — Point-to-Site (P2S)

**Azure VPN Gateway** is a managed VPN service attached to a [VNet](../azure/azure-vnet.md). In **Point-to-Site (P2S)** mode, an individual client machine establishes a VPN connection from wherever it is (home, office, coffee shop) directly into the [VNet](../azure/azure-vnet.md) — once connected, the client can reach any resource in the VNet by its **private IP**, as if it were on the same local network.

## How it works

```
Your laptop (VPN client)
   │  encrypted tunnel (OpenVPN / IKEv2 / SSTP, typically over TCP 443)
   ▼
Azure VPN Gateway (deployed in the VNet's GatewaySubnet)
   │  routes traffic over the VNet's private address space
   ▼
VM / any resource in the VNet — reached via its private IP, e.g. 10.0.1.4
```

Point-to-site requires a **route-based** VPN gateway. Once the tunnel is up, the client machine gets an IP from a configured client address pool and can route to the VNet's private CIDR range.

## Authentication options

| Method | How it works |
|---|---|
| **Certificate-based** | A root certificate is uploaded to [Azure](../azure/azure.md); client certificates generated from it are installed on each client machine and used to authenticate the tunnel |
| **RADIUS** | Authenticates against an existing RADIUS server (e.g. tied to on-prem AD) |
| **[Microsoft Entra ID](../azure/microsoft-entra-id.md)** | Authenticates using the user's Entra ID sign-in — ties VPN access to the same identity used elsewhere in [Azure](../azure/azure.md) (see [Microsoft Entra ID](../azure/microsoft-entra-id.md)) |

## Why this fixes the "my IP changed" problem

Once connected via P2S VPN, [SSH](../../protocols/ssh.md)/RDP traffic to a VM never needs to be exposed to the public internet at all — the target VM's [NSG](../azure/azure-nsg.md) only needs to allow [SSH](../../protocols/ssh.md) from the VNet's private address range (or `VirtualNetwork` service tag), not from any particular public IP. The client's *public* IP becomes irrelevant because the VPN tunnel, not an [NSG](../azure/azure-nsg.md) allow rule, is what grants reachability — and the tunnel is authenticated by certificate/Entra ID rather than by source IP.

## Setup (Azure CLI, certificate auth)

```bash
# 1. Create a dedicated GatewaySubnet
az network vnet subnet create \
  --resource-group nextcloud-rg \
  --vnet-name nextcloud-vnet \
  --name GatewaySubnet \
  --address-prefixes 10.0.255.0/27

# 2. Create a public IP for the gateway
az network public-ip create \
  --resource-group nextcloud-rg \
  --name vpn-gw-pip \
  --sku Standard

# 3. Create the VPN gateway (route-based, VpnGw1 SKU)
az network vnet-gateway create \
  --resource-group nextcloud-rg \
  --name nextcloud-vpn-gw \
  --public-ip-address vpn-gw-pip \
  --vnet nextcloud-vnet \
  --gateway-type Vpn \
  --vpn-type RouteBased \
  --sku VpnGw1 \
  --address-prefixes 172.16.0.0/24 \
  --client-protocol OpenVPN

# 4. Upload the root certificate's public key for P2S auth
az network vnet-gateway root-cert create \
  --resource-group nextcloud-rg \
  --gateway-name nextcloud-vpn-gw \
  --name P2SRootCert \
  --public-cert-data <base64-cert-data>

# 5. Download the client config (VPN client profile) from the Portal or CLI
az network vnet-gateway vpn-client generate \
  --resource-group nextcloud-rg \
  --name nextcloud-vpn-gw
```

## VPN Gateway P2S vs Bastion vs JIT

VPN Gateway grants broad, ongoing private-network access to the whole VNet (any resource, any protocol) rather than a single [SSH](../../protocols/ssh.md)/RDP session to one VM — it's the heavier-weight option, better suited when a team needs regular private-IP access to multiple resources, not just occasional VM admin access. See the [Azure secure remote access overview](../../../overviews/cloud/azure-secure-remote-access-options.md) for the full comparison.

## Related Concepts

- [Azure Bastion](azure-bastion.md) — lighter-weight alternative for single-VM [SSH](../../protocols/ssh.md)/RDP via the Portal
- [Azure Just-in-Time VM Access](azure-jit-vm-access.md) — alternative that briefly opens the [NSG](../azure/azure-nsg.md) instead
- [Azure NSG](../azure/azure-nsg.md) — still needed on the VM, but only needs to allow the VNet range once P2S is in place
- [Microsoft Entra ID](../azure/microsoft-entra-id.md) — supported as a P2S [authentication](../../security/auth/authentication.md) method
