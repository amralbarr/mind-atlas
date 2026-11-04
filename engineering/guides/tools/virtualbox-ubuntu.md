# VirtualBox + Ubuntu

## What Is It?

VirtualBox is a free virtual machine manager. Running Ubuntu 22.04 inside VirtualBox gives you a full Linux environment on any host OS (Windows, Mac). It is a valid alternative to WSL2 — all project tools install and behave identically inside it.

## WSL2 vs VirtualBox Ubuntu — Which to Use?

| | WSL2 | VirtualBox Ubuntu |
|---|---|---|
| Setup effort | Low | Medium |
| Performance | Faster (integrated with Windows kernel) | Slightly slower |
| [Docker](../../concepts/containers/docker.md) | [Docker](../../concepts/containers/docker.md) Desktop (GUI) | [Docker Engine](../../concepts/containers/docker-daemon.md) (terminal) |
| Matches [Azure](../../concepts/cloud/azure/azure.md) VM OS | Yes (Ubuntu 22.04) | Yes (Ubuntu 22.04) |
| Works on Windows | Yes | Yes |
| Works on Mac | No | Yes |
| Offline capable | Yes | Yes |

Both options produce the same development environment. Choose whichever your machine already has set up.

## Install VirtualBox + Ubuntu 22.04

**Step 1 — Download VirtualBox:**
- https://www.virtualbox.org/wiki/Downloads
- Install with default settings

**Step 2 — Download Ubuntu 22.04 ISO:**
- https://ubuntu.com/download/desktop (Desktop) or
- https://ubuntu.com/download/server (Server — lighter, recommended)

**Step 3 — Create a new VM in VirtualBox:**

| Setting | Recommended Value |
|---|---|
| Name | ubuntu-dev |
| Type | Linux |
| Version | Ubuntu (64-bit) |
| RAM | 4096 MB (4 GB) minimum |
| CPU | 2 cores minimum |
| Storage | 30 GB (dynamically allocated) |

**Step 4 — Boot the VM, attach the ISO, and install Ubuntu.**

## First-Time Setup Inside the VM

Open the Ubuntu terminal and run:

```bash
# Update packages
sudo apt update && sudo apt upgrade -y

# Install common tools
sudo apt install -y git curl wget unzip build-essential
```

## Install Docker Engine (No Docker Desktop Needed)

Inside the Ubuntu VM terminal:

```bash
# Official one-line install script
curl -fsSL https://get.docker.com | sh

# Add your user to the docker group (run docker without sudo)
sudo usermod -aG docker $USER
newgrp docker

# Install Docker Compose plugin
sudo apt install docker-compose-plugin
```

**Verify:**
```bash
docker --version          # Docker version 24.x.x or higher
docker compose version    # Docker Compose version v2.x.x or higher
docker run hello-world    # prints "Hello from Docker!"
```

## Install All Other Project Tools

Everything installs the same way as on any Ubuntu/Linux system.

**Git:**
```bash
sudo apt install git

git config --global user.name "Your Name"
git config --global user.email "your@email.com"
```

**Python 3.11:**
```bash
sudo apt install python3.11 python3.11-venv python3-pip

python3 --version    # 3.11.x
```

**[Terraform](../../concepts/cloud/iac/terraform.md):**
```bash
sudo apt update && sudo apt install -y gnupg software-properties-common

wget -O- https://apt.releases.hashicorp.com/gpg | \
  gpg --dearmor | \
  sudo tee /usr/share/keyrings/hashicorp-archive-keyring.gpg > /dev/null

echo "deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] \
  https://apt.releases.hashicorp.com $(lsb_release -cs) main" | \
  sudo tee /etc/apt/sources.list.d/hashicorp.list

sudo apt update && sudo apt install terraform

terraform --version
```

**[Azure](../../concepts/cloud/azure/azure.md) CLI:**
```bash
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash

az --version
az login
```

**[SSH](../../concepts/protocols/ssh.md) Client:**
```bash
# Built-in — no install needed
ssh -V

# Generate your key pair
ssh-keygen -t ed25519 -C "your@email.com"
```

## Access Project Files Inside the VM

**Option A — Clone from GitHub (recommended):**
```bash
git clone https://github.com/your-org/your-repo.git
cd your-repo
```

**Option B — Shared Folder (VirtualBox feature):**
1. VM Settings → Shared Folders → Add a host folder
2. Check "Auto-mount" and "Make Permanent"
3. Inside the VM, the folder appears at `/media/sf_<foldername>`

> For best performance, keep project files inside the VM filesystem, not in a shared folder.

## VS Code — Connect to VirtualBox VM

You can edit files inside the VM using VS Code on your host machine:

**Option A — Install VS Code inside the VM:**
```bash
sudo snap install code --classic
# Then open VS Code from inside the VM
```

**Option B — [SSH](../../concepts/protocols/ssh.md) into the VM from host VS Code (Remote-[SSH](../../concepts/protocols/ssh.md)):**
1. In VirtualBox: VM Settings → Network → Adapter 1 → Bridged Adapter (gives the VM its own IP)
2. Find the VM's IP: `ip addr show` inside the VM
3. In VS Code (host): Install **Remote - [SSH](../../concepts/protocols/ssh.md)** extension → connect to `username@<vm-ip>`

## Tips

- Allocate at least 4 GB RAM to the VM — Nextcloud + [PostgreSQL](../../concepts/databases/relational/postgresql.md) + the AI service all run simultaneously
- Use Ubuntu 22.04 — the same OS version as the [Azure](../../concepts/cloud/azure/azure.md) VM — so scripts behave identically in local testing and on the server
- Install VirtualBox Guest Additions for better display resolution and clipboard sharing: **Devices → Insert Guest Additions CD Image**
- Take a VM snapshot after initial setup so you can restore quickly if something breaks: **Machine → Take Snapshot**

## Related

- [Ubuntu Server Setup](../linux/ubuntu-server-setup.md)
- [SSH Client Setup](ssh-client.md)
- [VS Code](vscode.md)
