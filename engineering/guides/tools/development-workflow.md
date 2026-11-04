# Development Workflow: Local vs VM

## The Core Rule

```
Write code  →  Your LOCAL machine  (Windows / Mac, VS Code, Claude Code, Cursor)
Run code    →  AZURE VM            (Ubuntu 22.04, Docker, Bash scripts)
Sync        →  GitHub              (git push from local → git pull on VM)
```

You **never run the full project on your local machine**.
You **never write code directly on the [Azure](../../concepts/cloud/azure/azure.md) VM**.

## Two Environments Explained

| | Your Local Machine | [Azure](../../concepts/cloud/azure/azure.md) VM (Production) |
|---|---|---|
| **OS** | Windows or Mac | Ubuntu 22.04 LTS |
| **Purpose** | Write code, edit files | Run [Docker](../../concepts/containers/docker.md), test the full stack |
| **Tools** | VS Code, Claude Code, Cursor, Git | [Docker](../../concepts/containers/docker.md), Bash, Git |
| **Python venv** | Yes — for running/testing AI code locally | Inside [Docker](../../concepts/containers/docker.md) container |
| **[Docker](../../concepts/containers/docker.md)** | Optional ([Docker](../../concepts/containers/docker.md) Desktop for local testing) | Required — all services run here |
| **Bash scripts** | Write them here | Execute them here |
| **[Terraform](../../concepts/cloud/iac/terraform.md)** | Write files here | Run `terraform apply` from local or WSL2 |
| **`.env` file** | Separate copy, never committed | Separate copy, never committed |

## Step-by-Step Daily Workflow

### Step 1 — Write Code on Your Local Machine

Open the project in your editor:

```bash
# Open in VS Code
code .

# Or in Cursor
cursor .
```

Edit any file: Python scripts, Bash scripts, `docker-compose.yml`, `.tf` files, Markdown docs.

Use AI coding assistants freely — Claude Code, Cursor, GitHub Copilot.

### Step 2 — Commit and Push to GitHub

Same on Linux, Mac, and Windows:

```bash
git add .
git commit -m "feat: add permission filter to retriever"
git push origin main
```

### Step 3 — Pull Changes on the Azure VM

Connect to the VM via [SSH](../../concepts/protocols/ssh.md), then pull:

```bash
# From your local terminal (Linux/Mac/Windows — ssh works on all)
ssh azureuser@<azure-public-ip>

# Once inside the VM:
git -C ~/nextcloud-rag-platform pull
```

Or use the deploy script:

```bash
bash ~/nextcloud-rag-platform/scripts/deploy.sh
```

### Step 4 — Run the Project on the VM

All these commands run **on the [Azure](../../concepts/cloud/azure/azure.md) VM** (via [SSH](../../concepts/protocols/ssh.md)):

```bash
# Start all services
docker compose -f ~/nextcloud-rag-platform/deployment/docker-compose.yml up -d

# Check all containers are running
docker compose -f ~/nextcloud-rag-platform/deployment/docker-compose.yml ps

# View logs if something is wrong
docker compose -f ~/nextcloud-rag-platform/deployment/docker-compose.yml logs -f

# Run health check
bash ~/nextcloud-rag-platform/scripts/health-check.sh
```

### Step 5 — Test and Verify

Access Nextcloud in a browser from your local machine:

```
https://<azure-public-ip>
```

Test the AI endpoint from the VM:

```bash
curl -X POST http://localhost:5000/ask \
  -H "Content-Type: application/json" \
  -d '{"username": "finance_user1", "question": "What is Q3 net income?"}'
```

### Step 6 — Iterate

Go back to Step 1 — edit locally → commit → pull on VM → retest.

## Which Commands Run Where

| Command | Where it runs | Notes |
|---|---|---|
| `git add / commit / push` | Local machine | Same on all OS |
| `git pull` | [Azure](../../concepts/cloud/azure/azure.md) VM (via [SSH](../../concepts/protocols/ssh.md)) | Pulls your pushed code |
| `docker compose up -d` | [Azure](../../concepts/cloud/azure/azure.md) VM | [Docker](../../concepts/containers/docker.md) runs on the VM |
| `docker compose ps / logs` | [Azure](../../concepts/cloud/azure/azure.md) VM | Monitor containers on VM |
| `bash scripts/setup.sh` | [Azure](../../concepts/cloud/azure/azure.md) VM | Installs packages on Ubuntu |
| `bash scripts/deploy.sh` | [Azure](../../concepts/cloud/azure/azure.md) VM | Pulls + restarts stack |
| `bash scripts/health-check.sh` | Azure VM | Checks container status |
| `bash scripts/backup.sh` | Azure VM | Backs up data on VM |
| `terraform init / plan / apply` | Local machine or WSL2 | Provisions Azure resources |
| `az login` | Local machine | Authenticates Azure CLI |
| `python ai/indexer.py` | Azure VM (inside [Docker](../../concepts/containers/docker.md)) | Indexes documents |
| `source venv/bin/activate` | Local machine (Linux/Mac) | For local Python testing only |
| `venv\Scripts\activate` | Local machine (Windows) | For local Python testing only |

## OS-Specific: Activating the Python Virtual Environment (Local Only)

The Python venv is used **locally** to test AI code before pushing. On the Azure VM, Python runs inside the [Docker](../../concepts/containers/docker.md) container — no venv needed there.

**Linux / Mac:**

```bash
source venv/bin/activate
deactivate   # to exit
```

**Windows (CMD):**

```cmd
venv\Scripts\activate
deactivate
```

**Windows (PowerShell):**

```powershell
venv\Scripts\Activate.ps1
deactivate
```

> If PowerShell blocks the script, run once: `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`

## OS-Specific: Path Separators

| Action | Linux / Mac | Windows CMD | Windows PowerShell |
|---|---|---|---|
| Create folders | `mkdir -p a/b/c` | `mkdir a\b\c` | `mkdir a\b\c` |
| Copy file | `cp src dst` | `copy src dst` | `Copy-Item src dst` |
| Delete folder | `rm -rf folder/` | `rmdir /s /q folder` | `Remove-Item -Recurse -Force folder\` |
| Path in commands | `deployment/nginx/ssl` | `deployment\nginx\ssl` | `deployment\nginx\ssl` |
| Line continuation | `\` | `^` | `` ` `` (backtick) |

## Optional: Edit Directly on the VM via Remote-SSH

If you want to skip the git push/pull cycle during active debugging, connect VS Code directly to the VM:

1. Install the **Remote - [SSH](../../concepts/protocols/ssh.md)** extension in VS Code.
2. Press `F1` → `Remote-SSH: Connect to Host` → enter `azureuser@<azure-ip>`.
3. VS Code opens a window where all files are on the VM filesystem.
4. Edit files and run terminal commands directly on the VM.

```
VS Code (local UI) ──SSH──► VM filesystem + terminal
                              Docker runs here
                              No push/pull needed mid-session
```

**Important:** Still commit and push to GitHub when your session ends. Do not leave code only on the VM.

## What Each File Is Edited Where

| File | Edit where | Run where |
|---|---|---|
| `ai/*.py` (Python AI code) | Local machine | Azure VM (inside Docker) |
| `scripts/*.sh` (Bash scripts) | Local machine | Azure VM |
| `deployment/docker-compose.yml` | Local machine | Azure VM |
| `deployment/nginx/nginx.conf` | Local machine | Azure VM (inside nginx container) |
| `infrastructure/terraform/*.tf` | Local machine | Local machine or WSL2 (`terraform apply`) |
| `deployment/.env` | Created separately on each machine | Azure VM (never committed to Git) |
| `docs/*.md` | Local machine | — (documentation only) |
| `security/*.md` | Local machine | — (documentation only) |

## The `.env` File — Never Committed

Each machine needs its own `.env` file. It is in `.gitignore` and must never be committed.

**To create it:**

Linux / Mac:

```bash
cp deployment/.env.example deployment/.env
# then edit with real values
nano deployment/.env
```

Windows (CMD):

```cmd
copy deployment\.env.example deployment\.env
```

Windows (PowerShell):

```powershell
Copy-Item deployment\.env.example deployment\.env
```

Then open with any text editor and fill in:
- `POSTGRES_PASSWORD` — choose a strong password
- `NEXTCLOUD_ADMIN_PASSWORD` — choose a strong password
- `NEXTCLOUD_TRUSTED_DOMAINS` — `localhost` for local, `<azure-ip>` on the VM
- `OPENAI_API_KEY` — your key from https://platform.openai.com

## Summary

```
┌─────────────────────────────────────────────────────────┐
│  LOCAL MACHINE (Windows / Mac)                          │
│  - Write all code (Python, Bash, YAML, HCL, Markdown)  │
│  - Run: git add / commit / push                         │
│  - Run: terraform apply (provisions Azure)              │
│  - Run: python locally with venv (optional testing)     │
└───────────────────────┬─────────────────────────────────┘
                        │ git push
                        ▼
                    [ GitHub ]
                        │ git pull
                        ▼
┌─────────────────────────────────────────────────────────┐
│  AZURE VM (Ubuntu 22.04)                                │
│  - Run: docker compose up -d                            │
│  - Run: bash scripts/setup.sh / deploy.sh               │
│  - Run: bash scripts/health-check.sh / backup.sh        │
│  - Run: python ai/indexer.py (inside Docker container)  │
│  - Hosts: Nextcloud, PostgreSQL, nginx, AI service      │
└─────────────────────────────────────────────────────────┘
```

## Related
- [git-github-basics.md](../git/git-github-basics.md)
- [ssh-client.md](ssh-client.md)
- [vscode.md](vscode.md)
- [local-development-tools.md](local-development-tools.md)
