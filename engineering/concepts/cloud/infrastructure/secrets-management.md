# Secrets Management — Azure Key Vault and AWS Secrets Manager

A secrets manager is a secure, centralized store for sensitive configuration values — API keys, database passwords, [TLS](../../networking/tls.md) certificates, encryption keys — that should never be hardcoded in source code, environment files, or container images.

The core problem: applications need credentials to function, but those credentials must not be visible in version control, logs, or deployment artifacts. A secrets manager is the bridge between "the app needs a value" and "only authorized identities can retrieve it."

---

## The Problem Without a Secrets Manager

```
# What developers do without one (all of these are wrong):
DATABASE_URL=postgres://user:password123@db.internal:5432/prod   # .env committed to git
docker run -e DB_PASS=password123 ...                            # visible in shell history
const apiKey = "sk-abc123..."                                    # hardcoded in source
```

Any of these leaks the secret to anyone with repo access, shell history, or a [Docker](../../containers/docker.md) inspect.

---

## Azure Key Vault

Microsoft's managed secrets, keys, and certificates service. Three distinct stores in one service:

| Store type | Holds |
|---|---|
| **Secrets** | Arbitrary string values — connection strings, API keys, passwords |
| **Keys** | Cryptographic keys (RSA, EC) — used for encrypt/decrypt, sign/verify operations; the key material never leaves Key Vault |
| **Certificates** | [TLS](../../networking/tls.md)/SSL certificates with automatic renewal |

### Retrieving a Secret at Runtime

```python
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

credential = DefaultAzureCredential()   # uses managed identity in Azure, local auth in dev
client = SecretClient(
    vault_url="https://my-vault.vault.azure.net/",
    credential=credential,
)

secret = client.get_secret("database-connection-string")
db_url = secret.value   # use it, never log it
```

`DefaultAzureCredential` tries a chain of identity sources in order: managed identity → environment variables → [Azure](../azure/azure.md) CLI → VS Code → developer fallback. In production on [Azure](../azure/azure.md) (App Service, AKS, [Azure Functions](../azure/azure-functions.md)), it automatically uses the assigned managed identity — no credentials required to retrieve credentials.

### Access Control

Key Vault uses [Azure RBAC](../azure/azure-rbac.md). Common built-in roles:

| Role | Can do |
|---|---|
| `Key Vault Secrets User` | Read secret values |
| `Key Vault Secrets Officer` | Read, write, delete secrets |
| `Key Vault Administrator` | Full control including access policy changes |

In practice: your application's managed identity gets `Key Vault Secrets User`. No developer has `Key Vault Secrets Officer` in production.

### Secret Versioning

Every update creates a new version. The current version is always accessed by name. Old versions remain accessible by version ID — critical for rollback:

```
secret: database-connection-string
  versions:
    abc123  (current) ← get_secret("database-connection-string") returns this
    def456  (previous)
    ghi789  (older)
```

### Soft Delete and Purge Protection

By default, deleted secrets enter a soft-delete state (recoverable for 90 days). Purge protection prevents permanent deletion during that window — even by administrators. Enable both in production.

---

## AWS Secrets Manager

[AWS](aws.md)'s managed secrets service. Functionally equivalent to [Azure](../azure/azure.md) Key Vault Secrets (string values only — no cryptographic key operations; those go to [AWS](aws.md) KMS).

### Retrieving a Secret at Runtime

```python
import boto3
import json

client = boto3.client("secretsmanager", region_name="us-east-1")

response = client.get_secret_value(SecretId="prod/myapp/database")
secret = json.loads(response["SecretString"])
db_url = f"postgres://{secret['username']}:{secret['password']}@{secret['host']}/mydb"
```

On [AWS](aws.md) (EC2, ECS, Lambda), the SDK automatically uses the instance's IAM role — no access keys needed.

### Automatic Rotation

[AWS](aws.md) Secrets Manager has a built-in rotation engine. You attach a Lambda function that rotates the secret on a schedule:

```
Every 30 days:
  1. Secrets Manager calls your rotation Lambda
  2. Lambda generates new credentials in the database
  3. Lambda stores the new value in Secrets Manager
  4. Applications on next secret fetch get the new value
```

[Azure](../azure/azure.md) Key Vault supports rotation but requires more manual setup (Event Grid + [Azure](../azure/azure.md) Function).

### Secret Structure

[AWS](aws.md) stores secrets as [JSON](../../programming/fundamentals/json.md) by convention, allowing multiple values under one secret name:

```json
{
  "username": "app_user",
  "password": "generated-secure-password",
  "host": "db.internal.example.com",
  "port": 5432,
  "dbname": "production"
}
```

This keeps related credentials grouped — one IAM policy grants access to the whole database config rather than three separate secrets.

---

## Side-by-Side Comparison

| | [Azure](../azure/azure.md) Key Vault | [AWS](aws.md) Secrets Manager |
|---|---|---|
| Secrets | Yes | Yes |
| Cryptographic keys | Yes (HSM-backed) | No — use [AWS](aws.md) KMS |
| Certificates | Yes (with auto-renewal) | No |
| Auto rotation | Manual setup | Built-in (Lambda-based) |
| Identity | Managed Identity + [RBAC](../../security/authorization/rbac.md) | IAM roles |
| SDK auth in cloud | DefaultAzureCredential | IAM instance role (automatic) |
| Local dev auth | [Azure](../azure/azure.md) CLI / VS Code plugin | [AWS](aws.md) CLI profile |
| Pricing model | Per operation + per key | Per secret per month + API calls |
| Equivalent of the other | Key Vault + Managed Identity | Secrets Manager + KMS + ACM |

---

## What Never to Store in a Secrets Manager

| Fits | Does not fit |
|---|---|
| Database passwords | User passwords (store hashed in DB) |
| External API keys | Session tokens (store in Redis/cache) |
| Service-to-service credentials | Feature flags (use LaunchDarkly/etc.) |
| [TLS](../../networking/tls.md) private keys | Large binary blobs (use [object storage](object-storage.md)) |
| Signing secrets ([JWT](../../security/auth/jwt.md)) | Non-sensitive config (use env vars or app config) |

---

## Injecting Secrets Into Applications

Three patterns, in order of preference:

**1. SDK at runtime (best)** — application fetches the secret on startup or per request. Supports rotation without restart.

```python
secret = client.get_secret("db-password").value
```

**2. Init container / sidecar** — a sidecar writes secrets to a tmpfs volume at pod start. Application reads from a local file. No SDK dependency in the app.

```yaml
# Kubernetes: Azure Key Vault Provider for Secrets Store CSI Driver
volumes:
  - name: secrets
    csi:
      driver: secrets-store.csi.k8s.io
      readOnly: true
      volumeAttributes:
        secretProviderClass: azure-keyvault-secrets
```

**3. Environment variable injection** — least preferred. Secrets land in the process environment, visible via `/proc/*/environ` on Linux. Acceptable for non-critical secrets; avoid for high-value credentials.

---

## Local Development Pattern

In production, the application uses managed identity. In development, `DefaultAzureCredential` ([Azure](../azure/azure.md)) or the AWS CLI profile (AWS) provides the same SDK calls against a real vault — no `.env` files with real credentials needed.

For fully local development without cloud access, use a local secrets file that is `.gitignore`d:

```
.secrets.local.json   ← real values, never committed
.secrets.example.json ← placeholder keys, committed as documentation
```

---

## Related

- [JWT](../../security/auth/jwt.md) — signing secrets (JWT_SECRET) are a primary secrets manager use case
- [Multi-Tenancy](../../backend/architecture/multi-tenancy.md) — per-tenant database credentials stored in Key Vault, looked up by tenant ID at runtime
- [Azure Blob Storage](../azure/azure-blob-storage.md) — storage account keys are managed through Key Vault, not hardcoded
- [OpenFGA](../../security/authorization/openfga.md) — the store connection credentials come from a secrets manager, not config files
