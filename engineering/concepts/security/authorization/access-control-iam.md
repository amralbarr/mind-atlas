# Access Control & IAM

## What is IAM?

IAM (Identity and Access Management) is the framework that controls **who can access what**. It answers three questions:
1. **[Authentication](../auth/authentication.md):** Who are you? (verify identity — login with username + password)
2. **[Authorization](authorization.md):** What are you allowed to do? (check permissions — can you read this file?)
3. **Audit:** What did you do? (log actions — who opened which file and when)

## Example Access Control Model: RBAC

A common approach is **Role-Based Access Control ([RBAC](rbac.md))**:
- Users are assigned to **groups** (roles)
- Groups are given permissions to **folders**
- Users inherit permissions from their groups

```
Organization
 │
 ├── Finance Group
 │    ├── alice (finance_user)
 │    ├── bob (finance_manager)
 │    └── Permissions: Read + Write to /Finance/ folder
 │
 ├── HR Group
 │    ├── carol (hr_user)
 │    └── Permissions: Read + Write to /HR/ folder
 │
 ├── Projects Group
 │    ├── dave (project_lead)
 │    └── Permissions: Read + Write to /Projects/ folder
 │
 └── Admin Group
      ├── admin
      └── Permissions: Read + Write to ALL folders
```

## Example Permission Matrix

| User                  | /Finance/ | /HR/ | /Projects/ | /Admin/ |
| --------------------- | --------- | ---- | ---------- | ------- |
| admin                 | RW        | RW   | RW         | RW      |
| alice (Finance)       | RW        | ❌    | R          | ❌       |
| bob (Finance Manager) | RW        | ❌    | R          | ❌       |
| carol (HR)            | ❌         | RW   | R          | ❌       |
| dave (Projects)       | ❌         | ❌    | RW         | ❌       |

R = Read only | RW = Read + Write | ❌ = No access

## Granular Permission Levels

Many platforms (e.g. Nextcloud) support granular permissions for shared folders:

| Permission | What it allows          |
| ---------- | ----------------------- |
| **Read**   | View and download files |
| **Create** | Upload new files        |
| **Update** | Edit existing files     |
| **Delete** | Delete files            |
| **Share**  | Re-share with others    |

## Authentication Practices

- **Login:** Username + password via a web interface or API
- **Brute-force protection:** Throttle and block IPs/accounts that fail login repeatedly
- **App passwords / API tokens:** Separate credentials for API/app access (never expose the user's main password)
- **Session timeout:** Sessions expire after inactivity (configurable)
- **[HTTPS](../../networking/https.md) enforcement:** All traffic must use [HTTPS](../../networking/https.md) — [HTTP](../../networking/http.md) should redirect to [HTTPS](../../networking/https.md)
- **Multi-factor [authentication](../auth/authentication.md) (MFA):** A one-time password ([OTP](../auth/otp.md)) or authenticator app adds a second factor beyond the password — see [One-Time Passwords (OTP)](../auth/otp.md)

## The Principle of Least Privilege

Every user and service should have the **minimum permissions required** to do their job:
- A Finance user does not need access to HR documents → no HR permission
- A background/indexing service account only needs **read** access — it should never be able to delete or modify files
- The database should not be reachable from the Internet → no public port
- [SSH](../../protocols/ssh.md) access to a server should be restricted to specific IP addresses only

## Authorization in Retrieval Pipelines (e.g. RAG)

IAM concepts extend into AI/retrieval pipelines. When a user asks a question against a document corpus, the request should still respect the same access boundaries:

```
Step 1: User authenticates (session or API token)
Step 2: System looks up user's group memberships
Step 3: Retriever filters vector search results by allowed_groups
Step 4: Only authorized document chunks are passed to the LLM
Step 5: LLM generates an answer from authorized content only
```

This ensures an AI system cannot reveal information from documents the user is not permitted to read — even indirectly.

## Audit Logging

IAM is incomplete without audit logging. Key events to log:

| Event | Fields logged |
|---|---|
| User login | user, timestamp, IP, success/fail |
| File opened/downloaded | user, timestamp, file path, action |
| File uploaded | user, timestamp, file path |
| File deleted | user, timestamp, file path |
| Permission changed | admin, timestamp, target, old permission, new permission |
| Share created | user, timestamp, target user/group, file |
| Failed access attempt | user, timestamp, resource attempted |
| AI query | user, timestamp, question, documents retrieved |

## Real-World Example

In the [Nextcloud RAG case study](../../../guides/cloud/nextcloud-rag-case-study/nextcloud.md), access control is implemented with Nextcloud groups and folder permissions, a permission matrix, and a permission-aware retrieval layer that filters AI search results by the requesting user's group memberships — ensuring the AI cannot bypass access controls.

## Related

- [Authentication](../auth/authentication.md) — the "who are you" question this file's IAM model answers first
- [Authorization](authorization.md) — the "what can you do" question, with the full [RBAC](rbac.md)/[CASL](casl.md)/[OpenFGA](openfga.md) model comparison
- [One-Time Passwords (OTP)](../auth/otp.md)
- [Nextcloud](../../../guides/cloud/nextcloud-rag-case-study/nextcloud.md)
- [Ubuntu Server Setup](../../../guides/linux/ubuntu-server-setup.md)
- [JWT](../auth/jwt.md)
- [OAuth Scopes & Least-Privilege Tokens](../auth/oauth-scopes.md)
- [Policy-Based Authorization](../../backend/data/policy-based-authorization.md)
- [Multi-Tenancy & Tenant Isolation](../../backend/architecture/multi-tenancy.md)
- [Secrets Management](../secrets/secrets-management.md)
- [HMAC](../secrets/hmac.md) — request-signing auth, a different mechanism from identity-based IAM
- [Azure RBAC](../../cloud/azure/azure-rbac.md) — [Azure](../../cloud/azure/azure.md)'s concrete implementation of identity-based [authorization](authorization.md)
- [Microsoft Entra ID](../../cloud/azure/microsoft-entra-id.md) — the identity provider behind [Azure RBAC](../../cloud/azure/azure-rbac.md)
