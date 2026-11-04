# Azure RBAC (Role-Based Access Control)

**[Azure](azure.md) [RBAC](../../security/authorization/rbac.md)** is [Azure](azure.md)'s identity-based [authorization](../../security/authorization/authorization.md) system — it controls **who can manage which [Azure](azure.md) resources**, at what scope, through **role assignments**. It answers "can this identity create/read/update/delete this resource?" — it says nothing about network traffic.

## The three parts of a role assignment

Every Azure RBAC permission is a triple:

1. **Security principal** — the identity being granted access: a user, a group, a service principal, or a managed identity (all backed by [Microsoft Entra ID](microsoft-entra-id.md))
2. **Role definition** — the set of permissions (e.g. `Reader`, `Contributor`, `Owner`, `Virtual Machine Contributor`) — built-in or custom
3. **Scope** — the boundary the role applies to: management group → subscription → resource group → individual resource. Roles are inherited downward (a role at the resource-group scope applies to everything inside it).

```
Scope hierarchy (role inherited top → down):
Management Group
 └── Subscription
      └── Resource Group      ← e.g. "nextcloud-rg"
           └── Resource        ← e.g. one specific VM
```

## Common built-in roles

| Role | Grants |
|---|---|
| `Reader` | View resources only, no changes |
| `Contributor` | Create/manage resources, but cannot grant access to others |
| `Owner` | Full control, including managing role assignments |
| `Virtual Machine Contributor` | Manage VMs (start/stop/restart), but not the [VNet](azure-vnet.md)/[NSG](azure-nsg.md) around them |
| `Network Contributor` | Manage networking resources ([VNet](azure-vnet.md), [NSG](azure-nsg.md), public IP) |

## RBAC vs NSG — different layers, easy to conflate

This is the distinction that matters most in practice:

| | Azure RBAC | [NSG](azure-nsg.md) |
|---|---|---|
| Controls | Who can manage/administer a resource via the [Azure](azure.md) control plane (portal, CLI, API) | What network traffic can reach a resource on the data plane (ports, protocols, source IPs) |
| Identity model | Entra ID users/groups/service principals | IP addresses / address ranges / service tags |
| Example | "Alice can start/stop this VM" | "Only 203.0.113.5 can reach this VM on port 22" |
| Fixing one fixes... | Portal/CLI access to the resource | Network-level reachability of the resource |

**Being granted an Azure RBAC role on a resource group does not open any network path to the VMs inside it.** A user can have `Contributor` on `nextcloud-rg` and still be unable to [SSH](../../protocols/ssh.md) into the VM, because the [NSG](azure-nsg.md) attached to that VM's subnet/[NIC](azure-network-interface.md) is a completely separate, IP-based allow list. Fixing the [RBAC](../../security/authorization/rbac.md)/group assignment does nothing to fix "my IP changed and the [NSG](azure-nsg.md) rule no longer matches me" — that's a network-layer problem, not an identity-layer one. See [Azure Bastion](../remote-access/azure-bastion.md) for the fix that extends the same Entra-ID-based access model to the network layer instead of relying on IP allowlisting.

## Common project pattern: group-based role assignment

Rather than assigning roles to individuals one by one, assign the role once to a Entra ID **group**, then manage membership:

```bash
# Create an Entra ID group (or use Portal)
az ad group create --display-name "nextcloud-team" --mail-nickname "nextcloud-team"

# Assign a role to the group at the resource-group scope
az role assignment create \
  --assignee <group-object-id> \
  --role "Contributor" \
  --scope /subscriptions/<sub-id>/resourceGroups/nextcloud-rg

# Add a user to the group (they inherit the role assignment)
az ad group member add --group "nextcloud-team" --member-id <user-object-id>
```

## Azure CLI reference

```bash
# List role assignments at a scope
az role assignment list --resource-group nextcloud-rg --output table

# List available built-in roles
az role definition list --output table

# Remove a role assignment
az role assignment delete --assignee <principal-id> --role "Contributor" --scope <scope>
```

## Related Concepts

- [Microsoft Entra ID](microsoft-entra-id.md) — the identity provider backing every [RBAC](../../security/authorization/rbac.md) role assignment
- [Azure NSG](azure-nsg.md) — the network-layer counterpart [RBAC](../../security/authorization/rbac.md) does not replace
- [Azure Bastion](../remote-access/azure-bastion.md) — extends Entra-ID access control to network access
- [Access Control & IAM](../../security/authorization/access-control-iam.md) — general IAM concepts this specializes
- [Azure](azure.md) — platform overview
