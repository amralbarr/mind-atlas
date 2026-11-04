# Azure Virtual Network (VNet)

A **Virtual Network (VNet)** is a private, isolated network inside [Azure](azure.md) — the cloud equivalent of a corporate LAN, scoped to one subscription and region. Every [Azure](azure.md) resource that needs to communicate privately with another (a VM, a database, an App Service with private networking enabled) is placed inside a VNet so that traffic between them never has to traverse the public internet at all.

```
Azure Region
  └── VNet: 10.0.0.0/16
        ├── Subnet A: 10.0.1.0/24   (application tier)
        ├── Subnet B: 10.0.2.0/24   (data tier)
        └── Subnet C: 10.0.3.0/24   (private endpoints)
```

## Address Space and Subnets

A VNet is defined by a CIDR block (e.g. `10.0.0.0/16`, giving 65,536 addresses) and is then divided into **subnets** — smaller CIDR ranges within it (e.g. `10.0.1.0/24`, 256 addresses), each typically isolating one tier of an application (web, application, data) so that [NSG](azure-nsg.md) rules and routing policy can differ per tier without affecting the others. This tiered-subnet pattern is also exactly what the [concrete NSG rule set](networking-vnet-nsg.md) example applies in practice for a single-VM deployment.

## VNet Peering

Two VNets — even across different subscriptions — can be connected directly via **peering**, so resources in one VNet reach resources in the other using private IP addresses, without any gateway or public routing in between. Peered VNets must have non-overlapping address spaces; peering is non-transitive by default (if A peers with B and B peers with C, A cannot reach C through B without an explicit additional peering or a hub-spoke topology).

## Private Endpoints vs. Service Endpoints

Both let a VNet-resident resource reach a managed [Azure](azure.md) PaaS service (Storage, [Azure AI Search](azure-ai-search.md), [Azure OpenAI](azure-openai.md)) without that traffic crossing the public internet — but they work differently and have a real security distinction:

| | Service Endpoint | Private Endpoint |
|---|---|---|
| **What it does** | Routes traffic to the PaaS service over the [Azure](azure.md) backbone, but the service still has a public IP/endpoint | Gives the PaaS service an actual **private IP address inside the VNet** — the public endpoint can be disabled entirely |
| **Network isolation** | Traffic stays on [Azure](azure.md)'s backbone, but the service remains reachable from outside the VNet unless firewalled separately | Genuinely private — the service is only reachable through that specific private IP, from networks that can route to it |
| **[DNS](../../networking/dns.md)** | No change — the service's public [DNS](../../networking/dns.md) name still resolves to its public IP | Requires [Azure](azure.md) Private [DNS](../../networking/dns.md) zone integration so the service's name resolves to the private IP instead |

For a system with strict data-residency or network-isolation requirements — the kind this handbook's [Azure RAG platform map](../../../interview/interview-01/22-azure-rag-platform-map.md) assumes throughout — Private Endpoints are the default choice: they're what actually lets a service's public endpoint be disabled, closing the gap Service Endpoints leave open.

## VNet Integration for PaaS Compute

App Service, Container Apps, and [Azure Functions](azure-functions.md) aren't VNet-resident by default — they run in Microsoft-managed infrastructure outside any customer VNet. **VNet integration** gives the *outbound* calls from one of these services a path into a VNet (so it can reach a private-endpoint-only database, for instance); it does not by itself make the service's own *inbound* endpoint private — that's a separate configuration (private endpoints for inbound access, VNet integration for outbound).

## How NSG and WAF Layer on Top

A VNet alone provides isolation and address space — it has no concept of "allow this traffic, deny that traffic" on its own. That enforcement comes from layers applied on top:

```
Public internet
     │
     ▼
WAF                     ← L7 content inspection, at the edge
     │
     ▼
VNet + NSG              ← L3/L4 IP/port/protocol rules, this file + NSG
     │
     ▼
Private Endpoints        ← PaaS services reachable only inside the VNet
```

See [WAF](../../security/attacks/waf.md) for the content-inspection layer and [NSG](azure-nsg.md) for the per-subnet/per-[NIC](azure-network-interface.md) rule layer — a VNet is the address space and isolation boundary both of those enforcement layers operate within, not a replacement for either.

## Common Questions

**Does putting a resource inside a VNet make it secure by default?**
> No — a VNet provides address space and isolation, but with no rules attached, [Azure](azure.md)'s own [NSG default rules](azure-nsg.md#default-rules-always-present-cannot-be-deleted) still apply (deny all inbound from outside the VNet, allow all within it). Real security comes from the [NSG](azure-nsg.md) rules, private endpoint configuration, and [WAF](../../security/attacks/waf.md) layered on top — the VNet itself is the boundary those controls are scoped to, not a security control on its own.

**When is VNet peering preferred over a hub-spoke topology with a VPN Gateway?**
> Peering is the simpler, cheaper option for direct VNet-to-VNet connectivity within Azure, with no bandwidth throttling or gateway cost. A hub-spoke topology (a central "hub" VNet other "spoke" VNets peer with, often with a VPN Gateway or Azure Firewall in the hub) is preferred once there are many VNets needing centralized traffic inspection or connectivity to on-premises networks, rather than a full mesh of direct peerings between every pair.

**Can two peered VNets have overlapping address spaces?**
> No — peering requires non-overlapping CIDR ranges, which is why address space planning across a whole organization's VNets needs to happen up front, before VNets are created, rather than being fixed later without re-addressing resources.

## Related

- [NSG](azure-nsg.md) — the firewall rule layer applied within a VNet, at the subnet or [NIC](azure-network-interface.md) level
- [WAF](../../security/attacks/waf.md) — the L7 content-inspection layer that sits upstream of the VNet boundary
- [Azure Networking: VNet & NSG](networking-vnet-nsg.md) — a concrete, project-specific [NSG](azure-nsg.md) rule set and port-exposure matrix built on top of a VNet like this one
- [Azure Public IP](azure-public-ip.md) — the internet-facing address assigned separately from the VNet's private address space
- [Azure Network Interface](azure-network-interface.md) — where a VM's VNet membership and [NSG](azure-nsg.md) association actually attach
- [Azure RBAC](azure-rbac.md) — identity-based access control, a separate concern from VNet/NSG's network-based access control
- [Azure RAG Platform Map](../../../interview/interview-01/22-azure-rag-platform-map.md) — VNet, Private Endpoints, and Private DNS as Layer 2 of a full enterprise architecture
