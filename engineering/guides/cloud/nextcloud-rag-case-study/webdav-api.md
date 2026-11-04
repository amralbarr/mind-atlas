# WebDAV API

## What is WebDAV?

[WebDAV](../../../concepts/protocols/webdav.md) (Web Distributed Authoring and Versioning) is an extension of the [HTTP](../../../concepts/networking/http.md) protocol that allows clients to read, write, and manage files on a remote server over the web. It is the primary way external applications access files stored in Nextcloud — like a remote file system accessible over [HTTPS](../../../concepts/networking/https.md).

Nextcloud exposes a [WebDAV](../../../concepts/protocols/webdav.md) endpoint that allows the AI pipeline to:
- List all files in a folder
- Download file content
- Read file metadata (name, size, last modified)

## Nextcloud WebDAV Endpoint

```
https://<your-nextcloud-host>/remote.php/dav/files/<username>/
```

Example for user `admin`:
```
https://nextcloud.example.com/remote.php/dav/files/admin/Finance/Q3_Report.pdf
```

## Authentication

[WebDAV](../../../concepts/protocols/webdav.md) uses [HTTP](../../../concepts/networking/http.md) Basic [Authentication](../../../concepts/security/auth/authentication.md):
- Username: Nextcloud username
- Password: Nextcloud password (or app password — recommended)

**App Password:** A separate password generated in Nextcloud settings specifically for API access. Safer than using the main user password because it can be revoked without changing the user's login.

## Common WebDAV Operations

```python
import requests
from requests.auth import HTTPBasicAuth

BASE_URL = "https://nextcloud.example.com/remote.php/dav/files/admin"
AUTH = HTTPBasicAuth("admin", "app-password-here")

# List files in a folder (PROPFIND request)
response = requests.request(
    "PROPFIND",
    f"{BASE_URL}/Finance/",
    auth=AUTH,
    headers={"Depth": "1"}
)

# Download a file (GET request)
response = requests.get(
    f"{BASE_URL}/Finance/Q3_Report.pdf",
    auth=AUTH
)
file_content = response.content

# Check if a file exists (HEAD request)
response = requests.head(
    f"{BASE_URL}/Finance/Q3_Report.pdf",
    auth=AUTH
)
exists = response.status_code == 200
```

## Nextcloud OCS API

In addition to [WebDAV](../../../concepts/protocols/webdav.md), Nextcloud provides a [REST](../../../concepts/backend/api/rest.md) API called **OCS API** for administrative operations:

| Operation | Endpoint |
|---|---|
| Get user info | `GET /ocs/v1.php/cloud/users/{userid}` |
| Get user's groups | `GET /ocs/v1.php/cloud/users/{userid}/groups` |
| List users | `GET /ocs/v1.php/cloud/users` |
| Share info | `GET /ocs/v2.php/apps/files_sharing/api/v1/shares` |

The OCS API is used in the permission-aware retrieval flow to look up which groups a user belongs to:

```python
def get_user_groups(username: str) -> list[str]:
    response = requests.get(
        f"{NEXTCLOUD_URL}/ocs/v1.php/cloud/users/{username}/groups",
        auth=ADMIN_AUTH,
        headers={"OCS-APIRequest": "true"},
        params={"format": "json"}
    )
    return response.json()["ocs"]["data"]["groups"]

# Example result:
# get_user_groups("alice") → ["Finance", "Projects"]
```

## Security Considerations

- Always use [HTTPS](../../../concepts/networking/https.md) — never [HTTP](../../../concepts/networking/http.md) — to prevent credentials from being transmitted in plaintext
- Use app passwords, not the user's main password, for API access
- The AI service should use a **read-only service account** with access only to the documents it needs to index
- API credentials must be stored in the `.env` file, never hardcoded in source code

## How it fits in this project

The [WebDAV](../../../concepts/protocols/webdav.md) API is used by Member 1 (Computer Science) in `ai/ingestion/` to pull documents from Nextcloud for indexing. The OCS API is used by the permission-aware retrieval layer to look up the current user's group memberships at query time. Both require valid Nextcloud credentials stored securely in the environment configuration.

## Related

- [Nextcloud](nextcloud.md)
- [Access Control & IAM](../../../concepts/security/authorization/access-control-iam.md)
- [Document Indexing](../../../concepts/ai/ingestion/document-indexing.md)
