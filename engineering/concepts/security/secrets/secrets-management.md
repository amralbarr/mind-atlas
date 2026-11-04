# Secrets Management

A **secrets manager** is a dedicated system for storing, distributing, and rotating sensitive values — API keys, database passwords, [TLS](../../networking/tls.md) private keys, signing keys — instead of leaving them in `.env` files, hardcoded in source, or pasted into a [CI/CD](../../devops/ci-cd.md) dashboard's plaintext variable fields.

## Why Not Just Use Environment Variables?

Env vars are the most common starting point and are fine for local development, but they don't scale to a real production posture on their own:

| Problem with plain env vars | What a secrets manager adds |
|---|---|
| Visible to anything that can read the process/container's environment (a debugging tool, a crash dump, a compromised dependency) | Access is mediated per-request, through an auditable API, not a static blob sitting in memory |
| No rotation — changing a secret means redeploying everywhere it's set | Secrets can be rotated centrally; consumers fetch the current value rather than holding a static copy |
| No audit trail of who/what read a given secret | Every read is logged — who accessed which secret, when |
| Often the *same* secret is copy-pasted across many services/environments | Fine-grained, per-service/per-environment access policies |

Ad hoc tricks like `grep`-ing a single value out of a `.env` file (see [Bash & Shell Commands](../../../commands/bash.md#extracting-one-value-from-a-env-file-without-sourcing-it)) are fine for a quick local script, but they're not a substitute for real secrets management once there's more than one developer, environment, or service involved.

## Core Capabilities

- **Encrypted storage at rest**, with the secrets manager itself controlling the encryption keys.
- **Access policies** — which identity (a service, a CI pipeline, a human) can read which secret, often integrating with the platform's existing [access control / IAM](../authorization/access-control-iam.md).
- **Dynamic secrets** — some systems can generate a short-lived credential *on demand* (e.g. a database user that's created fresh and expires in an hour) rather than handing out one long-lived password to every consumer.
- **Leasing & automatic revocation** — a dynamically-issued secret has a lease; when the lease isn't renewed, the secrets manager can revoke the underlying credential itself, not just stop handing it out.
- **Audit logging** — a durable record of every access, which is often the actual regulatory/compliance requirement driving adoption in the first place.

## HashiCorp Vault → OpenBao

**HashiCorp Vault** was the dominant open-source secrets manager for years. In 2023, HashiCorp relicensed Vault (and its other tools) from the permissive MPL 2.0 to the more restrictive **Business Source License (BSL)** — which limits certain commercial/competitive uses. In response, a group of Vault's own contributors, under the **Linux Foundation**, forked the last MPL-licensed version into **[OpenBao](openbao.md)** — a drop-in-compatible, genuinely open-source continuation.

| | HashiCorp Vault | [OpenBao](openbao.md) |
|---|---|---|
| License | BSL (source-available, commercial-use restrictions) | MPL 2.0 (genuinely open source) |
| Governance | HashiCorp (a company) | Linux Foundation (vendor-neutral) |
| API/CLI compatibility | Original | Designed to stay compatible with Vault's API/CLI, so migration is low-friction |
| [Docker](../../containers/docker.md) image | `hashicorp/vault` | `openbao/openbao` |

Functionally the two are very similar — same core concepts (a KV secrets engine, dynamic secrets, policies, audit devices) — the split is a licensing/governance story more than a feature divergence, at least as of the fork. See [OpenBao](openbao.md) for hands-on installation, unsealing, and CLI/API usage.

## Other Common Options

| Tool | Notes |
|---|---|
| **[AWS](../../cloud/infrastructure/aws.md) Secrets Manager** / **[Azure](../../cloud/azure/azure.md) Key Vault** / **[GCP](../../cloud/infrastructure/gcp.md) Secret Manager** | Cloud-native, fully managed, tightly integrated with that provider's own IAM — the default choice if a system already lives entirely in one cloud |
| **SOPS** | Encrypts secrets *in files* (so they can live safely in Git) rather than running a live server — a good fit for GitOps workflows |
| **[Kubernetes](../../distributed-systems/kubernetes/ingress.md) Secrets** | Built into [Kubernetes](../../distributed-systems/kubernetes/ingress.md) itself, but base64-encoded rather than encrypted by default — commonly paired with Vault/[OpenBao](openbao.md) or a cloud KMS for real encryption at rest |

## Common Questions

**Is base64-encoding a secret in [Kubernetes](../../distributed-systems/kubernetes/ingress.md) the same as encrypting it?**
> No — base64 is an encoding, not encryption; anyone with read access to that [Kubernetes](../../distributed-systems/kubernetes/ingress.md) object can trivially decode it. [Kubernetes](../../distributed-systems/kubernetes/ingress.md) Secrets need to be paired with encryption at rest (etcd encryption, or an external secrets manager) to actually be protected.

**When is a full secrets manager overkill compared to just using a cloud provider's built-in option?**
> If a system runs entirely within one cloud provider, that provider's native secrets service is usually simpler to operate and sufficiently capable. A dedicated tool like Vault/[OpenBao](openbao.md) earns its complexity in multi-cloud, on-prem, or hybrid setups, or when dynamic/short-lived credentials are specifically needed.

## Related

- [OpenBao](openbao.md)
- [Access Control & IAM](../authorization/access-control-iam.md)
- [Docker](../containers/docker.md)
- [Azure](../cloud/azure.md)
- [JWT](../auth/jwt.md)
