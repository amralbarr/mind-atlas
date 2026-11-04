# Terraform

## What is it?

Terraform is an open-source [Infrastructure as Code](infrastructure-as-code.md) (IaC) tool made by HashiCorp. It lets you define cloud infrastructure (VMs, networks, storage, firewalls) in human-readable configuration files, then create and manage that infrastructure automatically by running commands.

Instead of clicking through the [Azure](../azure/azure.md) portal to create a VM, you write a `.tf` file that describes what you want, and Terraform creates it for you — reliably, every time.

## Why use it

- **Reproducible** — run `terraform apply` on any machine and get the exact same infrastructure
- **Version controlled** — `.tf` files live in Git alongside your application code
- **Destroyable** — `terraform destroy` removes all resources cleanly, with no orphaned resources left behind
- **Documented** — the configuration file is documentation of your infrastructure

## What Terraform Creates in This Project

One `terraform apply` command creates all of these in [Azure](../azure/azure.md) (Riyadh — Saudi Arabia North):

```
terraform apply
    │
    ├── 1x Resource Group          (container for all Azure resources)
    ├── 1x Virtual Network         (private network 10.0.0.0/16)
    ├── 1x Subnet                  (10.0.1.0/24 inside the VNet)
    ├── 1x Network Security Group  (firewall: 443 open, 80 open, 22 restricted to your IP)
    ├── 1x Public IP               (the IP you use to access Nextcloud in browser)
    ├── 1x Network Interface       (connects VM to the network and public IP)
    └── 1x Linux VM                (Ubuntu 22.04 LTS, Standard_B2s, Riyadh)
```

Terraform does **not** install [Docker](../../containers/docker.md), run scripts, or deploy Nextcloud. Its only job is to create the VM on [Azure](azure.md) so you can [SSH](../../protocols/ssh.md) into it and run the Bash scripts.

```
Azure (Terraform)             VM inside Azure (Bash scripts + Docker)
─────────────────             ──────────────────────────────────────
  VM                ───────►  setup.sh → installs Docker
  VNet                        deploy.sh → starts containers
  NSG                         nginx container (HTTPS)
  Public IP                   Nextcloud container
                              PostgreSQL container
```

## Development vs Production

|                       | Development (local)         | Production ([Azure](../azure/azure.md))                 |
| --------------------- | --------------------------- | ---------------------------------- |
| **Terraform needed?** | No                          | Yes                                |
| **Where it runs**     | Your Windows machine        | [Azure](../azure/azure.md) cloud, Riyadh                |
| **VM?**               | No VM — [Docker](../../containers/docker.md) Desktop only | 1 Ubuntu VM on [Azure](../azure/azure.md)               |
| **[Docker](../../containers/docker.md)**            | [Docker](../../containers/docker.md) Desktop on Windows   | [Docker](../../containers/docker.md) on the [Azure](../azure/azure.md) VM             |
| **Access**            | `https://localhost`         | `https://<azure-public-ip>`        |
| **Cost**              | Free                        | ~$30–40/month (or use free credit) |

For local testing, skip Terraform entirely — just run `docker compose up` with [Docker](../../containers/docker.md) Desktop.

## Prerequisites

### 1. Azure account

You must have an [Azure](azure.md) account. Terraform calls the [Azure](../azure/azure.md) API to create resources.

**Free options:**

| Option | Free credit | Duration |
|---|---|---|
| [Azure](../azure/azure.md) Free Account | $200 | 30 days |
| [Azure](../azure/azure.md) for Students | $100 | 12 months |

Sign up at `https://azure.microsoft.com/free`. Requires a credit card (not charged during the free tier) — the $200 credit is enough to test this project multiple times.

### 2. Azure CLI installation

Terraform uses your [Azure](../azure/azure.md) CLI login to authenticate. No [API key](../../security/auth/api-key.md) needed — it reads your session automatically.

**Option A — Direct MSI installer (recommended):** download from `https://aka.ms/installazurecliwindows`, run the `.msi` file → Next → Next → Install.

**Option B — PowerShell (run as Administrator):**
```powershell
Invoke-WebRequest -Uri https://aka.ms/installazurecliwindows -OutFile AzureCLI.msi
Start-Process msiexec.exe -ArgumentList '/I AzureCLI.msi /quiet' -Wait
Remove-Item AzureCLI.msi
```

**Verify install (close and reopen PowerShell first):**
```powershell
az --version
```

**Login to Azure:**
```powershell
az login
# Opens browser → sign in with your Azure account
# Terraform will automatically use this session — no API key needed
```

### 3. Terraform CLI installation

**Step 1 — Download:** go to `https://developer.hashicorp.com/terraform/install` and click **Windows** → **AMD64** to download the `.zip` (or use the direct link `https://releases.hashicorp.com/terraform/1.9.5/terraform_1.9.5_windows_amd64.zip`).

**Step 2 — Extract and place (PowerShell as Administrator):**
```powershell
New-Item -ItemType Directory -Force -Path "C:\terraform"
Expand-Archive -Path "$env:USERPROFILE\Downloads\terraform_1.9.5_windows_amd64.zip" -DestinationPath "C:\terraform"
```

**Step 3 — Add to PATH (PowerShell as Administrator):**
```powershell
[Environment]::SetEnvironmentVariable("PATH", $env:PATH + ";C:\terraform", "Machine")
```

**Step 4 — Close and reopen PowerShell, then verify:**
```powershell
terraform --version
# Expected: Terraform v1.9.5 on windows_amd64
```

> For Linux install steps, see [installation/linux/terraform.md](../../installation/linux/terraform.md).

## How Terraform Authenticates with Azure

No [API key](../../security/auth/api-key.md) file is required. Terraform uses the Azure CLI login session:

```
az login                    ← you login once in the terminal
      ↓
Terraform reads the session automatically via azurerm provider
      ↓
terraform apply             ← creates resources using your account
```

Behind the scenes, the `azurerm` provider in `main.tf` handles [authentication](../../security/auth/authentication.md):

```hcl
provider "azurerm" {
  features {}
}
```

This tells Terraform to use whatever Azure account is logged in via `az login`.

## How Terraform Works

```
Write .tf files
      ↓
terraform init     (download Azure provider plugin — one time)
      ↓
terraform validate (check syntax — free, no Azure needed)
      ↓
terraform plan     (preview what will be created — free, needs az login)
      ↓
terraform apply    (create real resources in Azure — uses credit)
      ↓
terraform destroy  (delete everything when done — stops billing)
```

## Testing Your Terraform Files (3 Levels)

### Level 1 — Syntax check (free, no Azure account needed)
```powershell
cd infrastructure\terraform
terraform init
terraform validate
# Success! The configuration is valid.
```

### Level 2 — Dry run / preview (needs Azure account, creates nothing, free)
```powershell
terraform plan -var="allowed_ssh_ip=YOUR_PUBLIC_IP/32"
# Shows every resource that WILL be created — nothing is deployed
# No cost
```

### Level 3 — Real deploy (uses free credit, ~$1–2/day)
```powershell
terraform apply -var="allowed_ssh_ip=YOUR_PUBLIC_IP/32"
# Creates VM in Azure Riyadh
# When done testing:
terraform destroy
# Deletes everything — billing stops
```

> To find your public IP: go to `https://whatismyip.com` and use that IP in `allowed_ssh_ip`.

## Full Workflow — From Zero to Running VM

```
1. Sign up      → azure.microsoft.com/free
2. Install CLI  → aka.ms/installazurecliwindows
3. Install TF   → releases.hashicorp.com/terraform/1.9.5/...
4. az login     → authenticate (opens browser)
5. cd infrastructure\terraform
6. terraform init
7. terraform validate
8. terraform plan     -var="allowed_ssh_ip=<your-ip>/32"
9. terraform apply    -var="allowed_ssh_ip=<your-ip>/32"
10. terraform output  → shows VM IP + SSH command + Nextcloud URL
11. ssh azureuser@<vm-ip>
12. (run Bash scripts on VM)
13. terraform destroy → when done testing
```

## Key Files in This Project

| File | Purpose |
|---|---|
| `main.tf` | All Azure resources: Resource Group, [VNet](../azure/azure-vnet.md), Subnet, [NIC](../azure/azure-network-interface.md), Public IP, VM |
| `nsg.tf` | Network Security Group rules: 443 open, 80 open, 22 restricted to your IP |
| `variables.tf` | Input variables: location, VM size, admin username, [SSH](../../protocols/ssh.md) key path |
| `outputs.tf` | Output values after apply: VM public IP, [SSH](../../protocols/ssh.md) command, Nextcloud URL |
| `terraform.tfvars.example` | Example values — copy to `terraform.tfvars` and fill in |
| `terraform.tfvars` | Your actual values — never committed to Git |
| `terraform.tfstate` | Auto-generated state file — tracks what Terraform created. Never edit manually |
| `.terraform/` | Downloaded provider plugins — auto-generated by `terraform init` |

## Basic Syntax

```hcl
resource "azurerm_resource_group" "main" {
  name     = var.resource_group_name
  location = var.location
}
```

- `resource` — declares an Azure resource to create
- `"azurerm_resource_group"` — the type of resource (from the Azure provider)
- `"main"` — a local name used to reference this resource elsewhere in the config
- `name`, `location` — configuration arguments

## Important Commands

| Command | What it does |
|---|---|
| `terraform init` | Downloads Azure provider plugin (run once) |
| `terraform validate` | Checks syntax — no Azure account needed |
| `terraform plan` | Preview of what will be created/changed/destroyed |
| `terraform apply` | Creates real resources in Azure |
| `terraform destroy` | Destroys all resources managed by this config |
| `terraform output` | Shows output values (VM IP, [SSH](../../protocols/ssh.md) command, URL) |

## Terraform State

Terraform records everything it creates in `terraform.tfstate`. This is how it knows what already exists vs what needs to be created or updated.

- In this project: state is stored **locally** (on your machine)
- In a team/production setup: state is stored in **[Azure Blob Storage](../azure/azure-blob-storage.md)** so all team members share the same state
- **Never edit `terraform.tfstate` manually**
- **Never commit `terraform.tfstate` to Git** — it is in `.gitignore`

## How it Fits in This Project

Member 4 (Networking) owns the Terraform configuration. The goal is that running `terraform apply` from a clean machine provisions the complete Azure environment in Riyadh:

```
Resource Group → VNet → Subnet → NSG → Public IP → NIC → Ubuntu VM
```

After `terraform apply` completes, it outputs the VM's public IP. Member 1/3 then SSHs into the VM and runs the Bash scripts to deploy Nextcloud. See [Virtual Machines](../infrastructure/virtual-machines.md) and [Azure Networking: VNet & NSG](../azure/networking-vnet-nsg.md) for the resources being provisioned.

## Official Resources

| Resource | Link |
|---|---|
| Website | https://www.terraform.io |
| Download | https://developer.hashicorp.com/terraform/install |
| Azure Provider Docs | https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs |
| Azure CLI Install | https://aka.ms/installazurecliwindows |
| Azure Free Account | https://azure.microsoft.com/free |

## Related

- [Infrastructure as Code](infrastructure-as-code.md)
- [Microsoft Azure](azure.md)
- [Virtual Machines](../infrastructure/virtual-machines.md)
- [Azure Networking: VNet & NSG](../azure/networking-vnet-nsg.md)
- [Nextcloud RAG Case Study](../../../guides/cloud/nextcloud-rag-case-study/nextcloud.md)
- [Ansible](ansible.md) — configuration management for hosts Terraform provisions
- [Terraform Commands](../../commands/terraform.md)
