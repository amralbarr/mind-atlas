# SMB / NFS

SMB (Server Message Block) and NFS (Network File System) are network file-sharing protocols that make remote storage appear as a local drive to the operating system. Unlike [WebDAV](webdav.md) or SFTP — which are application-level protocols — SMB and NFS operate at a lower level and are typically used within a LAN or private network.

## SMB vs NFS at a Glance

| | SMB | NFS |
|---|---|---|
| Full name | Server Message Block | Network File System |
| Origin | Microsoft | Sun Microsystems / IETF |
| Primary OS | Windows (native); Linux/macOS via Samba | Linux/Unix (native); Windows via client |
| Port | [TCP](../networking/tcp.md) 445 (modern) | [TCP](../networking/tcp.md)/UDP 2049 |
| Auth | Active Directory / NTLM / Kerberos | Host-based (IP/hostname) or Kerberos (NFSv4) |
| Encryption | SMB 3.0+ supports encryption | NFSv4.1+ supports [TLS](../networking/tls.md) (Kerberized) |
| Best for | Cross-platform LAN sharing, Windows environments | Linux-to-Linux high-throughput, HPC, NAS |

## SMB (Server Message Block)

SMB is the native Windows file-sharing protocol. On Linux and macOS it is implemented by **Samba**.

### Mount an SMB share

```bash
# Linux
sudo mount -t cifs //server/share /mnt/share \
  -o username=myuser,password=secret,uid=$(id -u),gid=$(id -g)

# macOS (Finder)
# Go → Connect to Server → smb://server/share

# /etc/fstab entry for persistent mount
//server/share  /mnt/share  cifs  credentials=/etc/samba/creds,uid=1000,gid=1000  0  0
```

`/etc/samba/creds`:
```
username=myuser
password=secret
domain=WORKGROUP
```

### Python access with `smbprotocol`

```bash
pip install smbprotocol
```

```python
import smbclient
import os
from dotenv import load_dotenv

load_dotenv()

smbclient.register_session(
    os.getenv("SMB_HOST"),
    username=os.getenv("SMB_USER"),
    password=os.getenv("SMB_PASSWORD"),
)

# List files
for entry in smbclient.scandir(rf"\\{os.getenv('SMB_HOST')}\share\reports"):
    print(entry.name, entry.stat().st_size)

# Read a file
with smbclient.open_file(rf"\\{os.getenv('SMB_HOST')}\share\report.pdf", mode="rb") as f:
    data = f.read()

# Write a file
with smbclient.open_file(rf"\\{os.getenv('SMB_HOST')}\share\output.txt", mode="w") as f:
    f.write("hello")
```

### Docker: access SMB from a container

```yaml
# docker-compose.yml
services:
  app:
    image: myapp
    volumes:
      - smb_share:/mnt/share

volumes:
  smb_share:
    driver: local
    driver_opts:
      type: cifs
      device: //192.168.1.10/share
      o: "username=myuser,password=secret,uid=1000"
```

## NFS (Network File System)

NFS is the standard file-sharing protocol in Linux/Unix environments. It is common in HPC clusters, NAS devices, and [Kubernetes](../distributed-systems/kubernetes/ingress.md) persistent volumes.

### NFS versions

| Version | Notes |
|---|---|
| NFSv3 | Stateless, UDP or [TCP](../networking/tcp.md), no built-in auth |
| NFSv4 | Stateful, [TCP](../networking/tcp.md) only, Kerberos auth, ACLs |
| NFSv4.1 | Parallel NFS (pNFS) for high throughput |

### Mount an NFS share

```bash
# Install client
sudo apt install nfs-common

# Mount
sudo mount -t nfs 192.168.1.10:/exports/data /mnt/data

# Persistent mount (/etc/fstab)
192.168.1.10:/exports/data  /mnt/data  nfs  defaults,_netdev  0  0
```

### NFS server setup (Linux)

```bash
sudo apt install nfs-kernel-server

# /etc/exports
/exports/data  192.168.1.0/24(rw,sync,no_subtree_check)

sudo exportfs -ra
sudo systemctl restart nfs-kernel-server
```

### Python access (NFS mounted as local path)

Once an NFS share is mounted, Python treats it like any local directory:

```python
import os

NFS_MOUNT = "/mnt/data"

for fname in os.listdir(NFS_MOUNT):
    path = os.path.join(NFS_MOUNT, fname)
    with open(path, "rb") as f:
        data = f.read()
```

No special library needed — the OS handles the network transparently.

## Kubernetes Persistent Volumes

Both SMB and NFS are common backing stores for [Kubernetes](../distributed-systems/kubernetes/ingress.md) PVs:

```yaml
# NFS PersistentVolume
apiVersion: v1
kind: PersistentVolume
metadata:
  name: nfs-pv
spec:
  capacity:
    storage: 100Gi
  accessModes: [ReadWriteMany]
  nfs:
    server: 192.168.1.10
    path: /exports/data
```

```yaml
# SMB PersistentVolume (via CSI driver)
apiVersion: v1
kind: PersistentVolume
metadata:
  name: smb-pv
spec:
  capacity:
    storage: 50Gi
  accessModes: [ReadWriteMany]
  csi:
    driver: smb.csi.k8s.io
    volumeHandle: unique-id
    volumeAttributes:
      source: //192.168.1.10/share
    nodeStageSecretRef:
      name: smb-secret
      namespace: default
```

## Environment Variables

```bash
# .env
SMB_HOST=192.168.1.10
SMB_USER=myuser
SMB_PASSWORD=secret
SMB_SHARE=share
NFS_SERVER=192.168.1.10
NFS_EXPORT=/exports/data
```

## Security Considerations

| Concern | SMB | NFS |
|---|---|---|
| Auth | AD/Kerberos (strong); NTLM (legacy, avoid) | Host-based IP trust (weak) or Kerberos (NFSv4) |
| Encryption | SMB 3.0+ encrypts in transit | NFSv4.1 with Kerberos for encryption |
| Network exposure | Keep behind firewall / VPN | Never expose NFS to internet — host-trust only |
| Credential storage | Store in `.env` or secret manager | Server-side `/etc/exports` controls access |

## SMB / NFS vs Alternatives

| | SMB/NFS | [WebDAV](webdav.md) | SFTP | S3 / MinIO |
|---|---|---|---|---|
| Feels like | Local drive | Remote [HTTP](../networking/http.md) filesystem | Secure file transfer | [Object storage](../cloud/infrastructure/object-storage.md) API |
| Firewall | Blocked (ports 445/2049) | Open (80/443) | Open (22) | Open (443) |
| Internet-accessible | No (VPN required) | Yes | Yes | Yes |
| Throughput | Very high (LAN) | Moderate | Moderate | High (parallel) |
| Best for | LAN / on-prem / [Kubernetes](../distributed-systems/kubernetes/ingress.md) | Web-integrated file management | Secure transfers | Cloud / distributed apps |

## Related Concepts

- [WebDAV](./webdav.md) — [HTTP](../networking/http.md)-based file management, firewall-friendly
- [FTP / SFTP](./ftp-sftp.md) — secure file transfer over [SSH](ssh.md)
- [Object Storage / MinIO](../cloud/infrastructure/object-storage.md) — S3-compatible, internet-scale blob storage
