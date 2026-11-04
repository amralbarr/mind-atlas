# Nextcloud RAG Case Study

## Internal File Sharing and Collaboration Platform Based on Nextcloud with AI-Powered Document Retrieval Using RAG

This is a case study of a student engineering project: an internal file-sharing platform built on top of Nextcloud, extended with an AI layer that lets users ask natural-language questions over their organization's documents using [Retrieval-Augmented Generation](../../../concepts/ai/rag/rag.md) (RAG).

The project combines four areas of work:
- **Cloud infrastructure** — provisioning the hosting environment on [Microsoft Azure](../../../concepts/cloud/azure/azure.md)
- **Platform & deployment** — running Nextcloud and its supporting services in containers on Ubuntu
- **Security** — access control and identity management so the AI layer never leaks documents a user isn't permitted to see
- **AI / [RAG](../../../concepts/ai/rag/rag.md)** — indexing documents and answering questions grounded in the retrieved, permission-filtered content

This page is the entry point and table of contents for the case study. Each linked page explains what the technology or concept is, why it was used, how it works, and how it fit into this specific project.

---

## Index

### Infrastructure & Cloud

| Topic | What it covers |
|---|---|
| [Microsoft Azure](../../../concepts/cloud/azure/azure.md) | Cloud platform, [Azure](../../../concepts/cloud/azure/azure.md) resources (VM, [VNet](../../../concepts/cloud/azure/azure-vnet.md), [NSG](../../../concepts/cloud/azure/azure-nsg.md), Resource Group) |
| [Terraform](../../../concepts/cloud/iac/terraform.md) | [Infrastructure as Code](../../../concepts/cloud/iac/infrastructure-as-code.md) — defining and provisioning [Azure](../../../concepts/cloud/azure/azure.md) resources automatically |
| [Networking: VNet & NSG](../../../concepts/cloud/azure/networking-vnet-nsg.md) | Virtual networks, subnets, firewalls ([NSG](../../../concepts/cloud/azure/azure-nsg.md)), port exposure, [SSH](../../../concepts/protocols/ssh.md) security |
| [Azure RBAC](../../../concepts/cloud/azure/azure-rbac.md) | Identity-based control-plane access — who can manage resources, and how it differs from [NSG](../../../concepts/cloud/azure/azure-nsg.md)'s network-layer filtering |
| [Microsoft Entra ID](../../../concepts/cloud/azure/microsoft-entra-id.md) | The identity provider backing [Azure RBAC](../../../concepts/cloud/azure/azure-rbac.md) role assignments and team group management |
| [Azure secure remote access options](../../../overviews/cloud/azure-secure-remote-access-options.md) | Comparison of Bastion, JIT VM access, and VPN Gateway P2S for reaching a VM without a static IP allowlist |

### Platform & Deployment

| Topic | What it covers |
|---|---|
| [Ubuntu Server Setup](../../linux/ubuntu-server-setup.md) | Server OS, [SSH](../../../concepts/protocols/ssh.md), file permissions, UFW firewall, package management |
| [Docker](../../../concepts/containers/docker.md) | Containerization — images, containers, volumes, networks |
| [Docker Compose](../../../concepts/containers/docker-compose.md) | Multi-container orchestration — [docker](../../../concepts/containers/docker.md)-compose.yml, persistent volumes, `down` vs `down -v` |
| [Docker Daemon (Docker Engine)](../../../concepts/containers/docker-daemon.md) | How `dockerd` works, and why it running as root by default is the main security trade-off |
| [Container Isolation](../../../concepts/containers/container-isolation.md) | The Linux namespaces/cgroups mechanism that actually isolates a container |
| [OCI (Open Container Initiative)](../../../concepts/containers/oci.md) | The standard image/runtime spec that makes containers portable across engines |
| [Podman](../../../concepts/containers/podman.md) | Rootless, daemonless, [OCI](../../../concepts/containers/oci.md)-compatible alternative to [Docker](../../../concepts/containers/docker.md) — why it wasn't chosen here |
| [LXC / LXD](../../../concepts/containers/lxc-lxd.md) | System containers vs [Docker](../../../concepts/containers/docker.md)'s application containers — a different category of tool |
| [Bash Scripting for Server Automation](../../linux/bash-scripting.md) | Shell scripting for automation — setup.sh, deploy.sh, health-check.sh, backup.sh |
| [Backup and Restore](../../../concepts/cloud/infrastructure/backup-and-restore.md) | Data backup strategy, why a [Docker](../../../concepts/containers/docker.md) image ≠ a backup, restore procedure |

### Application

| Topic | What it covers |
|---|---|
| [Nextcloud](nextcloud.md) | The file-sharing platform — users, groups, permissions, [WebDAV](../../../concepts/protocols/webdav.md) API, Activity app |
| [WebDAV API](webdav-api.md) | How the AI pipeline connects to Nextcloud to read and index documents |

### Security

| Topic | What it covers |
|---|---|
| [Access Control & IAM](../../../concepts/security/authorization/access-control-iam.md) | [RBAC](../../../concepts/security/authorization/rbac.md), permission matrix, [authentication](../../../concepts/security/auth/authentication.md), least privilege, audit logging |
| [Azure Bastion](../../../concepts/cloud/remote-access/azure-bastion.md) | Browser-based [SSH](../../../concepts/protocols/ssh.md)/RDP via the Portal, no public IP or open [NSG](../../../concepts/cloud/azure/azure-nsg.md) port on the VM needed |
| [Azure Just-in-Time VM Access](../../../concepts/cloud/remote-access/azure-jit-vm-access.md) | Temporary, auto-expiring [NSG](../../../concepts/cloud/azure/azure-nsg.md) port openings via Microsoft Defender for Cloud |
| [Azure VPN Gateway (Point-to-Site)](../../../concepts/cloud/remote-access/azure-vpn-gateway-point-to-site.md) | Client VPN into the [VNet](../../../concepts/cloud/azure/azure-vnet.md) for private-IP access to VM resources |

### AI / RAG Layer

| Topic | What it covers |
|---|---|
| [Document Indexing](../../../concepts/ai/ingestion/document-indexing.md) | The full indexing pipeline: extraction → chunking → [embeddings](../../../concepts/ai/ingestion/embeddings.md) → vector store |
| [Embeddings](../../../concepts/ai/ingestion/embeddings.md) | What [embeddings](../../../concepts/ai/ingestion/embeddings.md) are, how they enable semantic search, embedding models |
| [Vector Database](../../../concepts/ai/retrieval/vector-database.md) | Vector stores ([ChromaDB](../../../concepts/ai/retrieval/vector-stores/chromadb.md), [FAISS](../../../concepts/ai/retrieval/vector-stores/faiss.md), [Qdrant](../../../concepts/ai/retrieval/vector-stores/qdrant.md)) — how similarity search works |
| [RAG (Retrieval-Augmented Generation)](../../../concepts/ai/rag/rag.md) | The full [RAG](../../../concepts/ai/rag/rag.md) pipeline — retrieval, permission filtering, [LLM](../../../concepts/ai/generation/llm.md) generation |
| [LLM (Large Language Model)](../../../concepts/ai/generation/llm.md) | What [LLMs](../../../concepts/ai/generation/llm.md) are, hallucination, prompt templates, model options (GPT-4o, Ollama) |

---

## Reading Order (by team role)

A suggested reading path for each of the four contributor roles on this project.

### Computer Science

1. [Nextcloud](nextcloud.md)
2. [WebDAV API](webdav-api.md)
3. [Document Indexing](../../../concepts/ai/ingestion/document-indexing.md)
4. [Embeddings](../../../concepts/ai/ingestion/embeddings.md)
5. [Vector Database](../../../concepts/ai/retrieval/vector-database.md)
6. [RAG (Retrieval-Augmented Generation)](../../../concepts/ai/rag/rag.md)
7. [LLM (Large Language Model)](../../../concepts/ai/generation/llm.md)
8. [Access Control & IAM](../../../concepts/security/authorization/access-control-iam.md) — for permission-aware retrieval

### Cybersecurity

1. [Access Control & IAM](../../../concepts/security/authorization/access-control-iam.md)
2. [Nextcloud](nextcloud.md)
3. [Networking: VNet & NSG](../../../concepts/cloud/azure/networking-vnet-nsg.md)
4. [Azure RBAC](../../../concepts/cloud/azure/azure-rbac.md) — and how it differs from [NSG](../../../concepts/cloud/azure/azure-nsg.md)
5. [Azure secure remote access options](../../../overviews/cloud/azure-secure-remote-access-options.md) — Bastion, JIT, VPN Gateway P2S
6. [Docker](../../../concepts/containers/docker.md)
7. [Backup and Restore](../../../concepts/cloud/infrastructure/backup-and-restore.md)
8. [RAG (Retrieval-Augmented Generation)](../../../concepts/ai/rag/rag.md) — security implications section

### IT

1. [Ubuntu Server Setup](../../linux/ubuntu-server-setup.md)
2. [Docker](../../../concepts/containers/docker.md)
3. [Docker Compose](../../../concepts/containers/docker-compose.md)
4. [Nextcloud](nextcloud.md)
5. [Bash Scripting for Server Automation](../../linux/bash-scripting.md)
6. [Backup and Restore](../../../concepts/cloud/infrastructure/backup-and-restore.md)

### Computer Engineering / Networking

1. [Microsoft Azure](../../../concepts/cloud/azure/azure.md)
2. [Terraform](../../../concepts/cloud/iac/terraform.md)
3. [Networking: VNet & NSG](../../../concepts/cloud/azure/networking-vnet-nsg.md)
4. [Azure Bastion](../../../concepts/cloud/remote-access/azure-bastion.md)
5. [Ubuntu Server Setup](../../linux/ubuntu-server-setup.md)
6. [Docker](../../../concepts/containers/docker.md)
7. [LLM (Large Language Model)](../../../concepts/ai/generation/llm.md) — AI service deployment
