# POSIX ACLs

POSIX ACLs (Access Control Lists) are the traditional Unix/Linux permission model, extended beyond the classic owner/group/everyone bits to grant fine-grained, per-user or per-group read/write/execute permissions on individual files and directories. [ADLS](../../cloud/azure/adls.md) is the handbook's main real-world example of this model applied to cloud [object storage](../../cloud/infrastructure/object-storage.md) rather than a local filesystem — it's one of the few cloud storage services that implements genuine POSIX-style ACLs at all.

## The model

Classic Unix permissions give you exactly three permission slots per file: owner, group, and everyone else — each with its own read/write/execute bits (`rwxr-xr--`, etc.). POSIX ACLs extend this to an arbitrary list of additional users and groups, each with their own independent permission set on the same file:

```
# Classic Unix permissions (3 fixed slots)
-rwxr-xr--  owner: alice (rwx)  group: engineering (r-x)  other: (r--)

# POSIX ACL (arbitrary additional entries on top)
-rwxr-xr--+ owner: alice (rwx)  group: engineering (r-x)  other: (r--)
  + user:bob:rwx
  + group:finance:r--
  + user:carol:---
```

The `+` at the end of the permission string is the conventional signal (on `ls -l`) that a file has additional ACL entries beyond the classic three slots.

## Permission bits

| Bit | On a file | On a directory |
|---|---|---|
| `r` (read) | Can read file contents | Can list directory contents |
| `w` (write) | Can modify file contents | Can create/delete/rename entries inside the directory |
| `x` (execute) | Can execute the file as a program | Can enter the directory / traverse through it (needed even just to access a file inside) |

## Why ADLS specifically implements this

[ADLS Gen2](../../cloud/azure/adls.md) is built with a genuine hierarchical namespace (real folders, not simulated key prefixes) specifically so it can support POSIX ACLs the way a real filesystem does — per-file and per-directory permissions for specific users and service principals, set via [Azure](../../cloud/azure/azure.md) CLI or Storage Explorer. This is a real differentiator from [S3](../../protocols/s3-api.md) and [GCS](../../cloud/infrastructure/gcs.md), both of which only offer coarser IAM-policy-based access control precisely because their flat namespace has no real directory structure for a POSIX-style ACL to attach to.

## Not the whole access-control picture

As with every other access-control layer this handbook covers, POSIX ACLs on the storage layer don't automatically propagate into a downstream application — if [ADLS](../../cloud/azure/adls.md)-stored documents feed a [RAG](../../ai/rag/rag.md) pipeline, the application still has to read the relevant permissions and apply them as a retrieval-time filter (see [Vector Databases — Metadata filtering](../../ai/retrieval/vector-database.md#metadata-filtering)); [ADLS](../../cloud/azure/adls.md) enforcing who can read the raw file doesn't automatically enforce who can see it show up in a search result.

## Related

- [ADLS](../../cloud/azure/adls.md) — the handbook's primary example of POSIX ACLs applied to cloud storage
- [Azure RBAC](../../cloud/azure/azure-rbac.md) — the coarser-grained permission layer [ADLS](../../cloud/azure/adls.md) combines POSIX ACLs with
- [RBAC](rbac.md) — the general role-based model, contrasted with POSIX ACLs' per-identity granularity
- [Access Control & IAM](access-control-iam.md)
