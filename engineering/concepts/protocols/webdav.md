# WebDAV

WebDAV (Web Distributed Authoring and Versioning) is an extension of [HTTP](../networking/http.md)/1.1 defined in [RFC 4918](https://www.rfc-editor.org/rfc/rfc4918). It adds file-system-like operations — create, read, update, delete, move, copy, lock — on top of the standard [HTTP](../networking/http.md) verbs, making a remote server behave like a network drive over the web.

## How It Extends HTTP

| Standard [HTTP](../networking/http.md) | Added by WebDAV |
|---|---|
| GET, POST, PUT, DELETE, HEAD | PROPFIND, PROPPATCH, MKCOL, COPY, MOVE, LOCK, UNLOCK |
| Read/write a single resource | List directories, read/write properties, manage collections |

WebDAV requests and responses use **XML bodies** for structured metadata (properties). A `PROPFIND` response, for example, is a `207 Multi-Status` XML document listing each resource and its properties.

## Core Methods

| Method | Purpose |
|---|---|
| `PROPFIND` | List a resource's properties (or a directory's children) |
| `PROPPATCH` | Set or remove properties on a resource |
| `MKCOL` | Create a collection (directory) |
| `COPY` | Copy a resource to a new URL |
| `MOVE` | Move / rename a resource |
| `LOCK` | Lock a resource to prevent concurrent edits |
| `UNLOCK` | Release a lock |
| `GET` | Download a file (standard [HTTP](../networking/http.md)) |
| `PUT` | Upload / overwrite a file (standard [HTTP](../networking/http.md)) |
| `DELETE` | Delete a file or collection (standard [HTTP](../networking/http.md)) |

## Request & Response Structure

### List a directory (`PROPFIND`)

```http
PROPFIND /files/reports/ HTTP/1.1
Host: dav.example.com
Depth: 1
Content-Type: application/xml

<?xml version="1.0"?>
<d:propfind xmlns:d="DAV:">
  <d:prop>
    <d:displayname/>
    <d:getcontentlength/>
    <d:getlastmodified/>
    <d:resourcetype/>
  </d:prop>
</d:propfind>
```

`Depth` header controls recursion:
- `0` — the resource itself only
- `1` — resource + immediate children
- `infinity` — full recursive tree (often disabled server-side for performance)

Response: `207 Multi-Status` with one `<response>` block per resource.

### Upload a file (`PUT`)

```http
PUT /files/reports/Q3.pdf HTTP/1.1
Host: dav.example.com
Content-Type: application/pdf
Content-Length: 204800

<binary content>
```

### Create a directory (`MKCOL`)

```http
MKCOL /files/reports/2025/ HTTP/1.1
Host: dav.example.com
```

## Authentication

WebDAV relies on standard [HTTP](../networking/http.md) [authentication](../security/auth/authentication.md) mechanisms:

| Method | Notes |
|---|---|
| **Basic Auth** | Credentials in `Authorization: Basic <base64>` header — only safe over [HTTPS](../networking/https.md) |
| **Digest Auth** | Challenge-response, avoids plaintext password — still use [HTTPS](../networking/https.md) |
| **Bearer Token** | OAuth2 / [JWT](../security/auth/jwt.md) — used by modern WebDAV servers (e.g. Nextcloud with OIDC) |
| **App Passwords** | Server-generated per-client tokens (Nextcloud, ownCloud) — revocable without changing the user's main password |

Always use **[HTTPS](../networking/https.md)** — WebDAV credentials in [HTTP](../networking/http.md) headers are trivially intercepted over plain HTTP.

## Python Client

### Using `requests` (low-level)

```python
import requests
from requests.auth import HTTPBasicAuth
import os
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv("WEBDAV_URL")          # e.g. https://dav.example.com/files/user/
AUTH = HTTPBasicAuth(
    os.getenv("WEBDAV_USER"),
    os.getenv("WEBDAV_PASSWORD"),
)

# List directory
resp = requests.request("PROPFIND", BASE_URL, auth=AUTH, headers={"Depth": "1"})
print(resp.status_code)  # 207

# Download a file
resp = requests.get(f"{BASE_URL}report.pdf", auth=AUTH)
with open("report.pdf", "wb") as f:
    f.write(resp.content)

# Upload a file
with open("report.pdf", "rb") as f:
    requests.put(f"{BASE_URL}report.pdf", data=f, auth=AUTH)

# Delete a file
requests.delete(f"{BASE_URL}report.pdf", auth=AUTH)

# Create a directory
requests.request("MKCOL", f"{BASE_URL}archive/", auth=AUTH)
```

### Using `webdavclient3` (high-level)

```bash
pip install webdavclient3
```

```python
from webdav3.client import Client
import os
from dotenv import load_dotenv

load_dotenv()

client = Client({
    "webdav_hostname": os.getenv("WEBDAV_URL"),
    "webdav_login":    os.getenv("WEBDAV_USER"),
    "webdav_password": os.getenv("WEBDAV_PASSWORD"),
})

client.list("/")                          # list root
client.download_file("/report.pdf", "local_report.pdf")
client.upload_file("local.pdf", "/archive/local.pdf")
client.mkdir("/archive/2025/")
client.move("/old.pdf", "/archive/old.pdf")
client.clean("/trash/old.pdf")           # delete
```

## Environment Variables

```bash
# .env
WEBDAV_URL=https://dav.example.com/remote.php/dav/files/myuser/
WEBDAV_USER=myuser
WEBDAV_PASSWORD=app-password-here
```

Never hardcode credentials — always load from environment.

## Parsing PROPFIND Responses

```python
import xml.etree.ElementTree as ET

NS = {"d": "DAV:"}

def parse_propfind(xml_text: str) -> list[dict]:
    root = ET.fromstring(xml_text)
    resources = []
    for response in root.findall("d:response", NS):
        href = response.findtext("d:href", namespaces=NS)
        props = response.find(".//d:prop", NS)
        resources.append({
            "href": href,
            "name": props.findtext("d:displayname", namespaces=NS),
            "size": props.findtext("d:getcontentlength", namespaces=NS),
            "modified": props.findtext("d:getlastmodified", namespaces=NS),
            "is_dir": props.find("d:resourcetype/d:collection", NS) is not None,
        })
    return resources
```

## Locking (Concurrent Edit Prevention)

WebDAV defines an optional locking mechanism to prevent write conflicts:

```http
LOCK /files/doc.txt HTTP/1.1
Timeout: Second-3600
Content-Type: application/xml

<?xml version="1.0"?>
<d:lockinfo xmlns:d="DAV:">
  <d:lockscope><d:exclusive/></d:lockscope>
  <d:locktype><d:write/></d:locktype>
  <d:owner><d:href>mailto:user@example.com</d:href></d:owner>
</d:lockinfo>
```

Response includes a `Lock-Token` header. Subsequent writes must include `If: (<lock-token>)`.

Most read-only clients (indexing pipelines, [RAG](../ai/rag/rag.md) ingestion) don't need locking.

## WebDAV Servers

| Server | Notes |
|---|---|
| **Nextcloud / ownCloud** | Full WebDAV + OCS API; [Docker](../containers/docker.md)-ready |
| **Apache mod_dav** | Built-in; simple file server use cases |
| **[Nginx](../backend/api-gateways/nginx.md) + davfs** | Lightweight; read-heavy workloads |
| **SabreDAV** | PHP library for building custom DAV servers |
| **MinIO** | S3-compatible object store — does NOT speak WebDAV natively |

## WebDAV vs Alternatives

| | WebDAV | FTP/SFTP | [S3 API](s3-api.md) | SMB/NFS |
|---|---|---|---|---|
| Protocol | HTTP extension | Separate protocol | HTTP [REST](../backend/api/rest.md) | Network filesystem |
| Auth | HTTP Basic/Bearer | User/key | [HMAC](../security/secrets/hmac.md) signatures | OS-level |
| Firewall-friendly | Yes (port 80/443) | Often blocked | Yes (443) | Often blocked |
| Browser-accessible | Yes | No | Via SDK | No |
| Best for | Web-integrated file management | Legacy file transfer | [Object storage](../cloud/infrastructure/object-storage.md) at scale | LAN file sharing |

## Security Checklist

- Use [HTTPS](../networking/https.md) — never plain HTTP
- Use app passwords or bearer tokens, not the user's main password
- Use read-only service accounts for ingestion pipelines
- Store credentials in `.env`, never in source code
- Restrict `Depth: infinity` PROPFIND at the server level to prevent enumeration abuse
- Set short lock timeouts to avoid stale locks blocking other clients

## Related Concepts

- [Object Storage / MinIO](../cloud/infrastructure/object-storage.md) — S3-compatible alternative to WebDAV for binary files
- [REST](../backend/api/rest.md) — WebDAV builds on HTTP/[REST](../backend/api/rest.md) conventions
- [Access Control & IAM](../security/authorization/access-control-iam.md) — [authentication](../security/auth/authentication.md) and permissions
- [Nextcloud WebDAV Guide](../../guides/cloud/nextcloud-rag-case-study/webdav-api.md) — project-specific usage with Nextcloud + OCS API
