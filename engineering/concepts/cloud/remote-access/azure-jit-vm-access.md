# Just-in-Time (JIT) VM Access

**Just-in-Time (JIT) VM access** is a feature of **Microsoft Defender for Cloud** that keeps management ports ([SSH](../../protocols/ssh.md) 22, RDP 3389, etc.) closed on a VM's [NSG](../azure/azure-nsg.md) by default, and only opens them — to a specific requester's IP, for a specific port, for a limited time window — when an authorized user explicitly requests access.

## How it works

1. Defender for Cloud (Defender for Servers Plan 2) ensures a "deny all inbound" rule exists on the selected management ports for the VM's [NSG](../azure/azure-nsg.md) (and [Azure](../azure/azure.md) Firewall, if used)
2. A user requests access via the Portal, CLI, or [REST](../../backend/api/rest.md) API: which VM, which port, source IP, and duration (e.g. up to 3 hours)
3. Defender for Cloud checks the requester has the necessary [Azure RBAC](../azure/azure-rbac.md) permission on that VM before approving
4. On approval, it inserts a temporary high-priority [NSG](../azure/azure-nsg.md) rule allowing inbound traffic on that port from that IP
5. When the time window expires, Defender for Cloud automatically reverts the [NSG](../azure/azure-nsg.md) to its previous (closed) state — already-established connections aren't dropped, but no new ones can start

```
Request access (port 22, my current IP, 3 hours)
        ↓
Defender for Cloud checks Azure RBAC permission
        ↓
NSG temporarily updated: allow 22 from <requester IP>
        ↓
... 3 hours pass ...
        ↓
NSG automatically reverted: deny 22 from everywhere
```

## Why this fixes the "my IP changed" problem — with a caveat

JIT solves the *static allowlist* problem differently than [Azure Bastion](azure-bastion.md): instead of eliminating the open port, it re-opens the port on-demand for whatever IP the user currently has, every time they need access. There's no stale rule to break when someone connects from a new network — but the request has to happen freshly each session, and it still means [SSH](../../protocols/ssh.md)/RDP is briefly reachable from a public IP over the internet (unlike Bastion, where the VM's port is never internet-facing at all).

## Setup (conceptual — via Portal or CLI)

```bash
# Requires Defender for Servers Plan 2 enabled on the subscription
az security pricing create --name VirtualMachines --tier standard

# Configure JIT policy on a VM (example structure, via REST API / ARM)
az rest --method put \
  --uri "https://management.azure.com/subscriptions/<sub>/resourceGroups/nextcloud-rg/providers/Microsoft.Security/locations/<region>/jitNetworkAccessPolicies/default?api-version=2020-01-01" \
  --body '{
    "properties": {
      "virtualMachines": [{
        "id": "<vm-resource-id>",
        "ports": [{
          "number": 22,
          "protocol": "*",
          "allowedSourceAddressPrefix": "*",
          "maxRequestAccessDuration": "PT3H"
        }]
      }]
    }
  }'

# Request access (once policy exists) — from Portal: VM → Connect → Just-in-time access → Request access
```

## JIT vs Bastion vs VPN Gateway

| | JIT | [Bastion](azure-bastion.md) | [VPN Gateway P2S](azure-vpn-gateway-point-to-site.md) |
|---|---|---|---|
| VM ever internet-facing? | Briefly, per request | Never | Never (private IP only) |
| Identity-gated? | Yes ([Azure RBAC](../azure/azure-rbac.md) checks the request) | Yes (Entra ID + [RBAC](../../security/authorization/rbac.md)) | Yes (cert or Entra ID) |
| Setup overhead | Low (policy + Defender plan) | Medium (dedicated subnet + host) | Higher (gateway + client config) |
| Best for | Occasional admin access to a few VMs | Regular portal-based [SSH](../../protocols/ssh.md)/RDP without VPN client | Broader private-network access to many [VNet](../azure/azure-vnet.md) resources, not just [SSH](../../protocols/ssh.md) |

See the [Azure secure remote access overview](../../../overviews/cloud/azure-secure-remote-access-options.md) for the full comparison including plain [NSG](../azure/azure-nsg.md) IP allowlisting.

## Related Concepts

- [Azure NSG](../azure/azure-nsg.md) — the rules JIT temporarily modifies
- [Azure RBAC](../azure/azure-rbac.md) — gates who can request JIT access
- [Azure Bastion](azure-bastion.md) — the alternative that avoids exposing the port at all
