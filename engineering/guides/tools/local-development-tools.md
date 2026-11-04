# Local Development Tools

*Reference setup for the Nextcloud-based internal file-sharing platform with AI-powered document retrieval ([RAG](../../concepts/ai/rag/rag.md)).*

This file is the index of all local development tools needed for this project. Each tool has its own dedicated installation guide — see the links below.

## Quick Install Summary by Scope

| Tool | All | AI / [RAG](../../concepts/ai/rag/rag.md) | Security | Deployment | Infrastructure |
|---|---|---|---|---|---|
| VS Code | ✅ | ✅ | ✅ | ✅ | ✅ |
| Git + GitHub | ✅ | ✅ | ✅ | ✅ | ✅ |
| [Docker](../../concepts/containers/docker.md) Desktop | ✅ | ✅ | ✅ | ✅ | ✅ |
| WSL2 (Windows only) | ✅ | ✅ | ✅ | ✅ | ✅ |
| draw.io | ✅ | ✅ | ✅ | ✅ | ✅ |
| Python 3.11+ | — | ✅ | — | — | — |
| Postman | — | ✅ | ✅ | — | — |
| [SSH](../../concepts/protocols/ssh.md) Client | — | — | ✅ | ✅ | ✅ |
| [Terraform](../../concepts/cloud/iac/terraform.md) CLI | — | — | — | — | ✅ |
| [Azure](../../concepts/cloud/azure/azure.md) CLI | — | — | — | — | ✅ |

## Tool Installation Guides

| Tool | File | Scope |
|---|---|---|
| VS Code | [vscode.md](vscode.md) | All |
| Git + GitHub | [git-github-basics.md](../git/git-github-basics.md) | All |
| [Docker](../../concepts/containers/docker.md) Desktop | [docker-desktop.md](../../installation/macos/docker.md) | All |
| WSL2 | [../../installation/windows/wsl2.md](../../installation/windows/wsl2.md) | All (Windows) |
| draw.io | [drawio.md](drawio.md) | All |
| Python 3.11+ | [../../installation/linux/python.md](../../installation/linux/python.md) | AI / [RAG](../../concepts/ai/rag/rag.md) |
| Postman | [postman.md](postman.md) | AI / [RAG](../../concepts/ai/rag/rag.md), Security |
| [SSH](../../concepts/protocols/ssh.md) Client | [ssh-client.md](ssh-client.md) | Security, Deployment, Infrastructure |
| [Terraform](../../concepts/cloud/iac/terraform.md) CLI | [../../installation/linux/terraform.md](../../installation/linux/terraform.md) | Infrastructure |
| [Azure](../../concepts/cloud/azure/azure.md) CLI | [../../commands/azure.md](../../commands/azure.md) | Infrastructure |
| Optional Tools | [optional-tools.md](optional-tools.md) | All (by preference) |

## `.gitignore` — What Must Never Be Committed

Add this to the root of the repository:

```gitignore
# Secrets
.env
*.env
*.bak

# Terraform state files
*.tfstate
*.tfstate.backup
.terraform/
.terraform.lock.hcl

# Python
__pycache__/
*.pyc
*.pyo
.venv/
venv/
*.egg-info/
dist/
build/

# Vector store data (too large for Git)
ai/embeddings/chroma_db/
ai/embeddings/faiss_index/
*.index

# OS-generated files
.DS_Store
Thumbs.db
desktop.ini

# SSH keys (should never appear here)
*.pem
*.key
id_rsa
id_ed25519
```

## Environment Variables (`.env` file)

The `.env` file holds all secrets. It is **never committed to Git**.
Each contributor creates their own from the shared template:

```bash
cp deployment/.env.example deployment/.env
# Edit .env with your actual values
```

**`deployment/.env.example`** (safe to commit — placeholders only):

```env
# PostgreSQL Database
POSTGRES_DB=nextcloud
POSTGRES_USER=nextcloud_user
POSTGRES_PASSWORD=CHANGE_ME_STRONG_PASSWORD

# Nextcloud Admin
NEXTCLOUD_ADMIN_USER=admin
NEXTCLOUD_ADMIN_PASSWORD=CHANGE_ME_STRONG_PASSWORD
NEXTCLOUD_TRUSTED_DOMAINS=localhost <your-vm-ip>

# AI / LLM
OPENAI_API_KEY=CHANGE_ME_OR_LEAVE_BLANK_IF_USING_OLLAMA
OLLAMA_BASE_URL=http://ai:11434

# Nextcloud API access (for indexing pipeline)
NEXTCLOUD_URL=https://localhost
NEXTCLOUD_API_USER=admin
NEXTCLOUD_API_PASSWORD=CHANGE_ME
```

## First-Day Setup Checklist

Complete everything in your scope before Day 1.

### All Scopes
- [ ] VS Code installed with extensions relevant to your scope
- [ ] Git installed and configured (`user.name` and `user.email`)
- [ ] GitHub account created and added to the project repository
- [ ] [Docker](../../concepts/containers/docker.md) Desktop installed — `docker run hello-world` passes
- [ ] WSL2 installed with Ubuntu 22.04 (Windows only)
- [ ] draw.io available (web or desktop app)
- [ ] [SSH](../../concepts/protocols/ssh.md) key pair generated (`~/.ssh/id_ed25519`)
- [ ] `.env` created from `.env.example` with real values

### AI / RAG Scope
- [ ] Python 3.11+ installed and verified
- [ ] Virtual environment created in `ai/` and activated
- [ ] `pip install -r ai/requirements.txt` completes without error
- [ ] Postman installed and a test request to the Nextcloud API succeeds
- [ ] Ollama installed locally (optional — for offline [LLM](../../concepts/ai/generation/llm.md) testing)

### Security Scope
- [ ] [SSH](../../concepts/protocols/ssh.md) client tested — can connect to a remote server
- [ ] Postman installed
- [ ] VS Code [REST](../../concepts/backend/api/rest.md) Client extension installed

### Deployment Scope
- [ ] [Docker](../../concepts/containers/docker.md) Desktop configured with 4 GB RAM
- [ ] VS Code [Docker](../../concepts/containers/docker.md) + Bash IDE + ShellCheck extensions installed
- [ ] WSL2 / Ubuntu working — Bash scripts run correctly inside WSL2
- [ ] `docker compose up -d` tested locally with the project stack

### Infrastructure Scope
- [ ] [Terraform](../../concepts/cloud/iac/terraform.md) CLI installed — `terraform --version` shows v1.7+
- [ ] [Azure](../../concepts/cloud/azure/azure.md) CLI installed — `az --version` works
- [ ] [Azure](../../concepts/cloud/azure/azure.md) account logged in — `az login` and `az account list` works
- [ ] VS Code HashiCorp [Terraform](../../concepts/cloud/iac/terraform.md) extension installed
- [ ] [SSH](../../concepts/protocols/ssh.md) key configured — private key at `~/.ssh/id_ed25519`
- [ ] Minimal [Terraform](../../concepts/cloud/iac/terraform.md) test: `terraform init` runs without error

## Related
- [git-github-basics.md](../git/git-github-basics.md)
- [ssh-client.md](ssh-client.md)
- [vscode.md](vscode.md)
- [development-workflow.md](development-workflow.md)
