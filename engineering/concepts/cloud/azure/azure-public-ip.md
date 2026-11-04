# Azure Public IP

A **Public IP** is an [Azure](azure.md) resource that assigns a routable IPv4 (or IPv6) address to another [Azure](azure.md) resource — typically a VM's Network Interface, a Load Balancer, or an Application Gateway. Without a Public IP attached, a resource is only reachable within the virtual network.

## SKUs

| SKU | Allocation | Zone support | Use case |
|---|---|---|---|
| **Basic** (legacy) | Static or Dynamic | None | Dev/test only — being retired |
| **Standard** | Static only | Zone-redundant | All production workloads |

Always use **Standard SKU** for new deployments. Basic SKU is being retired.

## Allocation Types

- **Static** — the IP address is reserved and does not change even if the resource is stopped. Required by Standard SKU.
- **Dynamic** (Basic only) — IP is assigned when the resource starts; changes on stop/start.

## Create & Manage (Azure CLI)

```bash
# Create a Standard static Public IP
az network public-ip create \
  --resource-group my-rg \
  --name my-public-ip \
  --sku Standard \
  --allocation-method Static \
  --zone 1 2 3               # zone-redundant (omit for non-zonal)

# Show the assigned IP address
az network public-ip show \
  --resource-group my-rg \
  --name my-public-ip \
  --query ipAddress \
  --output tsv

# List all Public IPs
az network public-ip list \
  --resource-group my-rg \
  --output table

# Associate with a NIC (see Network Interface page)
az network nic ip-config update \
  --resource-group my-rg \
  --nic-name my-nic \
  --name ipconfig1 \
  --public-ip-address my-public-ip

# Dissociate Public IP from NIC
az network nic ip-config update \
  --resource-group my-rg \
  --nic-name my-nic \
  --name ipconfig1 \
  --remove publicIpAddress

# Delete Public IP (must be dissociated first)
az network public-ip delete \
  --resource-group my-rg \
  --name my-public-ip
```

## DNS Label

Attach a [DNS](../../networking/dns.md) label to get a hostname instead of a raw IP:

```bash
az network public-ip update \
  --resource-group my-rg \
  --name my-public-ip \
  --dns-name myapp-prod
# Result: myapp-prod.<region>.cloudapp.azure.com
```

## Terraform

```hcl
resource "azurerm_public_ip" "main" {
  name                = "my-public-ip"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  sku                 = "Standard"
  allocation_method   = "Static"
  zones               = ["1", "2", "3"]

  domain_name_label   = "myapp-prod"   # optional DNS label
}

# Get the IP address as an output
output "public_ip_address" {
  value = azurerm_public_ip.main.ip_address
}
```

## Associate with a VM (full Terraform example)

```hcl
resource "azurerm_network_interface" "main" {
  name                = "my-nic"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location

  ip_configuration {
    name                          = "ipconfig1"
    subnet_id                     = azurerm_subnet.main.id
    private_ip_address_allocation = "Dynamic"
    public_ip_address_id          = azurerm_public_ip.main.id
  }
}
```

## Security Considerations

- A Public IP alone does not open traffic — inbound ports are controlled by the **[NSG](azure-nsg.md)** attached to the [NIC](azure-network-interface.md) or subnet.
- Prefer **[Azure Bastion](../remote-access/azure-bastion.md)** over a Public IP for VM admin access (RDP/[SSH](../../protocols/ssh.md)) — Bastion provides secure browser-based access without exposing port 22/3389 to the internet.
- Use **[Azure](azure.md) Firewall** or **Application Gateway** as the single public-facing entry point instead of attaching Public IPs directly to individual VMs.
- Tag Public IPs with environment and owner metadata for cost attribution.

## Related Concepts

- [Network Interface (NIC)](./azure-network-interface.md) — the [NIC](azure-network-interface.md) is where the Public IP attaches
- [NSG](./azure-nsg.md) — controls which traffic reaches the Public IP
- [Terraform](./terraform.md) — provision Public IPs as infrastructure-as-code
