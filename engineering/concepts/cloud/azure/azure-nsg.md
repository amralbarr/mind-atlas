# Azure Network Security Group (NSG)

A **Network Security Group (NSG)** is a stateful firewall resource in [Azure](azure.md) that contains a list of security rules to allow or deny inbound and outbound network traffic. An NSG can be associated with one or more **subnets** or **Network Interfaces (NICs)**, and the same NSG can be reused across multiple resources.

## How NSGs Work

NSGs are **stateful** — if you allow inbound [TCP](../../networking/tcp.md) on port 443, the response traffic is automatically allowed outbound without needing an explicit rule. This is the same behavior as [AWS](../infrastructure/aws.md) Security Groups.

Rules are evaluated in **priority order** (lowest number = highest priority, evaluated first). The first matching rule wins; remaining rules are skipped. If no rule matches, the default rules apply.

## Default Rules (always present, cannot be deleted)

### Inbound defaults

| Priority | Name | Source | Destination | Port | Action |
|---|---|---|---|---|---|
| 65000 | AllowVnetInBound | VirtualNetwork | VirtualNetwork | Any | Allow |
| 65001 | AllowAzureLoadBalancerInBound | AzureLoadBalancer | Any | Any | Allow |
| 65500 | DenyAllInBound | Any | Any | Any | **Deny** |

### Outbound defaults

| Priority | Name | Source | Destination | Port | Action |
|---|---|---|---|---|---|
| 65000 | AllowVnetOutBound | VirtualNetwork | VirtualNetwork | Any | Allow |
| 65001 | AllowInternetOutBound | Any | Internet | Any | Allow |
| 65500 | DenyAllOutBound | Any | Any | Any | **Deny** |

## Create & Manage (Azure CLI)

```bash
# Create NSG
az network nsg create \
  --resource-group my-rg \
  --name my-nsg

# List NSGs
az network nsg list \
  --resource-group my-rg \
  --output table

# Show NSG rules
az network nsg show \
  --resource-group my-rg \
  --name my-nsg

# Delete NSG
az network nsg delete \
  --resource-group my-rg \
  --name my-nsg
```

## Security Rules (Azure CLI)

```bash
# Allow inbound HTTPS (port 443) from anywhere
az network nsg rule create \
  --resource-group my-rg \
  --nsg-name my-nsg \
  --name allow-https \
  --priority 100 \
  --direction Inbound \
  --access Allow \
  --protocol Tcp \
  --source-address-prefixes '*' \
  --source-port-ranges '*' \
  --destination-address-prefixes '*' \
  --destination-port-ranges 443

# Allow inbound SSH only from a specific IP
az network nsg rule create \
  --resource-group my-rg \
  --nsg-name my-nsg \
  --name allow-ssh-admin \
  --priority 110 \
  --direction Inbound \
  --access Allow \
  --protocol Tcp \
  --source-address-prefixes 203.0.113.5/32 \
  --source-port-ranges '*' \
  --destination-address-prefixes '*' \
  --destination-port-ranges 22

# Deny all inbound RDP (explicit deny before default)
az network nsg rule create \
  --resource-group my-rg \
  --nsg-name my-nsg \
  --name deny-rdp \
  --priority 200 \
  --direction Inbound \
  --access Deny \
  --protocol Tcp \
  --source-address-prefixes '*' \
  --source-port-ranges '*' \
  --destination-address-prefixes '*' \
  --destination-port-ranges 3389

# List rules
az network nsg rule list \
  --resource-group my-rg \
  --nsg-name my-nsg \
  --output table

# Delete a rule
az network nsg rule delete \
  --resource-group my-rg \
  --nsg-name my-nsg \
  --name allow-ssh-admin
```

## Associate NSG with Subnet or NIC

```bash
# Associate with a subnet
az network vnet subnet update \
  --resource-group my-rg \
  --vnet-name my-vnet \
  --name my-subnet \
  --network-security-group my-nsg

# Associate with a NIC
az network nic update \
  --resource-group my-rg \
  --name my-nic \
  --network-security-group my-nsg

# Remove NSG from subnet
az network vnet subnet update \
  --resource-group my-rg \
  --vnet-name my-vnet \
  --name my-subnet \
  --network-security-group ""

# Remove NSG from NIC
az network nic update \
  --resource-group my-rg \
  --name my-nic \
  --network-security-group ""
```

## Service Tags (instead of IP ranges)

Service tags are managed groups of IP prefixes for [Azure](azure.md) services. Use them instead of hardcoding IP ranges — [Azure](azure.md) keeps them updated automatically.

| Tag | Meaning |
|---|---|
| `Internet` | All public internet IPs |
| `VirtualNetwork` | All IPs in the [VNet](azure-vnet.md) and peered VNets |
| `AzureLoadBalancer` | [Azure](azure.md) infrastructure health probes |
| `Storage` | [Azure](azure.md) Storage service IPs |
| `Sql` | [Azure](azure.md) [SQL](../../databases/relational/sql.md) service IPs |
| `AppService` | [Azure](azure.md) App Service outbound IPs |
| `AzureCloud` | All [Azure](azure.md) datacenter IPs |

```bash
# Allow inbound from Azure Load Balancer (health probes)
az network nsg rule create \
  --resource-group my-rg \
  --nsg-name my-nsg \
  --name allow-lb-probe \
  --priority 90 \
  --direction Inbound \
  --access Allow \
  --protocol '*' \
  --source-address-prefixes AzureLoadBalancer \
  --destination-port-ranges '*'
```

## Effective Security Rules (Troubleshooting)

Shows the merged rules from both the [NIC](azure-network-interface.md)-level and subnet-level NSGs actually applied to a [NIC](azure-network-interface.md):

```bash
az network nic list-effective-nsg \
  --resource-group my-rg \
  --name my-nic \
  --output table
```

Use this when traffic is unexpectedly blocked or allowed — it shows which rule matched.

## NSG Flow Logs (Monitoring)

NSG Flow Logs record which traffic was allowed or denied, for security auditing and troubleshooting:

```bash
# Enable flow logs (requires a storage account)
az network watcher flow-log create \
  --resource-group my-rg \
  --name my-nsg-flow-log \
  --nsg my-nsg \
  --storage-account mystorageaccount \
  --enabled true \
  --retention 7    # days
```

Logs are written to the storage account in [JSON](../../programming/fundamentals/json.md) format and can be analyzed with [Azure](azure.md) Traffic Analytics.

## Terraform

```hcl
resource "azurerm_network_security_group" "main" {
  name                = "my-nsg"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location

  security_rule {
    name                       = "allow-https"
    priority                   = 100
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "443"
    source_address_prefix      = "*"
    destination_address_prefix = "*"
  }

  security_rule {
    name                       = "allow-ssh-admin"
    priority                   = 110
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "22"
    source_address_prefix      = "203.0.113.5/32"
    destination_address_prefix = "*"
  }
}

# Associate with subnet
resource "azurerm_subnet_network_security_group_association" "main" {
  subnet_id                 = azurerm_subnet.main.id
  network_security_group_id = azurerm_network_security_group.main.id
}

# Associate with NIC
resource "azurerm_network_interface_security_group_association" "main" {
  network_interface_id      = azurerm_network_interface.main.id
  network_security_group_id = azurerm_network_security_group.main.id
}
```

## NSG vs Azure Firewall

| | NSG | [Azure](azure.md) Firewall |
|---|---|---|
| Level | [NIC](azure-network-interface.md) / Subnet (L3/L4) | [VNet](azure-vnet.md) boundary (L4/L7) |
| Rules | IP, port, protocol | IP, port, FQDN, URL, [TLS](../../networking/tls.md) inspection |
| Cost | Free | ~$1/hour + data |
| Logging | Flow logs to storage | [Azure](azure.md) Monitor, Log Analytics |
| Best for | Per-resource traffic control | Central network perimeter control |

Use NSGs for per-resource rules; use [Azure](azure.md) Firewall for organization-wide egress control and L7 inspection.

## Security Best Practices

- Deny inbound by default — only open ports you explicitly need
- Never allow `0.0.0.0/0` on port 22 ([SSH](../../protocols/ssh.md)) or 3389 (RDP) to the internet — use [Azure Bastion](../remote-access/azure-bastion.md) or restrict to your IP
- Use **Service Tags** instead of hardcoded IP ranges for Azure services
- Apply NSGs at the **subnet** level for broad policy, at the **[NIC](azure-network-interface.md)** level only for per-VM exceptions
- Enable **Flow Logs** in production for audit trails
- Keep rule priorities spaced (100, 200, 300) to leave room for future insertions

## Related Concepts

- [Network Interface (NIC)](./azure-network-interface.md) — NSG can be attached here
- [Azure Public IP](./azure-public-ip.md) — NSG controls what reaches the Public IP
- [Azure Virtual Network (VNet)](azure-vnet.md) — the address space and isolation boundary an NSG's rules are scoped within
- [WAF](../../security/attacks/waf.md) — the L7 content-inspection layer upstream of NSG's L3/L4 rules, not a replacement for them
- [Terraform](./terraform.md) — provision NSGs as infrastructure-as-code
- [Access Control & IAM](../../security/authorization/access-control-iam.md) — identity-based access vs network-based access
- [Azure RBAC](azure-rbac.md) — the identity-layer control NSG is often conflated with, but doesn't replace
- [Azure secure remote access options](../../../overviews/cloud/azure-secure-remote-access-options.md) — Bastion, JIT, and VPN Gateway as alternatives to a static [SSH](../../protocols/ssh.md) IP allowlist
