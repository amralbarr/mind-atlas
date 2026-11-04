# OpenBao

OpenBao is an open-source secrets management server — a Linux Foundation-governed fork of HashiCorp Vault, created after Vault relicensed to the more restrictive BSL. See [Secrets Management](secrets-management.md) for the full Vault-vs-OpenBao licensing story and how it compares to other options (cloud-native secrets managers, SOPS, [Kubernetes](../../distributed-systems/kubernetes/ingress.md) Secrets). This note is the hands-on, tool-specific reference — installation, unsealing, and day-to-day CLI/API usage.

## Running It (Docker)

```bash
docker run -d --name openbao \
  --cap-add=IPC_LOCK \
  -p 8200:8200 \
  -e BAO_DEV_ROOT_TOKEN_ID=dev-root-token \
  openbao/openbao:latest server -dev
```

`-dev` mode auto-unseals and auto-configures a root token — convenient for local development, **never for production** (dev mode stores everything in memory, with no real durability or access hardening).

For anything real, run it with a persistent storage backend and go through the actual init/unseal flow below.

## Core Concepts

| Term | Meaning |
|---|---|
| **Seal / Unseal** | On startup, OpenBao's storage is encrypted and inaccessible ("sealed") until enough unseal keys are provided to reconstruct the master key — a deliberate safeguard so a stolen disk/backup alone can't be read |
| **Secrets engine** | A pluggable backend that stores or generates secrets — the simplest is `kv` (a plain key-value store); others generate *dynamic* secrets (e.g. a database engine that creates a short-lived DB user) |
| **Policy** | An HCL/[JSON](../../programming/fundamentals/json.md) document defining which paths a token may read/write — the actual [authorization](../authorization/authorization.md) mechanism |
| **Token** | The primary auth credential — every request is authenticated by a token tied to one or more policies |
| **Auth method** | How a client proves identity to get a token in the first place — tokens themselves, but also AppRole (for machines/services), OIDC, LDAP, [Kubernetes](../../distributed-systems/kubernetes/ingress.md) service accounts, and more |

## Initialize & Unseal (Production Mode)

```bash
bao operator init
# Outputs 5 unseal key shares and 1 initial root token — store these securely,
# they are shown exactly once.

bao operator unseal <key-share-1>
bao operator unseal <key-share-2>
bao operator unseal <key-share-3>
# Default threshold is 3 of 5 shares — no single operator can unseal it alone.

export BAO_TOKEN=<initial-root-token>
```

The root token should be used only to bootstrap real policies/auth methods, then revoked — day-to-day access should go through scoped tokens tied to least-privilege policies, not the root token.

## Enable a Secrets Engine & Store a Secret

```bash
bao secrets enable -path=secret kv-v2

bao kv put secret/myapp/database \
  username="app_user" \
  password="s3cr3t"

bao kv get secret/myapp/database
```

## Writing a Policy

```hcl
# read-only-myapp.hcl
path "secret/data/myapp/*" {
  capabilities = ["read"]
}
```

```bash
bao policy write read-only-myapp read-only-myapp.hcl

# Issue a token scoped to that policy
bao token create -policy="read-only-myapp"
```

## Reading a Secret via HTTP API

Since every CLI command is really a thin wrapper over OpenBao's [HTTP](../../networking/http.md) API, any service can fetch secrets directly:

```bash
curl \
  --header "X-Vault-Token: $BAO_TOKEN" \
  https://openbao.internal:8200/v1/secret/data/myapp/database
```

(The header name stays `X-Vault-Token` for API compatibility with Vault-based tooling — this is intentional, so existing Vault client libraries and integrations work against OpenBao largely unmodified.)

## Dynamic Secrets (Database Example)

Instead of a static, long-lived database password stored once, OpenBao can generate a fresh, short-lived credential per request:

```bash
bao secrets enable database

bao write database/config/my-postgres \
  plugin_name=postgresql-database-plugin \
  connection_url="postgresql://{{username}}:{{password}}@db.internal:5432/app" \
  allowed_roles="readonly"

bao write database/roles/readonly \
  db_name=my-postgres \
  creation_statements="CREATE ROLE \"{{name}}\" WITH LOGIN PASSWORD '{{password}}' VALID UNTIL '{{expiration}}'; GRANT SELECT ON ALL TABLES IN SCHEMA public TO \"{{name}}\";" \
  default_ttl="1h" \
  max_ttl="24h"

bao read database/creds/readonly
# Returns a brand-new username/password pair, valid for up to 1h,
# automatically revocable by OpenBao when the lease expires.
```

## Common Questions

**Is switching from HashiCorp Vault to OpenBao a big migration?**
> Generally low-friction for straightforward setups — OpenBao aims to stay API/CLI-compatible with the version of Vault it forked from, so most client integrations, [Terraform](../../cloud/iac/terraform.md) providers, and CLI scripts work with only the endpoint/binary name changed. Verify compatibility for any newer Vault-only features released after the fork point, since those won't exist in OpenBao unless separately implemented.

**Why does unsealing require multiple key shares instead of one password?**
> This is **Shamir's Secret Sharing** — splitting the master key into N shares where any K of them can reconstruct it, but fewer cannot. It means no single compromised operator (or single leaked key share) is enough to unseal the vault alone, which is a meaningfully stronger guarantee than a single master password.

## Related

- [Secrets Management](secrets-management.md)
- [Access Control & IAM](../authorization/access-control-iam.md)
- [Docker](../containers/docker.md)
- [curl Commands](../../../commands/curl.md)
