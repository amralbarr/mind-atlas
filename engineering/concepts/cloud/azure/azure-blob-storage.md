# Azure Blob Storage

Azure Blob Storage is Microsoft's cloud [object storage](../infrastructure/object-storage.md) service — the [Azure](azure.md) equivalent of [AWS S3](../../protocols/s3-api.md). It stores unstructured data (files, images, videos, backups, logs) as **blobs** inside **containers** inside a **storage account**. It is deeply integrated with the [Azure](azure.md) ecosystem ([Microsoft Entra ID](microsoft-entra-id.md) — formerly [Azure](azure.md) AD, [Azure Functions](azure-functions.md), [Azure CDN](azure-cdn.md), [Azure Data Factory (ADF)](azure-data-factory.md)) and is a common choice when the rest of the stack is on [Azure](azure.md).

## Core Concepts

| Term                | Meaning                                                              |
| ------------------- | -------------------------------------------------------------------- |
| **Storage Account** | Top-level namespace; holds all containers and blobs                  |
| **Container**       | Logical grouping of blobs (like an S3 bucket)                        |
| **Blob**            | A stored object — name + binary data + metadata                      |
| **Blob types**      | Block Blob (general files), Append Blob (logs), Page Blob (VM disks) |
| **Access tier**     | Hot (frequent), Cool (infrequent), Archive (rare, retrieval delay)   |
| **SAS token**       | Shared Access Signature — time-limited URL with scoped permissions   |

**Block Blob** is the type you use for almost everything (documents, images, datasets). Append and Page blobs are for specific infrastructure use cases.

## Storage Account Naming

Storage account names are globally unique across Azure, 3–24 lowercase alphanumeric characters, no hyphens.

Container names are lowercase, 3–63 characters, hyphens allowed.

## Authentication Options

| Method                                                             | When to use                                                          |
| ------------------------------------------------------------------ | -------------------------------------------------------------------- |
| **Connection String**                                              | Dev / local — includes account name + key                            |
| **Account Key**                                                    | Direct key auth ([HMAC](../../security/secrets/hmac.md)-signed) — full admin access, rotate regularly                |
| **SAS Token**                                                      | Scoped, time-limited access for external clients                     |
| **[Microsoft Entra ID](microsoft-entra-id.md) / Managed Identity** | Production — no secrets needed; identity-based [RBAC](azure-rbac.md) |
| **Service Principal**                                              | [CI/CD](../../devops/ci-cd.md), non-Azure apps that need Entra ID auth                        |

Prefer **Managed Identity** in production (no secret rotation needed). Use **connection strings** only locally.

## Installation

```bash
pip install azure-storage-blob python-dotenv
```

## Connect

```python
from azure.storage.blob import BlobServiceClient
import os
from dotenv import load_dotenv

load_dotenv()

# Option 1: Connection string (dev)
client = BlobServiceClient.from_connection_string(os.getenv("AZURE_STORAGE_CONNECTION_STRING"))

# Option 2: Account key
client = BlobServiceClient(
    account_url=f"https://{os.getenv('AZURE_STORAGE_ACCOUNT')}.blob.core.windows.net",
    credential=os.getenv("AZURE_STORAGE_KEY"),
)

# Option 3: Managed Identity (production — no secret needed)
from azure.identity import DefaultAzureCredential
client = BlobServiceClient(
    account_url=f"https://{os.getenv('AZURE_STORAGE_ACCOUNT')}.blob.core.windows.net",
    credential=DefaultAzureCredential(),
)
```

## Container Operations

```python
# Create container
container_client = client.create_container("my-container")

# Get existing container client
container_client = client.get_container_client("my-container")

# List containers
for c in client.list_containers():
    print(c["name"])

# Delete container
client.delete_container("my-container")
```

## Blob Operations

```python
container = client.get_container_client("my-container")

# Upload from file
with open("report.pdf", "rb") as f:
    container.upload_blob(name="reports/report.pdf", data=f, overwrite=True)

# Upload from bytes
container.upload_blob(name="data.json", data=b'{"key": "value"}', overwrite=True)

# Download to file
blob = container.get_blob_client("reports/report.pdf")
with open("downloaded.pdf", "wb") as f:
    f.write(blob.download_blob().readall())

# Download to bytes
data = blob.download_blob().readall()

# List blobs
for b in container.list_blobs(name_starts_with="reports/"):
    print(b.name, b.size, b.last_modified)

# Delete blob
blob.delete_blob()

# Check if blob exists
from azure.core.exceptions import ResourceNotFoundError
try:
    blob.get_blob_properties()
    exists = True
except ResourceNotFoundError:
    exists = False
```

## Blob Metadata & Properties

```python
# Set metadata on upload
container.upload_blob(
    name="doc.pdf",
    data=data,
    metadata={"author": "alice", "department": "finance"},
    overwrite=True,
)

# Read metadata
props = blob.get_blob_properties()
print(props.metadata)
print(props.size)
print(props.last_modified)
print(props.content_settings.content_type)
```

## SAS Tokens (Temporary Access URLs)

```python
from azure.storage.blob import generate_blob_sas, BlobSasPermissions
from datetime import datetime, timedelta, timezone

sas_token = generate_blob_sas(
    account_name=os.getenv("AZURE_STORAGE_ACCOUNT"),
    container_name="my-container",
    blob_name="reports/report.pdf",
    account_key=os.getenv("AZURE_STORAGE_KEY"),
    permission=BlobSasPermissions(read=True),
    expiry=datetime.now(timezone.utc) + timedelta(hours=1),
)

sas_url = (
    f"https://{os.getenv('AZURE_STORAGE_ACCOUNT')}.blob.core.windows.net"
    f"/my-container/reports/report.pdf?{sas_token}"
)
print(sas_url)  # share this — no credentials required
```

## Access Tiers

```python
from azure.storage.blob import StandardBlobTier

# Set tier on upload
container.upload_blob(
    name="archive/old.pdf",
    data=data,
    standard_blob_tier=StandardBlobTier.COOL,
)

# Change tier on existing blob
blob.set_standard_blob_tier(StandardBlobTier.ARCHIVE)
```

| Tier        | Use case                               | Retrieval               |
| ----------- | -------------------------------------- | ----------------------- |
| **Hot**     | Frequently accessed data               | Immediate               |
| **Cool**    | Infrequently accessed, stored ≥30 days | Immediate               |
| **Cold**    | Rarely accessed, stored ≥90 days       | Immediate               |
| **Archive** | Long-term retention, stored ≥180 days  | Hours (rehydrate first) |

## Environment Variables

```bash
# .env

# Dev — connection string (includes everything)
AZURE_STORAGE_CONNECTION_STRING=DefaultEndpointsProtocol=https;AccountName=myaccount;AccountKey=xxx;EndpointSuffix=core.windows.net

# Production — separate account + key (or use Managed Identity and omit the key)
AZURE_STORAGE_ACCOUNT=myaccount
AZURE_STORAGE_KEY=base64encodedkey==
```

## Lifecycle Management (Auto-tier / Delete)

Set rules in the Azure Portal or via policy to automatically move blobs between tiers or delete them after N days:

```json
{
  "rules": [{
    "name": "archive-old-reports",
    "type": "Lifecycle",
    "definition": {
      "filters": { "blobTypes": ["blockBlob"], "prefixMatch": ["reports/"] },
      "actions": {
        "baseBlob": {
          "tierToCool": { "daysAfterModificationGreaterThan": 30 },
          "tierToArchive": { "daysAfterModificationGreaterThan": 90 },
          "delete": { "daysAfterModificationGreaterThan": 365 }
        }
      }
    }
  }]
}
```

## Azure Blob vs S3 / MinIO

|               | Azure Blob                                                                                          | [AWS S3](../../protocols/s3-api.md)                                                                            | MinIO                                                  |
| ------------- | --------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------ |
| Vendor        | [Microsoft Azure](azure.md)                                                                                     | Amazon [AWS](../infrastructure/aws.md)                                                                                                     | Self-hosted / any cloud                                |
| Auth          | [Entra ID](microsoft-entra-id.md) / SAS / [Key (HMAC)](../../security/secrets/hmac.md)              | [IAM](../../security/authorization/access-control-iam.md) / [HMAC](../../security/secrets/hmac.md) / Presigned | [HMAC](../../security/secrets/hmac.md) (S3-compatible) |
| API           | Azure SDK (+ S3-compat layer)                                                                       | [S3 API](../../protocols/s3-api.md)                                                                                                         | [S3 API](../../protocols/s3-api.md)                                                 |
| Integration   | Azure services ([ADF](azure-data-factory.md), [Functions](azure-functions.md), [CDN](azure-cdn.md)) | [AWS](../infrastructure/aws.md) services                                                                                                   | Any S3 client                                          |
| Pricing model | Per GB + operations                                                                                 | Per GB + operations                                                                                            | Free (self-hosted infra cost)                          |
| Best for      | Azure-native stacks                                                                                 | [AWS](../infrastructure/aws.md)-native stacks                                                                                              | On-prem / S3-compatible                                |

Azure Blob Storage has an optional **S3-compatible API** (preview) but it is not the native interface — use the Azure SDK for full feature access.

## Terraform (provision storage account + container)

```hcl
resource "azurerm_storage_account" "main" {
  name                     = "mystorageaccount"
  resource_group_name      = azurerm_resource_group.main.name
  location                 = azurerm_resource_group.main.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
}

resource "azurerm_storage_container" "docs" {
  name                  = "documents"
  storage_account_name  = azurerm_storage_account.main.name
  container_access_type = "private"
}
```

## Related Concepts

- [ADLS](adls.md) — the hierarchical-namespace, POSIX-ACL superset of this same storage account model, built specifically for big-data analytics
- [Microsoft Entra ID](microsoft-entra-id.md) — formerly Azure AD, the identity provider behind Managed Identity and Service Principal auth
- [Azure Functions](azure-functions.md) — serverless compute commonly triggered by new blobs landing in a container
- [Azure CDN](azure-cdn.md) — caches blob content at edge locations for lower-latency, lower-cost public delivery
- [Azure Data Factory (ADF)](azure-data-factory.md) — the pipeline/orchestration service that most commonly reads from and writes to Blob Storage
- [Azure RBAC](azure-rbac.md) — the coarse-grained role layer identity-based auth is checked against
- [HMAC](../../security/secrets/hmac.md) — the keyed-hash mechanism behind Account Key signing, and S3/MinIO's auth
- [Access Control & IAM](../../security/authorization/access-control-iam.md) — the general identity/access-management framework S3's "IAM" row implements
- [Object Storage / MinIO](../infrastructure/object-storage.md) — S3-compatible self-hosted alternative
- [S3 API](../../protocols/s3-api.md) — the S3 protocol that Azure Blob partially mirrors
- [Terraform](../iac/terraform.md) — provision Azure storage accounts as infrastructure-as-code
- [python-dotenv](../../../installation/linux/python.md) — manage credentials securely
