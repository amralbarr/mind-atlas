# Azure Blob Container

A **Blob Container** is the logical grouping layer inside an [Azure](azure.md) Storage Account that holds blobs (files). It is the direct equivalent of an S3 bucket. Every blob must live inside a container; a storage account can hold unlimited containers.

## Hierarchy

```
Azure Subscription
└── Resource Group
    └── Storage Account  (globally unique name)
        └── Container    (lowercase, 3–63 chars)
            └── Blob     (file + metadata)
```

## Container Access Levels

| Level | Who can access blobs |
|---|---|
| **Private** (default) | Only authenticated requests (account key, SAS, [Azure](azure.md) AD) |
| **Blob** | Anyone can read blobs by URL; container listing requires auth |
| **Container** | Anyone can read blobs AND list container contents |

Always default to **Private** — grant access via SAS tokens or [Azure](azure.md) AD [RBAC](../../security/authorization/rbac.md) instead of making containers public.

## Create & Manage (Azure CLI)

```bash
# Create container
az storage container create \
  --name my-container \
  --account-name mystorageaccount \
  --auth-mode login

# List containers
az storage container list \
  --account-name mystorageaccount \
  --auth-mode login \
  --output table

# Show container properties
az storage container show \
  --name my-container \
  --account-name mystorageaccount \
  --auth-mode login

# Set access level
az storage container set-permission \
  --name my-container \
  --account-name mystorageaccount \
  --public-access off          # off | blob | container

# Delete container (and all blobs inside)
az storage container delete \
  --name my-container \
  --account-name mystorageaccount \
  --auth-mode login
```

## Python SDK

```python
from azure.storage.blob import BlobServiceClient, PublicAccess
import os
from dotenv import load_dotenv

load_dotenv()

service = BlobServiceClient.from_connection_string(
    os.getenv("AZURE_STORAGE_CONNECTION_STRING")
)

# Create (private)
service.create_container("my-container")

# Create with public blob access
service.create_container("public-assets", public_access=PublicAccess.BLOB)

# Get container client
container = service.get_container_client("my-container")

# List blobs
for blob in container.list_blobs(name_starts_with="reports/"):
    print(blob.name, blob.size)

# Get container properties & access level
props = container.get_container_properties()
print(props.public_access)

# Delete container
container.delete_container()
```

## Blob Operations (via Container Client)

```python
# Upload
with open("file.pdf", "rb") as f:
    container.upload_blob(name="docs/file.pdf", data=f, overwrite=True)

# Download
blob_client = container.get_blob_client("docs/file.pdf")
data = blob_client.download_blob().readall()

# Delete blob
blob_client.delete_blob()

# Copy blob between containers
dest = service.get_blob_client("archive-container", "docs/file.pdf")
dest.start_copy_from_url(blob_client.url)
```

## Container Metadata

```python
# Set metadata
container.set_container_metadata(metadata={"env": "production", "team": "data"})

# Read metadata
props = container.get_container_properties()
print(props.metadata)
```

## Soft Delete (Accidental Deletion Protection)

Enable at the storage account level — deleted blobs and containers are retained for a configurable number of days and can be restored.

```bash
# Enable blob soft delete (7-day retention)
az storage account blob-service-properties update \
  --account-name mystorageaccount \
  --enable-delete-retention true \
  --delete-retention-days 7

# Enable container soft delete
az storage account blob-service-properties update \
  --account-name mystorageaccount \
  --enable-container-delete-retention true \
  --container-delete-retention-days 7
```

## Terraform

```hcl
resource "azurerm_storage_container" "documents" {
  name                  = "documents"
  storage_account_name  = azurerm_storage_account.main.name
  container_access_type = "private"   # private | blob | container
}
```

## Environment Variables

```bash
# .env
AZURE_STORAGE_CONNECTION_STRING=DefaultEndpointsProtocol=https;AccountName=...;AccountKey=...
AZURE_STORAGE_ACCOUNT=mystorageaccount
AZURE_STORAGE_CONTAINER=my-container
```

## Related Concepts

- [Azure Blob Storage](./azure-blob-storage.md) — storage accounts, SAS tokens, access tiers
- [S3 API](../../protocols/s3-api.md) — S3-compatible equivalent (buckets ≈ containers)
- [Terraform](./terraform.md) — provision containers as infrastructure-as-code
