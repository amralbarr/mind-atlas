# SSH Client Setup

## What Is It?

[SSH](../../concepts/protocols/ssh.md) (Secure Shell) is the standard protocol for securely connecting to remote servers. An [SSH](../../concepts/protocols/ssh.md) client lets you open a terminal session on a remote Linux machine (like an [Azure](../../concepts/cloud/azure/azure.md) VM) from your local computer. Key-based [authentication](../../concepts/security/auth/authentication.md) — using a cryptographic key pair instead of a password — is the secure standard.

## Install

| OS | Status |
|---|---|
| Windows 10/11 | Built-in — OpenSSH Client is pre-installed |
| Mac | Built-in — OpenSSH available in Terminal |
| Linux / WSL2 | Built-in — `ssh` available by default |

**Verify (all platforms):**
```bash
ssh -V    # OpenSSH_9.x or similar
```

**If missing on Windows:**
Settings → Apps → Optional Features → Add a feature → OpenSSH Client

## Generate an SSH Key Pair

Run once per machine. Creates a private key (keep secret) and a public key (share with servers).

```bash
# Generate an Ed25519 key (modern, recommended)
ssh-keygen -t ed25519 -C "your@email.com"

# Accept default location: ~/.ssh/id_ed25519
# Set a passphrase (optional but recommended)
```

Your keys are stored at:
- `~/.ssh/id_ed25519` — **private key** — never share or commit this
- `~/.ssh/id_ed25519.pub` — **public key** — this is what you give to servers

**View your public key:**
```bash
cat ~/.ssh/id_ed25519.pub
```

## Connect to a Remote Server

```bash
# Basic connection
ssh username@<server-ip>

# With a specific private key file
ssh -i ~/.ssh/id_ed25519 username@<server-ip>

# With a specific port (default is 22)
ssh -p 2222 username@<server-ip>
```

## SSH Config File

Create `~/.ssh/config` to define shortcuts for servers you connect to regularly:

```
Host myserver
    HostName 20.10.30.40
    User azureuser
    IdentityFile ~/.ssh/id_ed25519
    Port 22
```

After saving, connect with just:
```bash
ssh myserver
```

## Copy Public Key to a Server

```bash
# Automatically (Linux/Mac/WSL2)
ssh-copy-id -i ~/.ssh/id_ed25519.pub username@<server-ip>

# Manually — paste your public key into the server's authorized_keys
cat ~/.ssh/id_ed25519.pub
# Copy the output, then on the server:
# echo "paste-key-here" >> ~/.ssh/authorized_keys
```

## Secure SSH Server Configuration

On the remote server (`/etc/ssh/sshd_config`), apply these settings to harden access:

```
PermitRootLogin no
PasswordAuthentication no
PubkeyAuthentication yes
AllowUsers azureuser
```

Apply changes:
```bash
sudo systemctl restart ssh
```

## VS Code Remote-SSH

Connect to the remote server and edit files in VS Code:

1. Install the **Remote - [SSH](../../concepts/protocols/ssh.md)** extension (Microsoft)
2. Press `F1` → **Remote-[SSH](../../concepts/protocols/ssh.md): Connect to Host**
3. Enter `username@<server-ip>` or use your [SSH](../../concepts/protocols/ssh.md) config alias
4. VS Code opens a new window connected to the remote filesystem

All editing, terminal commands, and extensions run on the remote server.

## SCP — Copy Files Over SSH

```bash
# Copy a local file to the server
scp localfile.txt username@<server-ip>:/remote/path/

# Copy a file from the server to local
scp username@<server-ip>:/remote/path/file.txt ./local/

# Copy a directory recursively
scp -r ./local-dir username@<server-ip>:/remote/path/
```

## `.gitignore` Entries for SSH Keys

```gitignore
# SSH private keys — never commit
*.pem
id_rsa
id_ed25519
id_ecdsa
*.key
```

## Tips

- Never share or commit your private key — treat it like a password
- Use a passphrase on your private key for an extra layer of protection
- Use the SSH config file to avoid re-typing IPs and usernames
- Disable password [authentication](../../concepts/security/auth/authentication.md) on servers once key-based auth is working

## Related

- [VS Code](vscode.md)
- [WSL2 Installation (Windows)](../../installation/windows/wsl2.md)
- [Ubuntu Server Setup](../../guides/linux/ubuntu-server-setup.md)
- [VirtualBox + Ubuntu](virtualbox-ubuntu.md)
