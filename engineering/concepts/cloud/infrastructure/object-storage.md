# Object Storage

## What is it?

Object storage is a way to store files (images, videos, backups, documents) as **objects** rather than as files in a traditional folder/filesystem hierarchy or as rows in a database. Each object bundles the file's data together with an ID and metadata, instead of relying on a directory path.

Instead of:

```
/folder1/image.png
```

Object storage stores:

```
Object = {
  file: image.png,
  metadata: {...},
  unique_id: "abc123"
}
```

## What is MinIO?

MinIO is:

- An open-source object storage server
- Compatible with the **[AWS](aws.md) [S3 API](../../protocols/s3-api.md)**
- Something you can run yourself on your own server or VPS

Think of it as **your own private [AWS](aws.md) S3**.

## Key Concepts

### Bucket

A container that groups related objects, e.g. `bucket: user-uploads`.

### Object

The actual file, e.g. `user-uploads/profile.png`.

### Metadata

Extra information attached to an object:

```json
{
  "content-type": "image/png",
  "userId": "123"
}
```

## Why Use Object Storage?

| Use case | Why object storage (e.g. MinIO) fits |
|---|---|
| Images / videos | Scalable and fast |
| AI datasets | Large file support |
| Backups | Reliable, decoupled from the application |
| SaaS apps | Separates files from the database |

It's a good fit for AI-oriented systems in general: storing user uploads, documents for [RAG](../../ai/rag/rag.md) pipelines, generated images, and TTS audio output. It also integrates cleanly with [Docker](../../containers/docker.md), Node.js/NestJS backends, and Python AI pipelines.

## Example Usage (Node.js)

Install the client library:

```bash
npm install minio
```

Upload a file:

```js
import { Client } from "minio";

const minioClient = new Client({
  endPoint: "localhost",
  port: 9000,
  useSSL: false,
  accessKey: "minioadmin",
  secretKey: "minioadmin",
});

await minioClient.putObject(
  "uploads",
  "file.txt",
  "Hello from MinIO"
);
```

## Running MinIO with Docker

```bash
docker run -d \
  -p 9000:9000 \
  -p 9001:9001 \
  -e "MINIO_ROOT_USER=admin" \
  -e "MINIO_ROOT_PASSWORD=password123" \
  minio/minio server /data --console-address ":9001"
```

- API: `http://your-server:9000`
- Dashboard (Console): `http://your-server:9001`

## Working with MinIO Locally

You can view, upload, download, and sync files with MinIO — it isn't automatic like Dropbox, but a client/tool makes it close.

### 1. Access from the browser (easiest)

Open the dashboard at `http://your-server:9001` and log in with your root user/password. From there you can create buckets, upload files, download files, and browse folders.

### 2. Use the MinIO Client (`mc`) — best for sync

**Install (Windows, PowerShell):**
```bash
choco install minio-client
```

Or download manually from `https://min.io/download`.

**Connect to your server:**
```bash
mc alias set myminio http://localhost:9000 admin password123
```

**List buckets:**
```bash
mc ls myminio
```

### 3. Sync files (local ↔ MinIO)

Upload a local folder to MinIO:
```bash
mc mirror ./local-folder myminio/mybucket
```

Download from MinIO to local:
```bash
mc mirror myminio/mybucket ./local-folder
```

Real-time sync (auto-update, closest to Dropbox-like behavior):
```bash
mc mirror --watch ./local-folder myminio/mybucket
```

### 4. Mount as a drive (advanced)

Using `rclone`:
```bash
rclone config
# then:
rclone mount myminio:bucket X:
```

This makes the bucket appear as a drive on your PC.

### 5. Access from code

```js
const Minio = require('minio')

const client = new Minio.Client({
  endPoint: 'localhost',
  port: 9000,
  useSSL: false,
  accessKey: 'admin',
  secretKey: 'password123'
})
```

## Pricing Note (AWS S3)

As a rough reference point, [AWS](aws.md) S3 standard storage bills the first 50 TB/month at about **$0.025 per GB** — see [AWS S3 pricing](https://aws.amazon.com/s3/pricing/) for current, region-specific rates.

## Important Notes

**Use the correct URL.** If running locally, use `http://localhost:9000` (API) and `http://localhost:9001` (dashboard) — not a bare server hostname.

**Open ports if using a VPS.** Port 9000 is the API; port 9001 is the dashboard. Only expose what's needed, and prefer putting MinIO behind the same [NSG](../azure/networking-vnet-nsg.md)/firewall discipline used for other internal services.

## Summary

| Task | Tool |
|---|---|
| View files | Browser |
| Upload/download | Browser or `mc` |
| Sync folders | `mc mirror` |
| Mount as drive | `rclone` |
| Use in backend | MinIO SDK |

**Recommendation:** for AI pipelines and backend services, use `mc mirror --watch` for syncing datasets, the MinIO SDK inside your backend, and one bucket per pipeline for a clean structure.

## Related

- [Backup and Restore](backup-and-restore.md)
- [Microsoft Azure](azure.md)
- [Azure Networking: VNet & NSG](../azure/networking-vnet-nsg.md)
- [Docker](../containers/docker.md)
