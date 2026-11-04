# Terraform CLI

For a conceptual overview of [Terraform](../../concepts/cloud/iac/terraform.md) — what it is, why we use it, and how it fits into this project's [Azure](../../concepts/cloud/azure/azure.md) workflow — see [concepts/cloud/terraform.md](../../concepts/cloud/iac/terraform.md).

[Terraform](../../concepts/cloud/iac/terraform.md) is an open-source [Infrastructure as Code](../../concepts/cloud/iac/infrastructure-as-code.md) (IaC) tool by HashiCorp. It lets you define cloud infrastructure — [virtual machines](../../concepts/cloud/infrastructure/virtual-machines.md), networks, firewalls, storage — in human-readable `.tf` files, then create, update, and destroy that infrastructure automatically with simple commands. Works with [Azure](../../concepts/cloud/azure/azure.md), [AWS](../../concepts/cloud/infrastructure/aws.md), [GCP](../../concepts/cloud/infrastructure/gcp.md), and 1000+ providers.

## Install

| OS | Method |
|---|---|
| Windows (winget) | `winget install HashiCorp.Terraform` |
| Windows (manual) | Download zip from https://developer.hashicorp.com/terraform/downloads, extract, add to PATH |
| Mac | `brew tap hashicorp/tap && brew install hashicorp/tap/terraform` |
| Linux / WSL2 (apt repository, recommended) | See below |
| Linux / WSL2 (manual binary) | See below |

**Option A — HashiCorp apt repository (recommended, keeps [Terraform](../../concepts/cloud/iac/terraform.md) updatable via `apt`):**

```bash
sudo apt update && sudo apt install -y gnupg software-properties-common

wget -O- https://apt.releases.hashicorp.com/gpg | \
  gpg --dearmor | \
  sudo tee /usr/share/keyrings/hashicorp-archive-keyring.gpg > /dev/null

echo "deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] \
  https://apt.releases.hashicorp.com $(lsb_release -cs) main" | \
  sudo tee /etc/apt/sources.list.d/hashicorp.list

sudo apt update && sudo apt install terraform
```

**Option B — download the binary directly:**

```bash
curl -O https://releases.hashicorp.com/terraform/1.9.5/terraform_1.9.5_linux_amd64.zip
unzip terraform_1.9.5_linux_amd64.zip
sudo mv terraform /usr/local/bin/
```

**Verify:**

```bash
terraform --version    # Terraform v1.7.x or higher
```

## Core Commands

```bash
terraform init       # initialize: download provider plugins
terraform plan       # preview: what will be created / changed / destroyed
terraform apply      # execute: create or update resources in the cloud
terraform destroy    # tear down: remove all managed resources
terraform output     # print output values (e.g., VM public IP)
terraform validate   # check configuration files for syntax errors
terraform fmt        # auto-format .tf files
terraform show       # display current state in human-readable form
```

## File Structure

```
infrastructure/terraform/
├── providers.tf    # cloud provider and authentication
├── main.tf         # resource definitions
├── variables.tf    # input variable declarations
├── outputs.tf      # output value declarations
└── terraform.tfstate   # auto-generated state file — never edit manually
```

## Basic Syntax

```hcl
# Declare a variable
variable "location" {
  description = "Azure region"
  type        = string
  default     = "East US"
}

# Define a resource
resource "azurerm_resource_group" "main" {
  name     = "my-project-rg"
  location = var.location

  tags = {
    project     = "my-project"
    environment = "dev"
  }
}

# Declare an output
output "resource_group_name" {
  value = azurerm_resource_group.main.name
}
```

## Terraform State

[Terraform](../../concepts/cloud/iac/terraform.md) records all created resources in `terraform.tfstate`. This file:
- Is auto-generated — never edit it manually.
- Must be kept in sync — always use `terraform apply` to make changes, never the cloud console.
- Contains sensitive data — never commit to Git.

**`.gitignore` entries:**

```gitignore
*.tfstate
*.tfstate.backup
.terraform/
.terraform.lock.hcl
```

**For teams:** Use a remote backend ([Azure Blob Storage](../../concepts/cloud/azure/azure-blob-storage.md), [Terraform](../../concepts/cloud/iac/terraform.md) Cloud) so all contributors share the same state:

```hcl
# providers.tf — remote state in Azure
terraform {
  backend "azurerm" {
    resource_group_name  = "terraform-state-rg"
    storage_account_name = "tfstateaccount"
    container_name       = "tfstate"
    key                  = "project.terraform.tfstate"
  }
}
```

## Typical Workflow

```bash
cd infrastructure/terraform/

# 1. First time only
terraform init

# 2. Before every change — review what will happen
terraform plan

# 3. Apply changes
terraform apply
# Type "yes" to confirm

# 4. Check outputs
terraform output

# 5. When done — tear everything down to avoid cloud costs
terraform destroy
# Type "yes" to confirm
```

## Tips

- Always run `terraform plan` before `terraform apply` — read it carefully.
- Run `terraform destroy` on any environment you are not actively using — cloud resources cost money.
- Use `terraform fmt` before committing to keep `.tf` files consistently formatted.
- Use `variables.tf` for all configurable values — never hardcode region names, VM sizes, or IPs in `main.tf`.
- Add `tags` to every resource so you can identify and filter them in the cloud console.

## Related
- [../../concepts/cloud/terraform.md](../../concepts/cloud/iac/terraform.md)
- [../../concepts/cloud/azure.md](../../concepts/cloud/azure/azure.md)
- [../../commands/azure.md](../../commands/azure.md)
