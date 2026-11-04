# Governed Data

Governed data is data managed under a formal set of policies, standards, and processes that ensure its quality, security, privacy, lineage, and appropriate use across an organization. "Governed" distinguishes data that is catalogued, access-controlled, quality-validated, and auditable from raw data that simply exists in storage without accountability.

## Why It Matters

Ungoverned data is data you cannot trust and cannot safely build AI on. The phrase "governed data delivery" in an enterprise AI context means the Data Engineering team guarantees: the data is accurate, it arrived through a controlled pipeline, you know where it came from, you have permission to use it, and it meets the quality bar required before it reaches a model.

## The Four Pillars

| Pillar | What it means |
|---|---|
| **Data Quality** | Data is accurate, complete, consistent, and timely — validated at ingestion, not assumed |
| **Data Lineage** | You can trace exactly where a piece of data came from, what transformations it went through, and where it flows downstream |
| **Access Control** | Only authorized users and services can read, write, or process specific datasets — enforced at the data layer, not just the application layer |
| **Compliance & Auditability** | Every access and transformation is logged; data handling satisfies regulatory requirements (GDPR, HIPAA, Saudi PDPL, etc.) |

## In Practice: What "Governed" Looks Like

**Ungoverned:**
- A shared folder of PDFs with no metadata, no owner, no access policy
- A database table copied manually by different teams with no record of when or why
- Data used in an AI model with no record of which version was used for which training run

**Governed:**
- Every document has: `owner`, `department`, `access_level`, `created_at`, `expires_at`, `source_system` metadata
- Every transformation is tracked in a data catalog ([Azure](../azure/azure.md) Purview, [Databricks](databricks.md) Unity Catalog, Apache Atlas)
- Access is enforced at the storage layer ([ADLS](../azure/adls.md) ACLs, column-level security in [Delta Lake](delta-lake.md))
- An audit log records who accessed which data, when, and for what purpose

## Governed Data in an Enterprise RAG System

Data governance directly shapes [RAG](../../ai/rag/rag.md) architecture:

```
Governed document store
├── Each document: owner, department, access_level, retention_date
├── Access enforced at ADLS / SharePoint layer
└── Ingestion pipeline validates metadata presence before indexing

Ingestion pipeline (governed)
├── Only processes documents from approved, catalogued sources
├── Preserves access_level metadata through chunking → embedding → vector store
└── Rejects documents missing required governance fields

Retrieval (governance enforced)
├── Every query filters by requesting user's access_level BEFORE vector search
├── A document's access_level in the index matches its access_level in the source
└── Cross-department data leakage is architecturally impossible, not just unlikely
```

**The key rule:** governance metadata set at the source must flow through every pipeline stage without being stripped. If `access_level` is on the original document but not on the indexed chunk, the retrieval-time filter has nothing to enforce.

## Tools for Data Governance

| Tool | Platform | What it governs |
|---|---|---|
| **Microsoft Purview** | [Azure](../azure/azure.md) | Data catalog, lineage, classification, GDPR compliance across [Azure](../azure/azure.md) services |
| **[Databricks](databricks.md) Unity Catalog** | [Databricks](databricks.md) | Table/column/row-level access control, lineage, auditing across all [Databricks](databricks.md) workspaces |
| **Apache Atlas** | Open source / [Hadoop](../../distributed-systems/processing/hadoop.md) | Metadata management and lineage for on-premises data |
| **Collibra / Alation** | Enterprise SaaS | Business-facing data catalog — data stewardship, business glossary |
| **dbt** | Data transformation | Lineage and documentation for [SQL](../../databases/relational/sql.md) transformation pipelines |

## Data Stewardship

The human side of governance: a **data steward** is the person (or role) responsible for a dataset's quality, metadata accuracy, and appropriate use. In an enterprise [RAG](../../ai/rag/rag.md) project, the data steward for a document set is typically the department that owns the documents — they define who should have access, how long documents are retained, and what constitutes a quality standard for ingestion.

Practical implication: before building an AI feature on a dataset, identify the data steward. They approve access, validate quality expectations, and sign off on what the data can and cannot be used for.

## Interview Answer Shape

> "Governed data delivery means the Data Engineering team owns reliable, quality-validated data access — so I can focus on the AI layer without also owning the data pipeline. My role is to agree interface contracts: what fields I need, what quality bar I require, and what the acceptance criteria are for the data layer before I build on top of it. If data readiness isn't there, I surface that as a project risk immediately rather than discovering it after the pipeline is built."

## Related
- [Databricks](databricks.md) — Unity Catalog for table/column governance
- [ADLS](../azure/adls.md) — ACL-based access control at the storage layer
- [Azure AI Foundry](../azure/azure-ai-foundry.md)
- [Microsoft Entra ID](../azure/microsoft-entra-id.md) — identity layer that access policies enforce against
- [AI Use Case Prioritization](../../ai/infrastructure/ai-use-case-prioritization.md) — Data Readiness is one of the five prioritization criteria
