# Microsoft Entra ID

**Microsoft Entra ID** (formerly **[Azure](azure.md) Active Directory / [Azure](azure.md) AD**) is Microsoft's cloud identity and access management service. It is the identity provider that underlies every [Azure](azure.md) sign-in and every [Azure RBAC](azure-rbac.md) role assignment — there is no such thing as an [Azure](azure.md) role assignment without an Entra ID identity behind it.

## What it provides

- **Identities**: user accounts, groups, service principals (app identities), and managed identities (identities automatically assigned to [Azure](azure.md) resources)
- **[Authentication](../../security/auth/authentication.md)**: sign-in, MFA, conditional access policies, single sign-on (SSO) across Microsoft 365, [Azure](azure.md), and third-party apps that support OIDC/SAML
- **Directory**: the tenant-wide store of users and groups that [Azure RBAC](azure-rbac.md), [Azure VPN Gateway](../remote-access/azure-vpn-gateway-point-to-site.md) (Entra ID auth), and other [Azure](azure.md) services all read from

## How it relates to Azure RBAC

Entra ID and [Azure](azure.md) [RBAC](../../security/authorization/rbac.md) are two different layers that are often confused because they're both "access control":

| | Microsoft Entra ID | [Azure RBAC](azure-rbac.md) |
|---|---|---|
| Layer | Identity — who exists, how they authenticate | [Authorization](../../security/authorization/authorization.md) — what an authenticated identity can do to a resource |
| Manages | Users, groups, service principals, sign-in policies | Role assignments (principal + role + scope) |
| Example | "Bob authenticates with his organizational account + MFA" | "Bob's group has `Contributor` on `nextcloud-rg`" |

In short: **Entra ID answers "who are you," [Azure](azure.md) [RBAC](../../security/authorization/rbac.md) answers "what can you do."** See [Azure RBAC](azure-rbac.md) for the [authorization](../../security/authorization/authorization.md) side.

## Groups as the standard access-management pattern

The common real-world pattern (used in this project's course setup) is:

1. Create an Entra ID **group** for a team (e.g. `nextcloud-team`)
2. Add team members as group members
3. Assign an [Azure RBAC](azure-rbac.md) role to the **group** at a resource-group scope, once
4. Managing access afterward means just adding/removing group members — no repeated per-user role assignments

```bash
# Create a group
az ad group create --display-name "nextcloud-team" --mail-nickname "nextcloud-team"

# Add a member
az ad group member add --group "nextcloud-team" --member-id <user-object-id>

# List members
az ad group member list --group "nextcloud-team" --output table
```

## Where Entra ID shows up beyond RBAC

- **[Azure Bastion](../remote-access/azure-bastion.md)** and the Azure Portal both gate access behind an Entra ID sign-in — this is what lets Bastion extend the same identity model to network-level VM access instead of relying on IP allowlisting
- **[Azure VPN Gateway Point-to-Site](../remote-access/azure-vpn-gateway-point-to-site.md)** supports Entra ID [authentication](../../security/auth/authentication.md) as an alternative to certificate-based auth
- **Just-in-time VM access** (Microsoft Defender for Cloud) checks the requesting user's [Azure RBAC](azure-rbac.md) permission — which in turn depends on their Entra ID identity — before opening any port

## OAuth2 / OIDC Tokens

When an application authenticates users through Entra ID, it receives [JWT](../../security/auth/jwt.md) tokens:

| Token | Purpose |
|---|---|
| **Access token** ([JWT](../../security/auth/jwt.md)) | Proves identity to the target resource (your API); contains `oid` (user object ID), `roles`, `groups` |
| **ID token** ([JWT](../../security/auth/jwt.md)) | Contains user profile claims for the client app; not sent to APIs |
| **Refresh token** | Long-lived, opaque; used to get new access tokens without re-login |

The access token is what a [FastAPI](../../programming/python/fastapi.md) or NestJS gateway validates — same [JWT](../../security/auth/jwt.md) mechanics as a self-issued token, but signed by Microsoft's key (validated via JWKS endpoint).

## How It Appears in an Enterprise RAG System

Entra ID provides the **identity layer** — who the user is and what groups/roles they belong to. The application then uses this identity to enforce document-level permissions.

```
User authenticates via Entra ID (OIDC)
    ↓
Entra ID issues a JWT access token
    ↓
Token contains: user_id, department, roles, group memberships
    ↓
RAG application extracts user context from JWT
    ↓
Application filters retrieval to documents the user is allowed to see
    ↓
LLM generates answer only from permitted documents
```

**Critical distinction:** Entra ID confirms who you are. It does NOT automatically know which documents you're allowed to read — that permission enforcement is the application's responsibility, applied at retrieval time.

## Managed Identities — Secrets-Free Service Auth

Instead of storing a client secret or [API key](../../security/auth/api-key.md) in app config, a Managed Identity lets Azure assign an automatic, auto-rotating identity to a service:

```python
from azure.identity import DefaultAzureCredential
from azure.search.documents import SearchClient

credential = DefaultAzureCredential()   # uses Managed Identity in Azure, dev credentials locally
client = SearchClient(endpoint=endpoint, index_name=index, credential=credential)
```

No secrets in environment variables, no rotation to manage. The standard pattern for any Azure service calling another Azure service.

## Entra ID vs Self-Hosted JWT

| | Microsoft Entra ID | Self-issued [JWT](../../security/auth/jwt.md) (e.g. in [FastAPI](../../programming/python/fastapi.md)) |
|---|---|---|
| Token issuer | Microsoft | Your own auth service |
| Token signing | Microsoft's RSA key (JWKS endpoint) | Your `SECRET_KEY` / RSA private key |
| User store | Entra ID directory | Your own database |
| MFA / SSO | Built-in | Build yourself or use a library |
| Enterprise integration | Native (M365, Teams, Azure) | Custom |
| Use case | Enterprise apps, Azure services | Self-hosted platforms, startups |

## Related Concepts

- [Azure RBAC](azure-rbac.md) — the [authorization](../../security/authorization/authorization.md) layer built on Entra ID identities
- [Azure Blob Storage](azure-blob-storage.md) — one of many Azure services authenticating via Entra ID / Managed Identity
- [Azure Bastion](../remote-access/azure-bastion.md) — network access gated by Entra ID sign-in
- [Azure AI Foundry](azure-ai-foundry.md) — the Azure AI platform that uses Entra ID for enterprise [RAG](../../ai/rag/rag.md) auth
- [JWT](../../security/auth/jwt.md) — the token format Entra ID issues
- [Access Token + Refresh Token Pattern](../../security/auth/access-refresh-tokens.md) — two-token session pattern
- [Access Control & IAM](../../security/authorization/access-control-iam.md) — general IAM concepts this specializes
- [Azure](azure.md) — platform overview
