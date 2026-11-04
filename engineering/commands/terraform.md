# Terraform Commands

The core [Terraform](../concepts/cloud/iac/terraform.md) CLI workflow. See [Terraform](../concepts/cloud/iac/terraform.md) for the underlying concepts (state, providers, declarative provisioning) and [Infrastructure as Code](../concepts/cloud/iac/infrastructure-as-code.md) for the broader principle this tool implements.

## Install & Setup

```bash
brew install terraform                     # macOS
terraform -version
```

## The Core Workflow

```bash
terraform init                             # download providers, set up backend/state
terraform plan                             # preview what would change, without applying
terraform apply                            # apply the plan (prompts for confirmation)
terraform apply -auto-approve              # skip the confirmation prompt (CI pipelines)
terraform destroy                          # tear down everything Terraform manages here
```

`init` is the only command that ever needs re-running just because you changed machines or pulled someone else's `.tf` changes — it's what actually fetches the provider plugins.

## Inspecting State

```bash
terraform show                             # human-readable dump of current state
terraform state list                       # every resource Terraform is tracking
terraform state show <resource.address>    # full attributes of one resource
terraform output                           # print declared output values
terraform output -json                     # machine-readable output, for scripting
```

## Targeted Operations

```bash
terraform plan -target=<resource.address>      # plan just one resource
terraform apply -target=<resource.address>     # apply just one resource
terraform destroy -target=<resource.address>   # destroy just one resource
```

Targeting is an escape hatch for debugging or a partial rollout — routine use of `-target` usually means the configuration should be split into smaller, independently-applied modules instead.

## State Surgery (Handle With Care)

```bash
terraform state mv <old.address> <new.address>   # rename a resource in state without recreating it
terraform state rm <resource.address>            # stop tracking a resource (leaves the real thing untouched)
terraform import <resource.address> <real-id>    # start tracking infrastructure that already exists
```

`state rm` and `import` are how you reconcile [Terraform](../concepts/cloud/iac/terraform.md) with infrastructure that was changed or created outside of it — see [Infrastructure as Code § Common Questions](../concepts/cloud/iac/infrastructure-as-code.md#common-questions) for what "drift" means here.

## Formatting & Validation

```bash
terraform fmt                              # auto-format .tf files to canonical style
terraform validate                         # check syntax and internal consistency, no API calls
```

Run both in CI before `plan`/`apply` — they catch mistakes for free, with no cloud-provider credentials required.

## Workspaces (Multiple Environments, One Config)

```bash
terraform workspace list
terraform workspace new staging
terraform workspace select staging
```

Each workspace gets its own state, so the same `.tf` files can manage separate `dev`/`staging`/`prod` environments — a lighter-weight alternative to fully duplicating the configuration per environment.

## Variables

```bash
terraform apply -var="region=us-east-1"
terraform apply -var-file="production.tfvars"
```

Never commit a `.tfvars` file containing real secrets — pass sensitive values via environment variables (`TF_VAR_<name>`) or a secrets manager instead. See [Secrets Management](../concepts/security/secrets/secrets-management.md).

## Related

- [Terraform](../concepts/cloud/iac/terraform.md)
- [Infrastructure as Code](../concepts/cloud/iac/infrastructure-as-code.md)
- [Ansible](../concepts/cloud/iac/ansible.md)
- [Azure CLI](azure.md)
- [Secrets Management](../concepts/security/secrets/secrets-management.md)
