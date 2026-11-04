# Amazon Web Services (AWS)

AWS is the largest cloud provider by market share — a vast catalog of on-demand infrastructure services (compute, storage, databases, networking, and hundreds more), billed by usage rather than bought as fixed hardware. See [Cloud Providers](../../../overviews/cloud/cloud-providers.md) for how it compares to [Azure](../azure/azure.md) and [GCP](gcp.md), and [Microsoft Azure](../azure/azure.md) for the provider actually used elsewhere in this vault's project notes.

## Core Concepts

| Term | Meaning |
|---|---|
| **Region** | A geographic area with multiple independent data centers (e.g. `us-east-1`) |
| **Availability Zone (AZ)** | An isolated data center within a region — deploying across multiple AZs is the standard way to survive a single data center failure |
| **IAM (Identity and Access Management)** | AWS's access-control system — users, roles, and policies defining exactly what an identity can do, down to individual API actions |
| **VPC (Virtual Private Cloud)** | An isolated virtual network within AWS where resources (EC2 instances, RDS databases) are placed |
| **ARN (Amazon Resource Name)** | The globally unique identifier format for any AWS resource, used throughout IAM policies and API calls |

## Core Services

| Service | Purpose | Analogous to |
|---|---|---|
| **EC2** | [Virtual machines](virtual-machines.md) | [Azure](../azure/azure.md) VM, [GCP](gcp.md) Compute Engine |
| **S3** | [Object storage](object-storage.md) | [Azure Blob Storage](../azure/azure-blob-storage.md), [GCP](gcp.md) Cloud Storage — see [S3 API](../../protocols/s3-api.md) |
| **RDS** | Managed relational databases (Postgres, [MySQL](../../databases/relational/mysql.md), etc.) | [Azure](../azure/azure.md) [SQL](../../databases/relational/sql.md), [GCP](gcp.md) Cloud [SQL](../../databases/relational/sql.md) |
| **DynamoDB** | Managed NoSQL key-value/document database | [Azure](../azure/azure.md) Cosmos DB, [GCP](gcp.md) Firestore |
| **Lambda** | Serverless functions, billed per invocation | [Azure Functions](../azure/azure-functions.md), GCP Cloud Functions |
| **[SQS](../../distributed-systems/messaging/sqs.md) / SNS** | Managed message queue / pub-sub | See [SQS](../../distributed-systems/messaging/sqs.md) |
| **EKS** | Managed [Kubernetes](../../distributed-systems/kubernetes/ingress.md) | AKS, GKE |
| **IAM** | Access control | [Azure](../azure/azure.md) AD/Entra ID, GCP IAM |

## AWS CLI — Basic Usage

```bash
aws configure                     # set access key, secret, default region
aws s3 ls                          # list S3 buckets
aws ec2 describe-instances          # list running EC2 instances
aws sts get-caller-identity         # confirm which identity the CLI is authenticated as
```

## A Minimal IAM Policy

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": ["s3:GetObject"],
      "Resource": "arn:aws:s3:::my-bucket/*"
    }
  ]
}
```

This grants read-only access to objects in one specific bucket — the least-privilege principle underlying every well-run AWS account: grant exactly the actions/resources a role needs, not broad admin access by default.

## Common Questions

**Why is AWS usually the default recommendation for learning cloud?**
> Largest install base, the most tutorials/community content, and typically the widest breadth of services to explore under its free tier — not because it's technically superior to Azure or GCP for every workload. See [Cloud Providers](../../../overviews/cloud/cloud-providers.md) for workload-specific recommendations.

**What's the practical difference between EC2 and Lambda?**
> EC2 is a persistent virtual machine you manage the OS/runtime of, billed continuously while running. Lambda runs your code only in response to an event/request, with no server to manage and billing per invocation/duration — a fundamentally different cost and operational model, not just "a smaller VM."

## Related

- [Cloud Providers](../../../overviews/cloud/cloud-providers.md)
- [Microsoft Azure](../azure/azure.md)
- [GCP](gcp.md)
- [SQS](../../distributed-systems/messaging/sqs.md)
- [AWS API Gateway](../../backend/api-gateways/aws-api-gateway.md)
- [S3 API](../../protocols/s3-api.md)
- [Access Control & IAM](../../security/authorization/access-control-iam.md)
