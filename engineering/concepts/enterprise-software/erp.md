# ERP (Enterprise Resource Planning)

ERP is a category of business software that unifies the core operational functions of an organization — finance, HR, supply chain, manufacturing, procurement, sales — into one integrated system backed by a single, shared source of truth, instead of each department running its own disconnected tool. The defining property isn't any one module; it's that a change in one module (a purchase order, a new hire, a finished-goods shipment) is immediately visible and consistent everywhere else that depends on it, because every module reads and writes the same underlying data rather than exporting/re-importing between separate systems.

## Core Modules

| Module | What it covers |
|---|---|
| **Finance & Accounting** | General ledger, accounts payable/receivable, budgeting, financial reporting, tax compliance |
| **HR / HCM** | Payroll, headcount, benefits, time & attendance — often the module that hands off to a [LMS](lms.md) for employee training/compliance tracking |
| **Supply Chain & Procurement** | Purchase orders, vendor management, demand planning |
| **Manufacturing / Production** | Bills of materials, work orders, shop-floor scheduling |
| **Inventory & Warehouse** | Stock levels, warehouse locations, fulfillment |
| **CRM / Sales** | Quotes, orders, customer accounts (sometimes a bundled module, sometimes a separate system integrated in) |
| **Project Management** | Budgets, timesheets, resource allocation for project-based work |
| **Business Intelligence / Reporting** | Cross-module dashboards and analytics, possible only because the data already lives in one place |

Most real deployments don't turn on every module — a mid-size manufacturer might run Finance, Supply Chain, and Manufacturing while leaving CRM to a dedicated tool integrated via API; the "ERP" label describes the unified-data architecture, not a mandatory feature checklist.

## How It Works: Shared Database, Modular Front End

Architecturally, a traditional ERP is closer to a large [monolith](../backend/architecture/monolith-vs-microservices.md) than a microservices system: one relational database (historically [SQL](../databases/relational/sql.md)-based) underlies every module, and the modules themselves are more like views and workflows over that shared schema than independently deployable services. This is a deliberate trade-off versus a best-of-breed collection of separate point solutions: it buys data consistency and a single reporting surface, at the cost of the kind of independent scaling and deployment flexibility a [microservices](../backend/architecture/monolith-vs-microservices.md) architecture would give each function. Modern cloud ERPs (see below) have moved toward more service-oriented internals, but the "one logical source of truth" principle is preserved regardless of the underlying implementation — it's the point of calling it an ERP at all.

Because one organization's ERP instance often serves many business units, subsidiaries, or (for a cloud/SaaS vendor) many separate customer organizations on the same platform, the same [multi-tenancy](../backend/architecture/multi-tenancy.md) concerns around data isolation between tenants apply directly to how an ERP vendor architects its database and query layer.

## On-Premise vs Cloud ERP

| Model | Deployment | Typical trade-off |
|---|---|---|
| **On-premise** | Installed and run on the customer's own servers/data center | Full control and customization, but the customer owns patching, scaling, and hardware |
| **Cloud / SaaS ERP** | Vendor-hosted, subscription-based, accessed over the internet | Lower upfront cost and faster rollout, but less deep customization and dependence on the vendor's release cadence |

As of 2026, the large majority of new ERP deployments and market growth are cloud-based — the leading enterprise vendors (SAP S/4HANA Cloud, Oracle Fusion Cloud, Microsoft Dynamics 365, Infor CloudSuite, Workday) now lead primarily with cloud editions, with on-premise offerings mostly serving existing long-term customers or regulatory environments that require it. At the smaller end, Odoo and NetSuite are common cloud choices for small-to-mid businesses that don't need full enterprise-scale deployments.

## ERP Applied to Government: GRP

When the same unified-system idea is applied specifically to government administrative functions — budgeting, procurement, payroll, inter-agency reporting — rather than to a private company's operations, it's sometimes marketed under the separate term **GRP (Government Resource Planning)**. The underlying architecture and core benefit (one shared source of truth across departments/ministries that otherwise run disconnected legacy systems) are the same as commercial ERP; GRP is essentially a go-to-market/vertical label for ERP sold into the public sector, not a structurally different category of software.

## Implementation: Configuration vs Customization

A recurring real-world failure mode in ERP projects is treating the system as infinitely customizable rather than working within its configuration options: heavy custom code written against the vendor's base product makes every future vendor upgrade a re-integration project, since the customization has to be re-applied or re-tested against the new version each time. Mature implementations lean on the vendor's built-in configuration (forms, workflows, approval chains that are data-driven rather than code-driven) wherever possible, and treat true custom development as the exception reserved for genuinely unsupported requirements — the same configuration-over-custom-code instinct that shows up across most large, long-lived enterprise software, not specific to any one vendor.

## Common Questions

**Is an ERP the same thing as a CRM?**
> No — a CRM (Customer Relationship Management system) focuses specifically on sales pipeline, customer accounts, and support interactions. Many ERPs bundle a CRM module, and many organizations instead run a dedicated CRM (e.g. Salesforce) integrated with their ERP via API, but the two solve different core problems: CRM is customer-facing relationship/sales data, ERP is internal operational/financial data.

**Why do ERP implementations have a reputation for running over budget and schedule?**
> Because the hard part usually isn't the software — it's data migration (reconciling years of inconsistent legacy data into one clean schema) and organizational change management (getting every department to actually change how they work to match the new unified process), both of which scale with how many departments and how much legacy history the organization has, not with the ERP vendor's feature list.

## Related

- [LMS](lms.md) — an ERP's HR/HCM module typically hands off employee training and compliance-tracking responsibilities to this dedicated system rather than reimplementing it
- [Monolith vs Microservices](../backend/architecture/monolith-vs-microservices.md) — traditional ERP architecture is the monolithic end of this spectrum: one shared database underlying every module
- [Multi-Tenancy & Tenant Isolation](../backend/architecture/multi-tenancy.md) — the isolation concerns a cloud ERP vendor faces running many customer organizations on shared infrastructure
- [SQL](../databases/relational/sql.md) — the relational data model most traditional and many modern ERP systems are built on
- [System Design](../backend/architecture/system-design.md) — the shared-database, modular-front-end pattern an ERP exemplifies is a recurring system-design trade-off (consistency vs. independent scalability)
