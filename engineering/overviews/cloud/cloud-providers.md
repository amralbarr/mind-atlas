# Cloud Providers

## What is Cloud Computing?

Cloud computing means renting computing resources — servers, storage, networking, databases — from a company that owns massive data centers around the world. Instead of buying physical hardware, you pay for what you use, when you use it.

```
Traditional (On-Premises)          Cloud
──────────────────────────         ──────────────────────────
Buy a physical server         →    Rent a virtual server
Pay upfront (thousands $)     →    Pay monthly / per hour
You manage the hardware       →    Provider manages hardware
Fixed capacity                →    Scale up or down instantly
One location                  →    Data centers worldwide
```

## Cloud Service Models

Before comparing providers, understand what they offer:

| Model | What you get | You manage | Provider manages | Example |
|---|---|---|---|---|
| **IaaS** — Infrastructure as a Service | [Virtual machines](../../concepts/cloud/infrastructure/virtual-machines.md), storage, networking | OS, apps, security | Physical hardware | [Azure](../../concepts/cloud/azure/azure.md) VM, [AWS](../../concepts/cloud/infrastructure/aws.md) EC2 |
| **PaaS** — Platform as a Service | Runtime environment, database, web server | Your app and data | OS, runtime, infrastructure | [Azure](../../concepts/cloud/azure/azure.md) App Service, Heroku |
| **SaaS** — Software as a Service | Ready-to-use application | Your data and settings | Everything else | Gmail, Dropbox, Microsoft 365 |
| **Shared Hosting** | Space on a shared server | Your website files | Server, OS, everything | Hostinger, Namecheap |

## Category 1 — Hyperscale Cloud Platforms (IaaS / PaaS / SaaS)

Full-featured enterprise cloud platforms with hundreds of services. Used for complex, scalable infrastructure.

### Microsoft Azure

- **What:** Microsoft's cloud platform — the one used in this project (see [Microsoft Azure](../../concepts/cloud/azure/azure.md) for the project-specific details)
- **Strengths:** Deep integration with Microsoft products (Windows, Active Directory, Office 365), strong enterprise and compliance features
- **Used for in this project:** VM, [VNet](../../concepts/cloud/azure/azure-vnet.md), [NSG](../../concepts/cloud/azure/azure-nsg.md), Storage Account ([Terraform](../../concepts/cloud/iac/terraform.md) remote state)
- **Pricing model:** Pay-as-you-go (per hour / per GB)
- **Free tier:** 12 months free services + $200 credit for new accounts
- **Best for:** Enterprise, Microsoft-stack teams, students with [Azure](../../concepts/cloud/azure/azure.md) for Students credit
- **Website:** https://azure.microsoft.com

### Amazon Web Services (AWS)

The largest cloud provider by market share — widest range of services, largest community, most tutorials available. See [AWS](../../concepts/cloud/infrastructure/aws.md) for core services, IAM basics, and CLI usage.

- **Free tier:** 12 months free tier (EC2 t2.micro, S3, RDS)
- **Best for:** Startups, general-purpose workloads, anyone starting cloud learning
- **Website:** https://aws.amazon.com

### Google Cloud Platform (GCP)

Best-in-class AI/ML services (Vertex AI, BigQuery) and strong [Kubernetes](../../concepts/distributed-systems/kubernetes/ingress.md) (GKE). See [GCP](../../concepts/cloud/infrastructure/gcp.md) for core services and CLI usage.

- **Free tier:** $300 credit for 90 days + always-free tier
- **Best for:** AI/ML workloads, data analytics, [Kubernetes](../../concepts/distributed-systems/kubernetes/ingress.md)-heavy projects
- **Website:** https://cloud.google.com

### Comparison — Hyperscale Platforms

|                | [Azure](../../concepts/cloud/azure/azure.md)                  | [AWS](../../concepts/cloud/infrastructure/aws.md)             | [GCP](../../concepts/cloud/infrastructure/gcp.md)                  |
| -------------- | ---------------------- | --------------- | -------------------- |
| Market share   | 2nd                    | 1st             | 3rd                  |
| VM product     | [Virtual Machines](../../concepts/cloud/infrastructure/virtual-machines.md)       | EC2             | Compute Engine       |
| Storage        | Blob Storage           | S3              | Cloud Storage        |
| Database       | [Azure](../../concepts/cloud/azure/azure.md) [SQL](../../concepts/databases/relational/sql.md) / Cosmos DB  | RDS / DynamoDB  | Cloud [SQL](../../concepts/databases/relational/sql.md) / Bigtable |
| [Kubernetes](../../concepts/distributed-systems/kubernetes/ingress.md)     | AKS                    | EKS             | GKE                  |
| AI / ML        | [Azure](../../concepts/cloud/azure/azure.md) AI               | SageMaker       | Vertex AI            |
| Best known for | Enterprise / Microsoft | General purpose | AI / Big Data        |

## Category 2 — VPS Providers (Virtual Private Server)

A VPS gives you a single virtual machine with root access. Simpler than hyperscale clouds — fewer services but cheaper and easier to manage. Good for hosting websites, apps, and self-hosted tools like Nextcloud.

### DigitalOcean

- **What:** Developer-friendly VPS provider — known for simplicity and clean UI
- **Product name:** Droplets (VMs)
- **Pricing:** Starts at $4/month for a basic VM
- **Strengths:** Very easy to use, great documentation, predictable flat-rate pricing
- **Best for:** Developers hosting web apps, APIs, self-hosted tools
- **Website:** https://www.digitalocean.com

### Linode (now Akamai Cloud)

- **What:** Long-running VPS provider, now part of Akamai
- **Pricing:** Starts at $5/month
- **Strengths:** Reliable, good performance, straightforward pricing
- **Best for:** Similar use cases to DigitalOcean
- **Website:** https://www.linode.com

### Vultr

- **What:** VPS provider with global data centers
- **Pricing:** Starts at $2.50/month
- **Strengths:** Cheapest entry price, many locations, bare metal options
- **Best for:** Budget hosting, gaming servers, lightweight apps
- **Website:** https://www.vultr.com

### Hetzner

- **What:** German VPS and dedicated server provider
- **Pricing:** Starts at €3.29/month — extremely cost-effective
- **Strengths:** Best price-to-performance ratio in Europe, eco-friendly data centers
- **Best for:** European teams, cost-sensitive projects, high-traffic apps on a budget
- **Website:** https://www.hetzner.com

### Comparison — VPS Providers

| | DigitalOcean | Linode | Vultr | Hetzner |
|---|---|---|---|---|
| Starting price | $4/month | $5/month | $2.50/month | €3.29/month |
| Ease of use | Excellent | Good | Good | Good |
| Locations | 15+ | 11+ | 32+ | 5 (EU focus) |
| Best for | Simplicity | Reliability | Cheapest | Best value EU |

## Category 3 — Shared Hosting & Domain Providers

Shared hosting puts your website on a server shared with hundreds of other customers. You do not get root access or the ability to run [Docker](../../concepts/containers/docker.md). Good for simple websites, WordPress blogs, or static sites — not suitable for running Nextcloud or [Docker](../../concepts/containers/docker.md)-based projects.

### Hostinger

- **What:** Popular budget web hosting provider
- **Products:** Shared hosting, WordPress hosting, VPS hosting, domain registration
- **Pricing:** Shared hosting from ~$3/month; VPS from ~$5/month
- **Strengths:** Very cheap, beginner-friendly control panel (hPanel), 24/7 support
- **Limitations (shared hosting):** No root access, no [Docker](../../concepts/containers/docker.md), limited to PHP/[MySQL](../../concepts/databases/relational/mysql.md) websites
- **Note:** Their **VPS plans** do give root access and can run [Docker](../../concepts/containers/docker.md) — similar to DigitalOcean
- **Best for:** Simple websites, WordPress, small businesses on a tight budget
- **Website:** https://www.hostinger.com

### Namecheap

- **What:** Primarily a **domain registrar** — the place you buy domain names (e.g., `yourproject.com`)
- **Products:** Domain registration, shared hosting, SSL certificates, VPN
- **Pricing:** Domains from $1–15/year; shared hosting from ~$2/month
- **Strengths:** Very cheap domains, clean interface, free WhoisGuard privacy protection
- **Limitations:** Hosting is basic shared hosting — not suitable for [Docker](../../concepts/containers/docker.md) projects
- **Best for:** Buying a domain name — this is what Namecheap is really used for
- **Website:** https://www.namecheap.com

### GoDaddy

- **What:** Large domain registrar and hosting provider
- **Products:** Domain registration, shared hosting, VPS, website builder
- **Pricing:** Domains from ~$12/year; hosting varies
- **Strengths:** Very well known, large support team
- **Limitations:** Aggressive upselling, hosting performance is average
- **Best for:** Domain registration (though Namecheap is often cheaper)
- **Website:** https://www.godaddy.com

## Category 4 — Platform as a Service (PaaS) / App Hosting

These platforms hide all server management — you push your code and they handle deployment, scaling, and infrastructure automatically.

### Heroku

- **What:** One of the original PaaS platforms — deploy apps with `git push`
- **Pricing:** Free tier removed in 2022; starts at $5/month
- **Strengths:** Extremely simple deployment, no server management needed
- **Best for:** Web apps, APIs, prototypes — when you don't want to manage a server
- **Website:** https://www.heroku.com

### Railway

- **What:** Modern Heroku alternative — deploy from GitHub in minutes
- **Pricing:** $5/month usage-based
- **Strengths:** Very fast setup, supports [Docker](../../concepts/containers/docker.md), databases included
- **Best for:** Quick deployments, side projects, student projects
- **Website:** https://railway.app

### Render

- **What:** Another modern PaaS — web services, databases, static sites
- **Pricing:** Free tier available; paid from $7/month
- **Strengths:** Free tier, automatic deploys from GitHub, managed [PostgreSQL](../../concepts/databases/relational/postgresql.md)
- **Best for:** Web apps and APIs with minimal ops overhead
- **Website:** https://render.com

### Vercel / Netlify

- **What:** Specialized platforms for frontend and static site hosting
- **Pricing:** Generous free tiers
- **Strengths:** Instant deployments from GitHub, global [CDN](../../concepts/networking/cdn.md), great for React/Next.js
- **Limitations:** Frontend only — not for running [Docker](../../concepts/containers/docker.md) or backend servers
- **Best for:** Frontend apps, documentation sites, landing pages
- **Websites:** https://vercel.com / https://www.netlify.com

## Which Provider for Which Use Case?

| Use case | Recommended provider |
|---|---|
| This project ([Azure](../../concepts/cloud/azure/azure.md) VM + [Terraform](../../concepts/cloud/iac/terraform.md)) | **[Microsoft Azure](../../concepts/cloud/azure/azure.md)** |
| Simple self-hosted app (Nextcloud, etc.) | **DigitalOcean** or **Hetzner** |
| Best price for a VPS | **Hetzner** (EU) or **Vultr** |
| Learning cloud for the first time | **[AWS](../../concepts/cloud/infrastructure/aws.md)** (most tutorials) or **Azure** (free student credit) |
| Just need a domain name | **Namecheap** |
| Simple WordPress website | **Hostinger** |
| Deploy a web app without managing servers | **Railway** or **Render** |
| Frontend / React app | **Vercel** or **Netlify** |

## Key Terms

| Term | Meaning |
|---|---|
| **Region** | A geographic location where the provider has data centers (e.g., East US, West Europe) |
| **Availability Zone** | A separate data center within a region — used for redundancy |
| **Instance / Droplet / VM** | Different names for a virtual machine depending on the provider |
| **Bandwidth / Egress** | Data transferred out of the cloud — often charged per GB |
| **Root access** | Full admin control over the server OS — available on VPS and IaaS, not shared hosting |
| **[CDN](../../concepts/networking/cdn.md)** | [Content Delivery Network](../../concepts/networking/cdn.md) — serves files from the location closest to the user |
| **Load balancer** | Distributes incoming traffic across multiple servers |
| **Managed service** | The provider handles updates, backups, and scaling (e.g., managed [PostgreSQL](../../concepts/databases/relational/postgresql.md)) |

## Related

- [Microsoft Azure](../../concepts/cloud/azure/azure.md)
- [AWS](../../concepts/cloud/infrastructure/aws.md)
- [GCP](../../concepts/cloud/infrastructure/gcp.md)
- [Terraform](../../concepts/cloud/iac/terraform.md)
- [Virtual Machines](../../concepts/cloud/infrastructure/virtual-machines.md)
- [Azure Networking: VNet & NSG](../../concepts/cloud/azure/networking-vnet-nsg.md)
- [Backup and Restore](../../concepts/cloud/infrastructure/backup-and-restore.md)
- [Object Storage](../../concepts/cloud/infrastructure/object-storage.md)
- [Docker](../../concepts/containers/docker.md)
