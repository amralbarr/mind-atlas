# Authorization

**Authorization** answers the question [authentication](../auth/authentication.md) deliberately leaves open: given a verified identity, **what is that identity allowed to do?** Authorization always runs *after* [authentication](../auth/authentication.md) — there's no meaningful permission check against an identity that hasn't first been verified — and it's checked again, independently, for every protected action or resource, not just once at login.

## Authentication vs. Authorization

| | [Authentication](../auth/authentication.md) | Authorization |
|---|---|---|
| **Question** | Who are you? | What are you allowed to do? |
| **Checked against** | Credentials (password, token signature, biometric) | Permissions/roles/policies |
| **Happens** | First, once per session/request | After [authentication](../auth/authentication.md), per action/resource |
| **Failure result** | 401 Unauthorized (identity not established) | 403 Forbidden (identity known, action denied) |
| **Example mechanisms** | Password login, [JWT](../auth/jwt.md), [OAuth](../auth/oauth-scopes.md) | [RBAC](rbac.md), [CASL](casl.md), [OpenFGA](openfga.md) |

The bouncer-at-the-door analogy: [authentication](../auth/authentication.md) confirms you're really you; authorization is the staff deciding which rooms your ticket actually lets you into once you're inside. A fully authenticated user can still be correctly denied access to a specific resource — that denial is authorization working as intended, not a bug.

## The Three Major Authorization Models

Different systems need fundamentally different granularity of permission, and this handbook covers three distinct models for it — see the [full comparison overview](../../../overviews/security/authorization-models.md) for the complete decision guide:

| Model | Core question | Granularity | Best for |
|---|---|---|---|
| **[RBAC](rbac.md)** (Role-Based Access Control) | What role does this user have? | Coarse — role → fixed permission set | Internal tools, admin panels, clear role boundaries |
| **[CASL](casl.md)** | Can this user do X on this specific record? | Medium — ability + field-level conditions in code | Ownership rules within a single service |
| **[OpenFGA](openfga.md)** | Does this user have relation Y to object Z? | Fine — per-object, relationship-based tuples | Document sharing, multi-tenant SaaS, cross-service auth |

Simpler systems often start with [RBAC](rbac.md) and only reach for [CASL](casl.md) or [OpenFGA](openfga.md) once permissions stop being expressible as a fixed role→permission table — e.g. once "can edit this specific document" depends on who created it, who it's shared with, or which department it belongs to, rather than purely on the requester's role.

## Other Authorization Mechanisms in This Handbook

- **[POSIX ACLs](posix-acls.md)** — per-file/directory permission bits, the filesystem-level authorization model (used by [ADLS](../../cloud/azure/adls.md), Linux filesystems)
- **[Azure RBAC](../../cloud/azure/azure-rbac.md)** — [Azure](../../cloud/azure/azure.md)'s own concrete implementation of role-based authorization at the cloud-resource level
- **[Policy-Based Authorization](../../backend/data/policy-based-authorization.md)** — expressing authorization rules as externalized, declarative policy rather than hardcoded role checks

## The Principle of Least Privilege

Every identity — human or service — should hold the **minimum permissions required** to do its job, nothing more:

- A Finance user does not need HR document access → no HR permission granted
- A background indexing service account only needs read access → it should never be able to delete or modify files
- A database should not be reachable from the public internet → no public port, regardless of any application-level authorization in front of it

This principle shapes every authorization model above — it's the design goal [RBAC](rbac.md) roles, [CASL](casl.md) abilities, and [OpenFGA](openfga.md) tuples are all trying to express precisely, rather than granting broad access and hoping it's never misused.

## Authorization in Retrieval Pipelines (e.g. RAG)

Authorization doesn't stop at the API boundary — in an enterprise [RAG](../../ai/rag/rag.md) system it has to extend into the retrieval pipeline itself, or the [LLM](../../ai/generation/llm.md) can leak content the requesting user was never permitted to see:

```
Step 1: User authenticates (session or API token)                — Authentication
Step 2: System looks up the user's roles/group memberships        — Authorization context
Step 3: Retriever filters vector search results by allowed_groups — Authorization enforcement
Step 4: Only authorized document chunks are passed to the LLM
Step 5: LLM generates an answer from authorized content only
```

Critically, this filter must be pushed into the retrieval query itself (e.g. a metadata `where` clause in [pgvector](../../ai/retrieval/vector-database.md#metadata-filtering)/[Qdrant](../../ai/retrieval/vector-stores/qdrant.md)) rather than applied after fetching broadly — fetch-then-filter leaves a window where unauthorized content momentarily exists in application memory, and a bug in the later filtering step silently leaks it.

## Related

- [Authentication](../auth/authentication.md) — the prerequisite step: no authorization decision is meaningful without a verified identity to check it against
- [Access Control & IAM](access-control-iam.md) — the fuller framework (authN + authZ + audit) this file is one-third of
- [RBAC](rbac.md) — role-based, the coarsest and most common starting model
- [CASL](casl.md) — ability-based, record-level conditions within one service
- [OpenFGA](openfga.md) — relationship-based, fine-grained and cross-service
- [POSIX ACLs](posix-acls.md) — filesystem-level permission model
- [Authorization Models: RBAC vs CASL vs OpenFGA](../../../overviews/security/authorization-models.md) — the full decision framework across all three
- [Policy-Based Authorization](../../backend/data/policy-based-authorization.md)
- [Azure RBAC](../../cloud/azure/azure-rbac.md)
- [RAG](../../ai/rag/rag.md) — where authorization extends into the retrieval layer, not just the API boundary
