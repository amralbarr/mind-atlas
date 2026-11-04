# WSL2

## What Is It?

WSL2 (Windows Subsystem for Linux 2) runs a real Linux kernel directly inside Windows. It lets you use Linux tools — Bash, apt, curl, ssh, Python, [Terraform](../../concepts/cloud/iac/terraform.md) — natively on a Windows machine without a separate virtual machine. [Docker](../../concepts/containers/docker.md) Desktop uses WSL2 as its backend on Windows.

## Why Use It?

- Bash scripts written for the Linux server run identically in WSL2.
- [Terraform](../../concepts/cloud/iac/terraform.md), [Azure](../../concepts/cloud/azure/azure.md) CLI, and [SSH](../../concepts/protocols/ssh.md) work naturally in a Linux environment.
- [Docker](../../concepts/containers/docker.md) Desktop integrates with WSL2 for better performance.
- Avoids "works on Linux but not on Windows" issues.

## Install

**Requirements:** Windows 10 version 2004+ or Windows 11.

**Step 1 — Install WSL2 (PowerShell as Administrator):**

```powershell
wsl --install
```

This installs WSL2 and Ubuntu by default. Restart your computer when prompted.

**Step 2 — Install Ubuntu 22.04 (if not installed automatically):**

```powershell
wsl --install -d Ubuntu-22.04
```

Or install from the Microsoft Store → search "Ubuntu 22.04 LTS".

**Step 3 — Set WSL2 as the default version:**

```powershell
wsl --set-default-version 2
```

**Verify:**

```powershell
wsl --list --verbose
# Should show Ubuntu-22.04 with VERSION 2
```

## First-Time Setup Inside WSL2

Open WSL2 (search "Ubuntu" in the Start menu) and run:

```bash
# Update packages
sudo apt update && sudo apt upgrade -y

# Install common tools
sudo apt install -y git curl wget unzip build-essential

# Verify you are on Ubuntu 22.04
lsb_release -a
```

## Access Project Files

**From WSL2, access Windows files:**

```bash
cd /mnt/c/Users/YourName/Projects/your-project
```

**Recommended:** Keep project files inside the WSL2 filesystem for better performance:

```bash
cd ~/projects
git clone https://github.com/your-org/your-repo.git
```

## Integration with Other Tools

**[Docker](../../concepts/containers/docker.md) Desktop:** Enable WSL2 integration in [Docker](../../concepts/containers/docker.md) Desktop settings:
- [Docker](../../concepts/containers/docker.md) Desktop → Settings → Resources → WSL Integration → Enable for Ubuntu-22.04

After enabling, `docker` and `docker compose` commands work inside WSL2 directly.

**VS Code:** Install the "WSL" extension by Microsoft. Then open any WSL2 folder in VS Code:

```bash
# From inside WSL2 terminal
code .
```

VS Code opens with the WSL2 filesystem — all extensions run on Linux.

**Windows Terminal:** Automatically detects WSL2 — adds Ubuntu as a tab option. Install from the Microsoft Store → "Windows Terminal".

## Useful Commands

```bash
# Check WSL version from PowerShell
wsl --version

# List installed distributions
wsl --list --verbose

# Shut down all WSL instances
wsl --shutdown

# Open a specific distribution
wsl -d Ubuntu-22.04

# Set default distribution
wsl --set-default Ubuntu-22.04
```

## Tips

- Use Ubuntu 22.04 — the same OS version as the project's cloud server — so scripts behave identically locally and in production.
- Store code inside the WSL2 filesystem (`~/projects/`), not on `/mnt/c/` — file [I/O](../../concepts/programming/fundamentals/io.md) is significantly faster.
- Windows Terminal gives you tabs for PowerShell, CMD, and WSL2 all in one window.

## Related
- [../../concepts/containers/docker.md](../../concepts/containers/docker.md)
- [Ubuntu Server Setup](../../guides/linux/ubuntu-server-setup.md)
- [../../guides/tools/development-workflow.md](../../guides/tools/development-workflow.md)
