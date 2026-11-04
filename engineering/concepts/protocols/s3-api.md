# S3 API

The S3 API is the [HTTP](../networking/http.md) [REST](../backend/api/rest.md) interface originally created by Amazon for S3 (Simple Storage Service). It has become the **de facto standard** for [object storage](../cloud/infrastructure/object-storage.md) — every major object store (MinIO, Backblaze B2, Cloudflare R2, Wasabi, DigitalOcean Spaces, Ceph) implements it, so client code written against the S3 API works against all of them by changing the endpoint URL.

## Core Concepts

| Term | Meaning |
|---|---|
| **Bucket** | Top-level namespace (like a root folder) |
| **Object** | A stored file — key + binary data + metadata |
| **Key** | The object's name within a bucket (can contain `/` to simulate folders) |
| **Metadata** | Arbitrary key-value pairs attached to an object |
| **Presigned URL** | A time-limited URL granting temporary access to a private object |
| **Region** | Geographic location of the bucket ([AWS](../cloud/infrastructure/aws.md) concept; self-hosted stores often ignore this) |

## Authentication

S3 uses **[HMAC](../security/secrets/hmac.md)-SHA256 request signing** ([AWS](../cloud/infrastructure/aws.md) Signature Version 4). Every request is signed with an access key + secret key. You never send the secret key over the wire — it is used to compute a signature that the server verifies.

```
Authorization: AWS4-HMAC-SHA256 Credential=<access-key>/..., SignedHeaders=..., Signature=<hmac>
```

All S3 client libraries (boto3, awscli, etc.) handle signing automatically.

## Common Operations

| Operation | [HTTP](../networking/http.md) Method | Notes |
|---|---|---|
| List buckets | `GET /` | |
| Create bucket | `PUT /<bucket>` | |
| List objects | `GET /<bucket>?list-type=2` | |
| Upload object | `PUT /<bucket>/<key>` | |
| Download object | `GET /<bucket>/<key>` | |
| Delete object | `DELETE /<bucket>/<key>` | |
| Copy object | `PUT` with `x-amz-copy-source` header | |
| Get object metadata | `HEAD /<bucket>/<key>` | |
| Presigned URL | Signed `GET` URL with expiry | |
| Multipart upload | Initiate → upload parts → complete | For large files (>100 MB) |

## Python Client (`boto3`)

```bash
pip install boto3
```

### Connect (works for AWS, MinIO, R2, any S3-compatible store)

```python
import boto3
import os
from dotenv import load_dotenv

load_dotenv()

s3 = boto3.client(
    "s3",
    endpoint_url=os.getenv("S3_ENDPOINT_URL"),        # omit for AWS; set for self-hosted
    aws_access_key_id=os.getenv("S3_ACCESS_KEY"),
    aws_secret_access_key=os.getenv("S3_SECRET_KEY"),
    region_name=os.getenv("S3_REGION", "us-east-1"),
)
```

### Bucket operations

```python
# Create bucket
s3.create_bucket(Bucket="my-bucket")

# List buckets
resp = s3.list_buckets()
for b in resp["Buckets"]:
    print(b["Name"])

# Delete bucket (must be empty first)
s3.delete_bucket(Bucket="my-bucket")
```

### Object operations

```python
# Upload a file
s3.upload_file("local.pdf", "my-bucket", "reports/local.pdf")

# Upload from bytes / file-like object
s3.put_object(Bucket="my-bucket", Key="data.json", Body=b'{"key": "value"}')

# Download a file
s3.download_file("my-bucket", "reports/local.pdf", "downloaded.pdf")

# Download to bytes
resp = s3.get_object(Bucket="my-bucket", Key="data.json")
content = resp["Body"].read()

# List objects
resp = s3.list_objects_v2(Bucket="my-bucket", Prefix="reports/")
for obj in resp.get("Contents", []):
    print(obj["Key"], obj["Size"])

# Delete object
s3.delete_object(Bucket="my-bucket", Key="reports/old.pdf")

# Copy object
s3.copy_object(
    Bucket="my-bucket",
    CopySource={"Bucket": "my-bucket", "Key": "reports/old.pdf"},
    Key="archive/old.pdf",
)
```

### Presigned URLs (temporary access without credentials)

```python
# Generate a presigned download URL (valid for 1 hour)
url = s3.generate_presigned_url(
    "get_object",
    Params={"Bucket": "my-bucket", "Key": "reports/report.pdf"},
    ExpiresIn=3600,
)
print(url)  # share this URL — no auth required

# Generate a presigned upload URL
url = s3.generate_presigned_url(
    "put_object",
    Params={"Bucket": "my-bucket", "Key": "uploads/file.pdf", "ContentType": "application/pdf"},
    ExpiresIn=900,
)
# Client PUTs directly to this URL — server never touches the file
```

### Object metadata

```python
# Set metadata on upload
s3.put_object(
    Bucket="my-bucket",
    Key="doc.pdf",
    Body=data,
    Metadata={"author": "alice", "department": "finance"},
    ContentType="application/pdf",
)

# Read metadata (HEAD request — no body download)
resp = s3.head_object(Bucket="my-bucket", Key="doc.pdf")
print(resp["Metadata"])
print(resp["ContentLength"])
print(resp["LastModified"])
```

### Multipart upload (large files)

```python
# boto3 handles multipart automatically for upload_file > 8MB
s3.upload_file(
    "large_video.mp4",
    "my-bucket",
    "videos/large_video.mp4",
    Config=boto3.s3.transfer.TransferConfig(multipart_threshold=8 * 1024 * 1024),
)
```

## Environment Variables

```bash
# .env

# AWS S3
S3_ACCESS_KEY=AKIAIOSFODNN7EXAMPLE
S3_SECRET_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
S3_REGION=eu-west-1
# S3_ENDPOINT_URL=  (leave unset for AWS)

# MinIO / self-hosted
S3_ENDPOINT_URL=http://localhost:9000
S3_ACCESS_KEY=minioadmin
S3_SECRET_KEY=minioadmin
S3_REGION=us-east-1
```

## Bucket Policies & ACLs

Buckets can be public or private. Access is controlled by:
- **Bucket Policy** — [JSON](../programming/fundamentals/json.md) document attached to the bucket ([IAM](../security/authorization/access-control-iam.md)-style rules)
- **ACLs** — per-object access control (legacy; bucket policies preferred)

Example: make a bucket publicly readable

```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Principal": "*",
    "Action": "s3:GetObject",
    "Resource": "arn:aws:s3:::my-public-bucket/*"
  }]
}
```

```python
import json
s3.put_bucket_policy(
    Bucket="my-public-bucket",
    Policy=json.dumps(policy),
)
```

## S3-Compatible Stores

| Store | Endpoint pattern | Notes |
|---|---|---|
| [AWS](../cloud/infrastructure/aws.md) S3 | *(omit endpoint_url)* | Reference implementation |
| MinIO | `http://localhost:9000` | Self-hosted, [Docker](../containers/docker.md)-ready |
| Cloudflare R2 | `https://<account>.r2.cloudflarestorage.com` | No egress fees |
| Backblaze B2 | `https://s3.<region>.backblazeb2.com` | Cheap storage |
| Ceph | `http://<ceph-gateway>` | On-prem, enterprise |
| DigitalOcean Spaces | `https://<region>.digitaloceanspaces.com` | Managed |

All use the same boto3 client — only `endpoint_url` and credentials differ.

## S3 API vs Alternatives

| | S3 API | [WebDAV](webdav.md) | SFTP | SMB/NFS |
|---|---|---|---|---|
| Transport | [HTTPS](../networking/https.md) | [HTTPS](../networking/https.md) | [SSH](ssh.md) | [TCP](../networking/tcp.md) (LAN) |
| Auth | [HMAC](../security/secrets/hmac.md) signing | Basic/Bearer | Password/Key | AD/host-based |
| Firewall | Open (443) | Open (443) | Open (22) | Blocked |
| Scale | Unlimited (object store) | Limited (file server) | Limited | LAN only |
| Best for | Cloud / distributed apps | File management UIs | Secure transfers | On-prem LAN sharing |

## Related Concepts

- [HMAC](../security/secrets/hmac.md) — the keyed-hash mechanism behind [AWS](../cloud/infrastructure/aws.md) Signature Version 4 request signing
- [Access Control & IAM](../security/authorization/access-control-iam.md) — the general framework bucket policies implement
- [Object Storage / MinIO](../cloud/infrastructure/object-storage.md) — MinIO setup, [Docker](../containers/docker.md), and Python examples
- [WebDAV](./webdav.md) — [HTTP](../networking/http.md)-based file management for document servers
- [FTP / SFTP](./ftp-sftp.md) — legacy and secure file transfer
- [SMB / NFS](./smb-nfs.md) — LAN network file sharing
