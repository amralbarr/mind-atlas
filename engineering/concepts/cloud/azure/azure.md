# Microsoft Azure

## What is it?

Microsoft Azure is a public cloud computing platform that provides on-demand infrastructure — [virtual machines](../infrastructure/virtual-machines.md), networking, storage, databases, and more — billed by usage. It is one of the three major [cloud providers](../../../overviews/cloud/cloud-providers.md) alongside [AWS](../infrastructure/aws.md) and Google Cloud.

## Why Azure for this project

Azure is the deployment target chosen for this project. It provides the virtual machine that hosts Ubuntu, [Docker](../../containers/docker.md), and the Nextcloud stack. Azure manages the physical hardware; the team manages the software on top. The VM is deployed in **Saudi Arabia North (Riyadh)**.

## Key Azure Resources Used in This Project

| Resource | What it does |
|---|---|
| **Resource Group** | A logical container that holds all Azure resources. Makes management and deletion easy. |
| **Virtual Network ([VNet](azure-vnet.md))** | A private network in Azure. All containers and services communicate over this network. |
| **Subnet** | A subdivision of the [VNet](azure-vnet.md). The VM is placed inside the subnet. |
| **Network Security Group ([NSG](azure-nsg.md))** | A firewall attached to the VM. Controls which ports are open to the Internet. |
| **Virtual Machine (VM)** | A cloud server running Ubuntu 22.04 LTS. This is where [Docker](../../containers/docker.md) and Nextcloud run. |
| **Public IP Address** | The Internet-facing IP assigned to the VM. Users access Nextcloud through this IP via [HTTPS](../../networking/https.md). |
| **Disk / Storage** | The VM's OS disk (64 GB) for persistent storage of files and database. |

## Creating an Azure Account

### Email requirements

| Email type | Works? | Notes |
|---|---|---|
| Microsoft / Outlook email | Yes, always | Best option — go to outlook.com to create one |
| Work email (Microsoft tenant) | Yes | May be tied to a company Azure tenant |
| University / student email | Yes | Use Azure for Students — no credit card needed |
| Gmail (new account) | Often blocked | Azure blocks new Gmail accounts as fraud prevention |
| Gmail (old/established) | Sometimes | Not reliable |

**Recommended:** create a free Outlook email at `https://outlook.com` if you don't have one, then use it for Azure signup.

### Free account options

| Option | Free credit | Duration | Credit card? |
|---|---|---|---|
| **Azure Free Account** | $200 | 30 days | Required (not charged) |
| **Azure for Students** | $100 | 12 months | Not required |

- Sign up (free account): `https://azure.microsoft.com/free`
- Sign up (students): `https://azure.microsoft.com/free/students`

### Registration steps

1. Go to `https://azure.microsoft.com/free`
2. Click **Start free**
3. Sign in with your Microsoft/Outlook/work email
4. Fill in your details and verify phone number
5. Enter credit card (not charged — used for identity verification only)
6. You get $200 free credit valid for 30 days
7. After signup you land on the Azure Portal at `https://portal.azure.com`

## Azure CLI — installation and login

The Azure CLI (`az`) is a command-line tool that lets you manage Azure from your terminal. [Terraform](../iac/terraform.md) uses your CLI login session to authenticate — **no [API key](../../security/auth/api-key.md) or secret file needed**.

### Install on Windows

**Option A — MSI installer (recommended):**
1. Download: `https://aka.ms/installazurecliwindows`
2. Run the `.msi` file → Next → Next → Install
3. Close and reopen PowerShell

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

### Login to Azure

```powershell
az login
# Opens browser → sign in with your Azure account
# Returns to terminal with your subscription details
```

After login, [Terraform](../iac/terraform.md) can use your session automatically — no extra config needed.

### Useful Azure CLI commands

| Command | What it does |
|---|---|
| `az login` | Login to your Azure account (opens browser) |
| `az logout` | Logout |
| `az account show` | Show current logged-in account and subscription |
| `az account list` | List all subscriptions available to your account |
| `az group list` | List all resource groups |
| `az vm list` | List all [virtual machines](../infrastructure/virtual-machines.md) |
| `az vm start --name <vm> --resource-group <rg>` | Start a stopped VM |
| `az vm stop --name <vm> --resource-group <rg>` | Stop a running VM (saves cost) |
| `az vm deallocate --name <vm> --resource-group <rg>` | Stop + deallocate VM (stops all billing) |

## How Terraform authenticates with Azure

No [API key](../../security/auth/api-key.md) or credentials file is required for this project. [Terraform](../iac/terraform.md) reads your `az login` session automatically:

```
az login                          ← login once in terminal
        ↓
Terraform reads the session       ← via azurerm provider
        ↓
terraform apply                   ← creates resources using your account
```

The `provider` block in `main.tf` handles this:

```hcl
provider "azurerm" {
  features {}
}
```

This tells [Terraform](../iac/terraform.md) to use whatever Azure account is currently logged in via `az login`. See [Terraform](terraform.md) for the full [IaC](../iac/infrastructure-as-code.md) workflow.

## Azure Portal

The Azure Portal is the web UI to view and manage your Azure resources.

- URL: `https://portal.azure.com`
- Login with the same account you used for `az login`
- Use it to monitor resources, check VM status, view billing
- Do **not** use it to create resources manually — use [Terraform](../iac/terraform.md) instead so everything stays version-controlled

## Important Concepts

**Region**
The geographic location of the datacenter where resources are deployed. This project uses **Saudi Arabia North** (Riyadh datacenter). Backup option: **Saudi Arabia West** (Jeddah datacenter).

**[NSG](azure-nsg.md) rules (firewall)**
Inbound security rules control what traffic reaches the VM:
- Port 443 ([HTTPS](../../networking/https.md)) — open to everyone → Nextcloud access
- Port 80 ([HTTP](../../networking/http.md)) — open to everyone → redirects to [HTTPS](../../networking/https.md)
- Port 22 ([SSH](../../protocols/ssh.md)) — restricted to your IP address only → administration
- All other ports — denied by default

See [Azure Networking: VNet & NSG](networking-vnet-nsg.md) for the full rule set.

**[SSH](../../protocols/ssh.md) key [authentication](../../security/auth/authentication.md)**
Azure VMs use [SSH](../../protocols/ssh.md) key pairs for secure access. Password login is disabled. Your public key (`~/.ssh/id_rsa.pub`) is uploaded to the VM via [Terraform](../iac/terraform.md). You connect with your private key.

**Pay-as-you-go**
You only pay for what you use. The VM (`Standard_B2s` in Riyadh) costs approximately $30–40/month running 24/7.
- Stop the VM when not using it to save cost — [Docker](../../containers/docker.md) volumes persist
- Run `terraform destroy` to delete everything and stop all billing
- Use free credit ($200) to test without any actual charges

## Development vs Production

| | Development (local) | Production (Azure) |
|---|---|---|
| **Azure account needed?** | No | Yes |
| **[Terraform](../iac/terraform.md) needed?** | No | Yes |
| **VM?** | No — [Docker](../../containers/docker.md) Desktop only | Yes — 1 Ubuntu VM in Riyadh |
| **Access URL** | `https://localhost` | `https://<azure-public-ip>` |
| **Cost** | Free | ~$30–40/month (or use free credit) |

For local testing, skip Azure entirely — run `docker compose up` with [Docker](../../containers/docker.md) Desktop on your Windows machine.

## How it Fits in This Project

Azure is provisioned entirely through **[Terraform](../iac/terraform.md)**. The team does not manually create resources through the Azure portal — everything is defined in `.tf` files and applied with `terraform apply`. This makes the environment reproducible and version-controlled.

```
Terraform (local machine)
        ↓  terraform apply
Azure Riyadh (Saudi Arabia North)
        └── Resource Group
            └── VNet → Subnet → NSG
                └── VM (Ubuntu 22.04)
                    └── Docker Compose
                        ├── nginx (HTTPS)
                        ├── Nextcloud
                        └── PostgreSQL
```

## Azure vs On-Premises

| | Azure | On-Premises |
|---|---|---|
| Hardware | Managed by Microsoft | Managed by the team |
| Setup time | Minutes ([Terraform](../iac/terraform.md)) | Days/weeks |
| Cost model | Pay per use | Capital expense |
| Scalability | Instant | Requires hardware purchase |
| Geographic reach | Global | Local |

## Official Resources

| Resource | Link |
|---|---|
| Azure Portal | https://portal.azure.com |
| Free Account Signup | https://azure.microsoft.com/free |
| Azure for Students | https://azure.microsoft.com/free/students |
| Azure CLI Install (Windows) | https://aka.ms/installazurecliwindows |
| Azure CLI Documentation | https://learn.microsoft.com/en-us/cli/azure |
| Azure VM Pricing | https://azure.microsoft.com/en-us/pricing/details/virtual-machines/linux |
| Azure Regions | https://azure.microsoft.com/en-us/explore/global-infrastructure/geographies |

## Related

- [Cloud Providers](../../../overviews/cloud/cloud-providers.md)
- [Terraform](terraform.md)
- [Virtual Machines](../infrastructure/virtual-machines.md)
- [Azure Networking: VNet & NSG](networking-vnet-nsg.md)
- [Azure RBAC](azure-rbac.md)
- [Microsoft Entra ID](microsoft-entra-id.md)
- [Azure AI Foundry](azure-ai-foundry.md) — unified AI platform for building and deploying AI applications on Azure
- [Azure AI services](azure-ai-services.md) — the family of pre-built AI APIs (Language, Vision, Speech, Document Intelligence, Content Safety, etc.), consumable standalone or through [Azure AI Foundry](azure-ai-foundry.md)
- [Azure AI Search](azure-ai-search.md) — managed [hybrid search](../../ai/retrieval/hybrid-search.md) and semantic ranking service, the standard [RAG](../../ai/rag/rag.md) retrieval layer on Azure
- [Azure secure remote access options](../../../overviews/cloud/azure-secure-remote-access-options.md)
- [Access Control & IAM](../../security/authorization/access-control-iam.md)
- [Nextcloud RAG Case Study](../../../guides/cloud/nextcloud-rag-case-study/nextcloud.md)
