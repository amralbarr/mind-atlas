# Infrastructure as Code (IaC)

**Infrastructure as Code** is the practice of defining and managing infrastructure (servers, networks, storage, [DNS](../../networking/dns.md), firewall rules) through machine-readable configuration files instead of manually clicking through a cloud console or running one-off commands by hand. Those files live in version control alongside application code, so infrastructure changes get the same review, history, and repeatability that code already has.

## The Problem It Solves

Without IaC, infrastructure tends to become **"ClickOps"** — a series of manual console actions nobody fully documents:

```text
Engineer A creates a VM by hand, tweaks a firewall rule, forgets to write it down
        ↓
Engineer B needs an identical staging environment
        ↓
Engineer B guesses, misses a setting, staging behaves differently from production
```

The knowledge of what infrastructure actually exists — and why — lives only in engineers' memory (or nowhere at all) rather than in a reviewable, reproducible source of truth.

## Declarative vs. Imperative IaC

| | Imperative | Declarative |
|---|---|---|
| You specify | The exact steps to reach a result ("create a VM, then attach this disk, then...") | The desired end state ("this VM, with this disk, should exist") |
| Re-running it | Can duplicate resources or error if run twice, unless carefully written to check first | Converges to the same state regardless of the starting point — re-running is safe |
| Examples | A hand-written bash script calling cloud CLI commands | [Terraform](terraform.md), CloudFormation, Pulumi |

Most modern IaC tooling favors the declarative model specifically because of that re-run safety — you describe the target state and let the tool diff it against what currently exists, rather than tracking "have I already run this step" yourself.

## Two Layers: Provisioning vs. Configuration

IaC itself splits into two related but distinct concerns, often confused because both are "infrastructure as code" in the broad sense:

| Layer | Question it answers | Tool example |
|---|---|---|
| **Provisioning** | What infrastructure should exist? (a VM, a network, a firewall rule) | [Terraform](terraform.md) |
| **Configuration management** | What should be installed/configured on infrastructure that already exists? | [Ansible](ansible.md) |

See [Ansible § Configuration Management vs. Provisioning](ansible.md#configuration-management-vs-provisioning) for the fuller comparison — the two are commonly chained ([Terraform](terraform.md) creates the VM, then [Ansible](ansible.md) configures it) rather than being competing choices.

## Why It Matters

| Benefit | What it actually buys you |
|---|---|
| **Reproducibility** | The same config file produces the same infrastructure every time, on any machine |
| **Version control** | Infrastructure changes go through the same diff/review/history as application code |
| **Drift detection** | The tool can compare declared state against real infrastructure and flag when they've diverged (someone made a manual change outside the IaC pipeline) |
| **Disaster recovery** | A destroyed environment can be recreated from the config files rather than from memory |
| **Disposable environments** | Spinning up (and tearing down) a full staging/test environment becomes a single command instead of a multi-hour manual rebuild |

## Common Questions

**Is a Dockerfile a form of IaC?**
> In spirit, yes — it's a declarative, version-controlled definition of an environment. In practice, "IaC" is usually reserved for the infrastructure *around* containers (the VMs/networks/clusters they run on), while a Dockerfile defines what runs *inside* one container. See [Docker](../containers/docker.md) and [OCI](../../containers/oci.md) for that distinct layer.

**What happens if someone manually changes infrastructure that [Terraform](terraform.md) manages?**
> This is exactly what "drift" means — the tool's next run detects the difference between its recorded state and reality, and depending on configuration, either overwrites the manual change back to the declared state or flags it for a human to reconcile. Manual changes to IaC-managed infrastructure are the most common source of drift and a common source of "but it worked when I tested it" incidents.

## Related

- [Terraform](terraform.md)
- [Ansible](ansible.md)
- [Virtual Machines](../infrastructure/virtual-machines.md)
- [Docker](../containers/docker.md)
