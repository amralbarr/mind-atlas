# Ansible

Ansible is an open-source **configuration management** tool: it installs software, edits config files, manages users, and enforces a desired state on servers that already exist — the complement to [Terraform](terraform.md), which provisions the servers/networks/storage themselves. A common real-world split: [Terraform](terraform.md) creates the VM, then Ansible turns that blank VM into a properly configured host ([Docker](../../containers/docker.md) installed, NVIDIA drivers present, firewall rules set, the application deployed).

## Configuration Management vs. Provisioning

| | [Terraform](terraform.md) | Ansible |
|---|---|---|
| Operates on | Cloud provider APIs (create/destroy resources) | Existing machines, over [SSH](../../protocols/ssh.md) |
| Answers | "What infrastructure should exist?" | "What should be installed/configured on this machine?" |
| Typical unit | A VM, a network, a firewall rule | A package, a config file, a service, a user |
| State model | Tracks a state file mapping config → real resources | Stateless by default — re-runs the same playbook and converges to the same result |

They're commonly chained: `terraform apply` creates the VM → its IP gets added to an Ansible inventory → `ansible-playbook` configures it.

## Core Concepts

| Term | Meaning |
|---|---|
| **Inventory** | The list of hosts Ansible manages, grouped by role (e.g. `control-plane`, `gpu-workers`) |
| **Playbook** | A [YAML](../../devops/yaml.md) file describing a sequence of tasks to apply to a group of hosts |
| **Role** | A reusable, named bundle of tasks/templates/handlers (e.g. a `docker` role, an `nvidia` role) that multiple playbooks can include |
| **Task** | One declarative step — "ensure this package is installed," "ensure this file has this content" |
| **Module** | The building block a task calls (`apt`, `copy`, `service`, `docker_container`, hundreds of others) — each module knows how to check current state and only change what's actually different |

## Example

```yaml
# ansible/playbooks/bootstrap-gpu-node.yml
- hosts: gpu_workers
  become: true
  roles:
    - common
    - docker
    - nvidia
    - firewall
    - node-agent
```

```bash
ansible-playbook -i ansible/inventory/production.yml ansible/playbooks/bootstrap-gpu-node.yml
```

## Idempotency Is the Whole Point

An Ansible task should describe a **desired end state**, not a one-shot imperative command — running the same playbook twice against the same host should produce no changes the second time. This is why Ansible's modules check current state before acting (`apt` won't reinstall an already-installed package; `copy` won't rewrite a file whose content already matches) rather than just blindly re-executing shell commands. Concretely: don't write a task that always reinstalls the NVIDIA driver — write one that checks whether the correct driver version is already present, and only acts if it isn't. This mirrors the same [idempotency](../../backend/api/idempotency.md) principle covered generally in [Idempotency & Race Conditions](../../programming/fundamentals/idempotency-and-race-conditions.md), applied to host configuration instead of API requests.

## Why Not Just Bash Scripts?

A bash script *can* install [Docker](../../containers/docker.md) and configure a firewall — but it typically re-runs every command every time, has no built-in concept of "only change what's different," and accumulates ad hoc conditionals to become pseudo-idempotent. Ansible's declarative task model gives you that [idempotency](../../backend/api/idempotency.md), a consistent way to target subsets of hosts (by inventory group), and reusable roles — at the cost of learning [YAML](../../devops/yaml.md)-based DSL conventions instead of writing shell directly.

## Common Questions

**Does Ansible require an agent installed on every managed server?**
> No — this is one of its main differentiators from tools like Puppet or Chef. Ansible connects over plain [SSH](../../protocols/ssh.md) and runs Python on the target transiently; there's no persistent agent process to install, update, or secure on every managed host.

**When would you skip Ansible and just use a Dockerfile/Compose file instead?**
> When everything you need to configure is scoped to *inside* a container — Ansible's value is specifically for host-level state that exists outside any container (installing [Docker](../../containers/docker.md) itself, NVIDIA drivers, firewall rules, OS packages) that has to be in place before containers can even run.

## Related

- [Infrastructure as Code](infrastructure-as-code.md)
- [Terraform](terraform.md)
- [Idempotency & Race Conditions](../../programming/fundamentals/idempotency-and-race-conditions.md)
- [Docker](../containers/docker.md)
- [Virtual Machines](../infrastructure/virtual-machines.md)
