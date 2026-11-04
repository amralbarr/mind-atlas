# FTP / SFTP

FTP (File Transfer Protocol) and SFTP ([SSH](ssh.md) File Transfer Protocol) are protocols for transferring files between a client and a server. Despite the similar names, they are fundamentally different protocols — SFTP is not FTP over [SSH](ssh.md); it is a completely separate subsystem of the [SSH](ssh.md) protocol.

## FTP vs SFTP at a Glance

| | FTP | SFTP |
|---|---|---|
| Protocol | [TCP](../networking/tcp.md) (port 21) | [SSH](ssh.md) subsystem (port 22) |
| Encryption | None (plaintext) | Full encryption via [SSH](ssh.md) |
| Auth | Username + password | Password or [SSH](ssh.md) key pair |
| Firewall-friendly | No (dual-channel) | Yes (single port) |
| Use today | Legacy systems only | Standard for secure file transfer |

**Never use plain FTP in production.** All credentials and file content are transmitted in plaintext. Use SFTP or FTPS (FTP over [TLS](../networking/tls.md)) instead.

## How FTP Works (Dual-Channel)

FTP opens two [TCP](../networking/tcp.md) connections:
- **Control channel** (port 21) — commands and responses
- **Data channel** (port 20 or ephemeral) — actual file content

This dual-channel design makes FTP hostile to firewalls and NAT, since the data channel port is negotiated dynamically.

## How SFTP Works

SFTP runs as a subsystem over a single [SSH](ssh.md) connection (port 22). All communication — [authentication](../security/auth/authentication.md), commands, data — is encrypted and flows through one channel. It supports the same file operations as FTP plus extras like stat, symlinks, and permissions.

## Common Operations (SFTP CLI)

```bash
# Connect
sftp user@host

# Inside the SFTP shell:
ls                        # list remote directory
lls                       # list local directory
pwd / lpwd                # remote / local working directory
get remote.txt local.txt  # download
put local.txt remote.txt  # upload
mkdir /remote/dir         # create directory
rm /remote/file.txt       # delete file
chmod 644 remote.txt      # change permissions
exit
```

Batch transfer (non-interactive):

```bash
sftp user@host <<'EOF'
get /remote/report.pdf ./report.pdf
put ./data.csv /remote/data.csv
EOF
```

## Python Client (`paramiko`)

```bash
pip install paramiko
```

```python
import paramiko
import os
from dotenv import load_dotenv

load_dotenv()

transport = paramiko.Transport((os.getenv("SFTP_HOST"), int(os.getenv("SFTP_PORT", 22))))
transport.connect(username=os.getenv("SFTP_USER"), password=os.getenv("SFTP_PASSWORD"))

sftp = paramiko.SFTPClient.from_transport(transport)

# List directory
print(sftp.listdir("/remote/files/"))

# Download
sftp.get("/remote/files/report.pdf", "local_report.pdf")

# Upload
sftp.put("local_data.csv", "/remote/files/data.csv")

# Delete
sftp.remove("/remote/files/old.txt")

sftp.close()
transport.close()
```

### Key-based authentication (recommended over password)

```python
key = paramiko.RSAKey.from_private_key_file(os.getenv("SFTP_KEY_PATH"))
transport.connect(username=os.getenv("SFTP_USER"), pkey=key)
```

## Python Client (`pysftp` — simpler wrapper)

```bash
pip install pysftp
```

```python
import pysftp
import os

cnopts = pysftp.CnOpts()
cnopts.hostkeys = None  # disable host key checking (dev only — enable in prod)

with pysftp.Connection(
    host=os.getenv("SFTP_HOST"),
    username=os.getenv("SFTP_USER"),
    password=os.getenv("SFTP_PASSWORD"),
    cnopts=cnopts,
) as sftp:
    sftp.get("/remote/report.pdf", "report.pdf")
    sftp.put("data.csv", "/remote/data.csv")
    files = sftp.listdir("/remote/")
```

## Environment Variables

```bash
# .env
SFTP_HOST=sftp.example.com
SFTP_PORT=22
SFTP_USER=myuser
SFTP_PASSWORD=secret
SFTP_KEY_PATH=~/.ssh/id_rsa
```

## FTPS (FTP over TLS)

FTPS adds [TLS](../networking/tls.md) encryption to FTP. It comes in two modes:
- **Explicit FTPS** — client upgrades the connection with `AUTH TLS` after connecting on port 21
- **Implicit FTPS** — [TLS](../networking/tls.md) from the start, usually on port 990

FTPS still has the dual-channel firewall problem. Prefer SFTP unless you're integrating with a legacy system that requires FTPS.

## Security Checklist

- Never use plain FTP — always SFTP or FTPS
- Prefer [SSH](ssh.md) key [authentication](../security/auth/authentication.md) over passwords for SFTP
- Validate server host keys in production (`cnopts.hostkeys` should NOT be `None`)
- Use a dedicated service account with minimal permissions (read-only if possible)
- Store credentials in `.env`, never hardcoded

## Related Concepts

- [WebDAV](./webdav.md) — [HTTP](../networking/http.md)-based file management (firewall-friendly, browser-accessible)
- [Object Storage / MinIO](../cloud/infrastructure/object-storage.md) — S3-compatible blob storage for modern architectures
- [SMB / NFS](./smb-nfs.md) — LAN network file sharing
