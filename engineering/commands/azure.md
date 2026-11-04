# Azure CLI

The [Azure](../concepts/cloud/azure/azure.md) CLI (`az`) is a command-line tool for managing [Azure](../concepts/cloud/azure/azure.md) resources directly from the terminal. It lets you create, inspect, and delete resource groups, [virtual machines](../concepts/cloud/infrastructure/virtual-machines.md), storage accounts, and more — without using the [Azure](../concepts/cloud/azure/azure.md) Portal web UI. Essential for scripting and automation alongside [Terraform](../concepts/cloud/iac/terraform.md).

## Install

| OS | Method |
|---|---|
| Windows | `winget install Microsoft.AzureCLI` |
| Mac | `brew install azure-cli` |
| Linux / WSL2 | `curl -sL https://aka.ms/InstallAzureCLIDeb \| sudo bash` |

**Verify:**

```bash
az --version    # azure-cli 2.x.x or higher
```

## Login

```bash
# Interactive browser login (recommended)
az login

# Login with a service principal (CI/CD pipelines)
az login --service-principal \
  --username <app-id> \
  --password <secret> \
  --tenant <tenant-id>

# Check currently logged-in account
az account show

# List all subscriptions
az account list --output table

# Set active subscription
az account set --subscription "<subscription-name-or-id>"
```

## Core Commands

```bash
# Resource Groups
az group list --output table
az group show --name my-rg
az group create --name my-rg --location "East US"
az group delete --name my-rg --yes

# Virtual Machines
az vm list --output table
az vm show --resource-group my-rg --name my-vm
az vm start --resource-group my-rg --name my-vm
az vm stop --resource-group my-rg --name my-vm
az vm list-ip-addresses --resource-group my-rg --name my-vm

# Public IP
az network public-ip show \
  --resource-group my-rg \
  --name my-vm-ip \
  --query "ipAddress" \
  --output tsv

# Storage accounts (for Terraform remote state)
az storage account list --output table
az storage container list --account-name mystorageaccount --output table

# Network Security Groups
az network nsg list --output table
az network nsg rule list --resource-group my-rg --nsg-name my-nsg --output table
```

## Integration with Terraform

[Terraform](../concepts/cloud/iac/terraform.md) uses your active [Azure](../concepts/cloud/azure/azure.md) CLI login for [authentication](../concepts/security/auth/authentication.md) automatically:

```hcl
# providers.tf
provider "azurerm" {
  features {}
  # No credentials needed — inherits from `az login`
}
```

Run `az login` before any `terraform apply` command.

## Useful Patterns

```bash
# Get the public IP of a VM in one command
az vm list-ip-addresses \
  --resource-group my-rg \
  --name my-vm \
  --query "[0].virtualMachine.network.publicIpAddresses[0].ipAddress" \
  --output tsv

# Watch VM provisioning state
az vm show \
  --resource-group my-rg \
  --name my-vm \
  --query "provisioningState" \
  --output tsv

# List all resources in a group
az resource list --resource-group my-rg --output table
```

## Tips

- Run `az login` at the start of each working session — tokens expire.
- Use `--output table` for readable terminal output; `--output json` for scripting.
- Use `--query` with JMESPath expressions to extract specific fields.
- Use `az account set` if you have multiple [Azure](../concepts/cloud/azure/azure.md) subscriptions to ensure commands target the right one.

## Related
- [../concepts/cloud/azure.md](../concepts/cloud/azure/azure.md)
- [../installation/linux/terraform.md](../installation/linux/terraform.md)
