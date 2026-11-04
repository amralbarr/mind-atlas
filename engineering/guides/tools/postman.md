# Postman

## What Is It?

Postman is a GUI tool for sending [HTTP](../../concepts/networking/http.md) requests and inspecting responses. It is the standard tool for testing [REST](../../concepts/backend/api/rest.md) APIs, [WebDAV](../../concepts/protocols/webdav.md) endpoints, and any web service — without writing code. You can save requests into collections, set environment variables (like base URLs and auth tokens), and share collections with teammates.

## Install

| OS | Method |
|---|---|
| Windows | Download from https://www.postman.com/downloads/ |
| Mac | Download from https://www.postman.com/downloads/ |
| Linux | Download `.tar.gz` or use Snap: `snap install postman` |

No account is required for basic use — skip the sign-in prompt if you prefer.

## Core Concepts

| Concept | What it means |
|---|---|
| Request | A single [HTTP](../../concepts/networking/http.md) call: method (GET/POST/PUT/DELETE) + URL + headers + body |
| Collection | A folder of saved requests — share with the team by exporting as [JSON](../../concepts/programming/fundamentals/json.md) |
| Environment | A set of variables (e.g., `{{base_url}}`, `{{token}}`) that swap values per environment |
| Response | The server's reply: status code, headers, and body |

## Making a Request

1. Click **New** → **[HTTP](../../concepts/networking/http.md) Request**
2. Select the method (GET, POST, PUT, DELETE, PROPFIND…)
3. Enter the URL
4. Add headers under the **Headers** tab
5. Add a body under the **Body** tab (select **raw** + **[JSON](../../concepts/programming/fundamentals/json.md)** for [JSON](../../concepts/programming/fundamentals/json.md) APIs)
6. Click **Send**

## WebDAV Requests (Nextcloud)

[WebDAV](../../concepts/protocols/webdav.md) uses [HTTP](../../concepts/networking/http.md) methods not in the standard dropdown. Type them manually.

**List files in a folder (PROPFIND):**
```
Method: PROPFIND
URL:    http://<server-ip>/remote.php/dav/files/<username>/
Headers:
  Authorization: Basic <base64(username:password)>
  Depth: 1
```

**Download a file (GET):**
```
Method: GET
URL:    http://<server-ip>/remote.php/dav/files/<username>/Documents/report.pdf
Headers:
  Authorization: Basic <base64(username:password)>
```

**Generate the Basic Auth header in Postman:**
- Under the **[Authorization](../../concepts/security/authorization/authorization.md)** tab → Type: **Basic Auth**
- Enter username and password — Postman encodes it automatically

## OCS API Requests (Nextcloud User Management)

**Get groups a user belongs to:**
```
Method: GET
URL:    http://<server-ip>/ocs/v2.php/cloud/users/<username>/groups
Headers:
  Authorization: Basic <base64(admin:password)>
  OCS-APIRequest: true
```

**List all users:**
```
Method: GET
URL:    http://<server-ip>/ocs/v2.php/cloud/users
Headers:
  Authorization: Basic <base64(admin:password)>
  OCS-APIRequest: true
```

## REST API Requests (AI Service)

**Query the [RAG](../../concepts/ai/rag/rag.md) search endpoint:**
```
Method: POST
URL:    http://localhost:5000/search
Headers:
  Content-Type: application/json
Body (raw JSON):
{
  "query": "What is the vacation policy?",
  "username": "alice"
}
```

## Environment Variables

Set variables once, reuse across all requests:

1. Click **Environments** (top right) → **New Environment**
2. Add variables:

| Variable | Example Value |
|---|---|
| `base_url` | `http://20.10.30.40` |
| `nc_user` | `admin` |
| `nc_password` | `yourpassword` |

3. In requests, reference them as `{{base_url}}`, `{{nc_user}}`

## Export and Share a Collection

1. Right-click a collection → **Export**
2. Save as [JSON](../../concepts/programming/fundamentals/json.md)
3. Commit to the repo under `docs/postman/` so teammates can import it

## Tips

- Use environments to switch between local (`localhost`) and production (`server-ip`) without editing URLs
- Save every request you test — collections become living API documentation
- Use the **Tests** tab to write assertions that automatically verify response status and body
- The VS Code extension **[REST](../../concepts/backend/api/rest.md) Client** is a lightweight alternative for quick one-off requests

## Related

- [VS Code](vscode.md)
- [Git & GitHub Basics](../git/git-github-basics.md)
