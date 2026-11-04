# Ubuntu Server Setup

## What is it?

Ubuntu Server is a free, open-source Linux operating system widely used for cloud servers, web hosting, and enterprise infrastructure. It is a common choice as the underlying OS for cloud VMs that run [Docker](../../concepts/containers/docker.md), [Docker Compose](../../concepts/containers/docker-compose.md), and application services.

**Version referenced here:** Ubuntu Server 22.04 LTS (Long-Term Support) — supported until 2027.

## Why Ubuntu?

- Free and open source
- Official [Docker](../../concepts/containers/docker.md) support and easy installation
- Large community and extensive documentation
- Stable LTS release — security patches available for 5 years
- Standard choice for cloud Linux VMs ([Azure](../../concepts/cloud/azure/azure.md), [AWS](../../concepts/cloud/infrastructure/aws.md), [GCP](../../concepts/cloud/infrastructure/gcp.md))
- Familiar environment for most IT professionals

## Key Linux Concepts

### File System Structure

```
/                       root of the file system
├── etc/                configuration files
├── var/                variable data (logs, app data)
├── opt/                optional application software
├── home/               user home directories
├── tmp/                temporary files
└── usr/                user programs and utilities
```

### Users and Permissions

Linux uses a permission model for files and directories:
```
-rw-r--r--  1  alice  finance  1024  Sep 1  report.txt
│           │   │       │
│           │   owner  group
│           number of links
permission bits: owner(rw-) group(r--) others(r--)
```

For a file containing secrets (e.g. `.env`):
```bash
chmod 600 .env   # only the owner can read and write — no one else
```

### SSH (Secure Shell)

[SSH](../../concepts/protocols/ssh.md) is how administrators connect to a Ubuntu VM remotely over an encrypted connection:
```bash
ssh -i ~/.ssh/id_rsa ubuntu@<VM-PUBLIC-IP>
```

**Key-based [authentication](../../concepts/security/auth/authentication.md):** Instead of a password, [SSH](../../concepts/protocols/ssh.md) uses a cryptographic key pair:
- **Private key:** Stays on your local machine (never shared)
- **Public key:** Placed on the server in `~/.ssh/authorized_keys`
- Connection is authenticated by proving you have the private key without sending it

**Security hardening for [SSH](../../concepts/protocols/ssh.md):**
```
/etc/ssh/sshd_config:
  PermitRootLogin no           # disable root login
  PasswordAuthentication no    # disable password auth (keys only)
  AllowUsers ubuntu            # only allow the ubuntu user
```

### systemctl (Service Management)

Services on Ubuntu are managed with `systemctl`:
```bash
systemctl status docker     # check if Docker is running
systemctl start docker      # start Docker
systemctl enable docker     # start Docker automatically on boot
systemctl restart docker    # restart Docker
```

### UFW (Firewall)

UFW (Uncomplicated Firewall) is Ubuntu's firewall:
```bash
ufw allow 443/tcp       # allow HTTPS
ufw allow 22/tcp        # allow SSH
ufw deny 5432/tcp       # deny PostgreSQL port from outside
ufw enable              # activate the firewall
ufw status              # show current rules
```

UFW at the host level typically works alongside a cloud-provider network firewall (e.g. [Azure NSG](../../concepts/cloud/azure/azure-nsg.md)) for defense in depth.

### Package Management (apt)

Ubuntu uses `apt` to install software:
```bash
apt update                    # refresh package list
apt upgrade                   # upgrade installed packages
apt install docker.io         # install a package
apt install -y curl wget git  # install multiple, auto-confirm
```

## Example Setup Script

```bash
#!/bin/bash
set -e

# Update the system
apt update && apt upgrade -y

# Install prerequisites
apt install -y ca-certificates curl gnupg git

# Install Docker
install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" > /etc/apt/sources.list.d/docker.list
apt update
apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Start and enable Docker
systemctl enable docker
systemctl start docker

echo "Setup complete."
```

## How This Fits into a Typical Deployment

Ubuntu is usually the OS layer managed by the IT/infrastructure team. After the VM is provisioned (e.g. via [Terraform](../../concepts/cloud/iac/terraform.md)), an operator connects via [SSH](../../concepts/protocols/ssh.md) and runs a setup script to install [Docker](../../concepts/containers/docker.md) and prepare the environment. All subsequent application work then happens inside containers on top of Ubuntu.

## Related

- [Bash Scripting for Server Automation](bash-scripting.md)
- [Nextcloud](../cloud/nextcloud-rag-case-study/nextcloud.md)
- [Access Control & IAM](../../concepts/security/authorization/access-control-iam.md)
- [Virtual Machines](../../concepts/cloud/infrastructure/virtual-machines.md)
- [Networking: VNet & NSG](../../concepts/cloud/azure/networking-vnet-nsg.md)
