# Azure Network Interface (NIC)

A **Network Interface (NIC)** is the [Azure](azure.md) resource that connects a Virtual Machine to a Virtual Network. It holds the VM's private IP address, optionally an attached Public IP, and is the attachment point for Network Security Groups. Every VM must have at least one NIC; high-throughput VMs can have multiple NICs connected to different subnets.

## NIC Anatomy

```
VM
└── NIC (Network Interface)
    ├── IP Configuration (ipconfig1)
    │   ├── Private IP  (from subnet address space)
    │   └── Public IP   (optional, attached resource)
    ├── NSG             (optional, overrides subnet NSG)
    ├── DNS Servers     (optional, overrides VNet defaults)
    └── Accelerated Networking (optional, SR-IOV bypass)
```

A NIC can have **multiple IP configurations** — useful when a VM serves multiple services on different IPs.

## Create & Manage (Azure CLI)

```bash
# Create a NIC (dynamic private IP, no public IP)
az network nic create \
  --resource-group my-rg \
  --name my-nic \
  --vnet-name my-vnet \
  --subnet my-subnet

# Create a NIC with static private IP and Public IP
az network nic create \
  --resource-group my-rg \
  --name my-nic \
  --vnet-name my-vnet \
  --subnet my-subnet \
  --private-ip-address 10.0.1.10 \
  --public-ip-address my-public-ip

# Show NIC details (private IP, public IP, MAC)
az network nic show \
  --resource-group my-rg \
  --name my-nic \
  --output table

# List NICs
az network nic list \
  --resource-group my-rg \
  --output table

# Attach NSG to NIC
az network nic update \
  --resource-group my-rg \
  --name my-nic \
  --network-security-group my-nsg

# Enable Accelerated Networking
az network nic update \
  --resource-group my-rg \
  --name my-nic \
  --accelerated-networking true

# Delete NIC (VM must be stopped and NIC detached first)
az network nic delete \
  --resource-group my-rg \
  --name my-nic
```

## IP Configuration

```bash
# List IP configurations on a NIC
az network nic ip-config list \
  --resource-group my-rg \
  --nic-name my-nic \
  --output table

# Add a secondary IP configuration
az network nic ip-config create \
  --resource-group my-rg \
  --nic-name my-nic \
  --name ipconfig2 \
  --private-ip-address 10.0.1.11

# Attach a Public IP to primary config
az network nic ip-config update \
  --resource-group my-rg \
  --nic-name my-nic \
  --name ipconfig1 \
  --public-ip-address my-public-ip

# Remove Public IP
az network nic ip-config update \
  --resource-group my-rg \
  --nic-name my-nic \
  --name ipconfig1 \
  --remove publicIpAddress
```

## Attach / Detach from a VM

```bash
# Attach NIC to a stopped VM
az vm nic add \
  --resource-group my-rg \
  --vm-name my-vm \
  --nics my-nic

# Detach NIC from a VM (VM must be stopped)
az vm nic remove \
  --resource-group my-rg \
  --vm-name my-vm \
  --nics my-nic
```

## Effective Security Rules (Troubleshooting)

Shows the merged set of [NSG](azure-nsg.md) rules actually applied to the NIC (NIC-level [NSG](azure-nsg.md) + subnet-level [NSG](azure-nsg.md)):

```bash
az network nic list-effective-nsg \
  --resource-group my-rg \
  --name my-nic \
  --output table
```

## Accelerated Networking

Accelerated Networking uses SR-IOV to bypass the hypervisor's virtual switch, reducing latency and CPU overhead. Requires a supported VM size (most D/E/F v3+ series).

- Enable only when the VM is **stopped**.
- Reduces latency by ~30–50% for network-intensive workloads.

## Terraform

```hcl
resource "azurerm_network_interface" "main" {
  name                = "my-nic"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location

  accelerated_networking_enabled = true

  ip_configuration {
    name                          = "ipconfig1"
    subnet_id                     = azurerm_subnet.main.id
    private_ip_address_allocation = "Static"
    private_ip_address            = "10.0.1.10"
    public_ip_address_id          = azurerm_public_ip.main.id  # optional
  }
}

# Associate NSG with NIC
resource "azurerm_network_interface_security_group_association" "main" {
  network_interface_id      = azurerm_network_interface.main.id
  network_security_group_id = azurerm_network_security_group.main.id
}

# Attach NIC to VM
resource "azurerm_linux_virtual_machine" "main" {
  name                = "my-vm"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  size                = "Standard_D2s_v3"
  network_interface_ids = [azurerm_network_interface.main.id]
  # ...
}
```

## NIC vs Subnet NSG — Which Takes Precedence?

NSGs can be attached at two levels:

| Level | Scope | Evaluation order |
|---|---|---|
| **Subnet [NSG](azure-nsg.md)** | All NICs in the subnet | Evaluated first (inbound) / last (outbound) |
| **NIC [NSG](azure-nsg.md)** | Only this NIC | Evaluated after subnet NSG (inbound) / before (outbound) |

For **inbound**: Subnet NSG → NIC NSG (both must allow for traffic to reach the VM).  
For **outbound**: NIC NSG → Subnet NSG (both must allow for traffic to leave).

## Related Concepts

- [Azure Public IP](./azure-public-ip.md) — attached to the NIC's IP configuration
- [NSG](./azure-nsg.md) — security rules applied at NIC or subnet level
- [Terraform](./terraform.md) — provision NICs as infrastructure-as-code
