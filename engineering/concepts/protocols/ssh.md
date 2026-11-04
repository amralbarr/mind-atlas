# SSH (Secure Shell)

**SSH** is an encrypted protocol for securely accessing and controlling a remote machine over an untrusted network — a remote terminal session, file transfer, port forwarding, and more, all protected by the same encrypted connection. It runs over [TCP](../networking/tcp.md), conventionally on port 22, and replaced older, plaintext remote-access protocols (Telnet, rsh) that sent credentials and data unencrypted.

## What SSH Actually Provides

```
Client                                    Server
  │  SSH connection request  ─────────────▶  │
  │  ◀───── server's host key presented ──── │
  │  (client verifies the key is trusted)     │
  │  ───── key exchange, session encrypted ─▶ │
  │  ───── authenticate (key or password) ──▶ │
  │  ◀──────── encrypted shell session ─────▶ │
```

- **Encryption** — every byte after the handshake is encrypted, so credentials and data can't be read in transit even on an untrusted network.
- **[Authentication](../security/auth/authentication.md)** — via a password, or (far more common and more secure) a public/private key pair: the server trusts any client that can prove possession of the matching private key.
- **Integrity** — the protocol detects tampering with data in transit, not just eavesdropping.

## Key-Based Authentication

The standard, recommended [authentication](../security/auth/authentication.md) method — never password-based for anything production-facing:

```bash
ssh-keygen -t ed25519 -C "my-key"          # generate a key pair locally
ssh-copy-id user@remote-host                # install the public key on the server
ssh user@remote-host                        # the private key authenticates automatically
```

The private key never leaves the client machine; the server only ever holds the public key. A leaked public key is harmless — a leaked private key is a full compromise of every server that trusts it, which is why private keys should themselves be encrypted at rest (a passphrase) and never committed to a repository.

## What Runs on Top of SSH

SSH isn't only an interactive shell — several other protocols and tools tunnel through the same encrypted connection:

| Built on SSH | What it does |
|---|---|
| **SFTP** | File transfer over the SSH connection — see [FTP / SFTP](ftp-sftp.md) for the comparison with plaintext FTP |
| **SCP** | Simple file copy over SSH, an older/simpler alternative to SFTP |
| **Port forwarding / tunneling** | Forwards a local or remote port through the encrypted SSH connection — exposes a service on a remote network without opening it to the public internet |
| **Git over SSH** | `git@github.com:...` URLs authenticate via an SSH key instead of a username/password or token |
| **rsync over SSH** | File synchronization using SSH as its secure transport |

## SSH in Production Access Control

- **Bastion hosts** — a single hardened, monitored entry point that all SSH access to a private network must go through, rather than exposing every server's SSH port directly to the internet; see [Azure Bastion](../cloud/remote-access/azure-bastion.md) for a managed cloud implementation of this pattern.
- **Restrict by IP/network** — SSH access should be limited to specific trusted IP ranges or a VPN, not open to `0.0.0.0/0`.
- **Disable password [authentication](../security/auth/authentication.md)** — key-only [authentication](../security/auth/authentication.md) removes an entire class of [brute-force attacks](../security/attacks/brute-force.md); see [Brute-Force Attacks](../security/attacks/brute-force.md) and [fail2ban](../security/attacks/fail2ban.md) for what still has to be defended against when password auth can't be fully disabled.
- **Disable root login** — authenticate as a normal user and `sudo` for privileged actions, so every action is attributable to a specific key/user, not an anonymous shared "root."

## Related

- [TCP](../networking/tcp.md) — the transport protocol SSH runs over
- [FTP / SFTP](ftp-sftp.md) — SFTP is a subsystem of SSH, not FTP-over-SSH
- [Azure Bastion](../cloud/remote-access/azure-bastion.md) — a managed bastion-host implementation gating SSH access
- [Brute-Force Attacks](../security/attacks/brute-force.md) — the attack class key-only [authentication](../security/auth/authentication.md) defends against
- [fail2ban](../security/attacks/fail2ban.md) — rate-limiting repeated failed SSH login attempts
- [Access Control & IAM](../security/authorization/access-control-iam.md)
- [Authentication](../security/auth/authentication.md) — SSH key-based auth as a concrete instance of the general concept
