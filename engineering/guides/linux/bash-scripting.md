# Bash Scripting for Server Automation

## What is it?

Bash (Bourne Again SHell) is the default command-line interpreter on Linux systems. A Bash script is a plain text file containing a sequence of Linux commands that the system executes automatically, top to bottom. It is used to automate repetitive tasks that would otherwise require a human to type commands manually.

## Why use it?

- **Automation:** One command runs a 50-step setup process without human involvement
- **Repeatability:** The same script on a fresh server produces the same result every time
- **Speed:** Deploys the entire stack in minutes, not hours
- **Documentation:** The script itself documents exactly how to set up the system

## Example: Scripts in a Deployment Project

| Script | Purpose | Typical owner |
|---|---|---|
| `setup.sh` | Prepares a fresh Ubuntu VM: installs packages, [Docker](../../concepts/containers/docker.md), [Docker Compose](../../concepts/containers/docker-compose.md), clones the repo | IT / Infra |
| `deploy.sh` | Starts the application stack with [Docker Compose](../../concepts/containers/docker-compose.md), waits for health, reports status | IT / Infra |
| `health-check.sh` | Checks that all services (application, database, background workers) are running and responding | IT / Infra |
| `backup.sh` | Backs up application files, database, and configuration to a timestamped archive | IT / Infra |
| `restore.sh` | Restores application files and database from a backup archive | IT / Infra |

## Basic Bash Concepts

```bash
#!/bin/bash
# This line (shebang) tells the OS this is a Bash script

# Variables
APP_DIR="/opt/nextcloud"
DATE=$(date +%Y%m%d_%H%M%S)   # capture command output into a variable

# Conditional
if [ -d "$APP_DIR" ]; then
  echo "Directory exists"
else
  echo "Directory not found"
  exit 1   # exit with error code
fi

# Loop
for file in *.txt; do
  echo "Processing: $file"
done

# Running a command and checking success
docker compose up -d
if [ $? -ne 0 ]; then
  echo "ERROR: docker compose failed"
  exit 1
fi
```

## Key Bash Patterns for Production Scripts

**Error handling:** Every script should exit immediately if any command fails:
```bash
set -e          # exit on any error
set -u          # error on undefined variables
set -o pipefail # catch errors in pipelines
```

**Logging:** Scripts should log what they are doing:
```bash
echo "[$(date)] Starting backup..."
echo "[$(date)] Backup complete: $BACKUP_FILE"
```

**Health check pattern:**
```bash
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" https://localhost)
if [ "$HTTP_CODE" = "200" ]; then
  echo "PASS: service is responding"
else
  echo "FAIL: service returned HTTP $HTTP_CODE"
fi
```

## Running Scripts

```bash
# Make a script executable (do this once)
chmod +x setup.sh

# Run a script
./setup.sh

# Run with sudo (if elevated permissions needed)
sudo ./setup.sh
```

## How Bash Fits into a Deployment Pipeline

Bash scripts are commonly the automation layer between [Infrastructure as Code](../../concepts/cloud/iac/infrastructure-as-code.md) (e.g. [Terraform](../../concepts/cloud/iac/terraform.md)) and container orchestration (e.g. [Docker](../../concepts/containers/docker.md) Compose). After `terraform apply` creates the VM, `setup.sh` prepares the OS, and `deploy.sh` starts the application. The goal is that any team member can reproduce the full deployment with a handful of commands: `terraform apply`, `./setup.sh`, `./deploy.sh`.

## Related

- [Ubuntu Server Setup](ubuntu-server-setup.md)
- [Nextcloud](../cloud/nextcloud-rag-case-study/nextcloud.md)
- [Docker Compose](../../concepts/containers/docker-compose.md)
