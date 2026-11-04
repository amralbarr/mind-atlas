# CI/CD (Continuous Integration / Continuous Deployment)

## What Is It

CI/CD is a set of engineering practices and tooling that automates the steps between a developer committing code and that code running in production. It removes the long, error-prone gap that used to exist between writing code and shipping it.

The two halves:

- **Continuous Integration (CI)** — every developer merges their work into a shared branch frequently (at minimum daily). Each merge triggers an automated pipeline that builds the code and runs tests. Errors surface within minutes, while context is fresh, rather than days later during a big "integration week."
- **Continuous Deployment (CD)** — once the CI pipeline passes, the code is automatically packaged and deployed to the target environment (staging or production) without a human manually running deploy commands. The pipeline is the deployment.

Some teams draw a distinction between Continuous *Delivery* (the pipeline gets the build ready to deploy, but a human presses the button) and Continuous *Deployment* (the pipeline deploys automatically with no human gate). In practice, both are called "CD" — the difference is just where the final human approval step sits.
a
## Why It Matters

Without CI/CD, the workflow looks like this:
1. Developers work in long-lived branches for weeks.
2. Branches are merged all at once ("merge hell").
3. Someone manually runs build steps on their laptop.
4. Someone [SSH](../protocols/ssh.md)-es into the server and runs deploy commands.
5. If something breaks, it's unclear which of dozens of changes caused it.

With CI/CD:
1. Developers push small changes daily.
2. The pipeline runs automatically — tests, linting, security scans, build, deploy.
3. If a push breaks something, the pipeline fails, the team is notified immediately, and the diff is tiny and easy to diagnose.
4. Deploys become boring non-events rather than high-risk manual ceremonies.

The practical result: teams using mature CI/CD deploy up to 208x more frequently with far shorter recovery times when things do go wrong.

## The Pipeline

A CI/CD pipeline is a sequence of automated stages, typically:

| Stage                    | What Happens                                                                        |
| ------------------------ | ----------------------------------------------------------------------------------- |
| Trigger                  | A push or pull request fires the pipeline                                           |
| Install                  | Dependencies are installed in a fresh environment                                   |
| Lint / Type-check        | Code style and type errors are caught early                                         |
| Unit / Integration tests | Automated tests verify behavior                                                     |
| Build                    | Code is compiled or bundled into a deployable artifact ([Docker](../containers/docker.md) image, binary, etc.) |
| Publish                  | The artifact is pushed to a registry (e.g. [Docker](../containers/docker.md) Hub, GitHub Container Registry)   |
| Deploy                   | The artifact is rolled out to staging or production                                 |
| Notify                   | Success/failure is reported (Slack, email, PR comment)                              |

Not every project needs every stage. A small API might skip the publish step and deploy directly. A complex platform might add security scans, end-to-end tests, and canary deploys between build and full rollout.

## Key Terms

**Pipeline** — the full automated sequence of stages.

**Runner / Agent** — the machine (virtual or physical) that executes pipeline steps. [GitHub Actions](github-actions.md) calls these "runners."

**Artifact** — the output of the build stage, e.g. a compiled binary or a [Docker](../containers/docker.md) image. Artifacts are versioned and stored so any deploy can be rolled back to a known-good artifact.

**Environment** — a target for deployment. Common environments: `dev`, `staging`, `production`. Pipelines often deploy to staging automatically and require an approval gate before promoting to production.

**Secrets** — API keys, passwords, and tokens that the pipeline needs but must never be committed to source code. CI/CD platforms provide encrypted secret stores so pipelines can authenticate to external services without exposing credentials in [YAML](yaml.md) files.

## Where GitHub Actions Fits

[GitHub Actions](github-actions.md) is the CI/CD platform built directly into GitHub. A `.github/workflows/` folder in your repo holds [YAML](yaml.md) files that define pipelines. Pushes, pull requests, tags, and schedules can all trigger a workflow. See [GitHub Actions](github-actions.md) for the full breakdown of its building blocks.

## Common CI/CD Platforms

| Platform | Notes |
|---|---|
| [GitHub Actions](github-actions.md) | Native to GitHub; [YAML](yaml.md)-based; generous free tier for public repos |
| GitLab CI | Built into GitLab; strong for self-hosted teams |
| CircleCI | Cloud-native; good parallelism support |
| Jenkins | Self-hosted; highly extensible; steep setup overhead |
| [Azure](../cloud/azure/azure.md) DevOps Pipelines | Strong [Azure](../cloud/azure/azure.md) integration; often used in enterprise .NET stacks |

## Related

- [GitHub Actions](github-actions.md)
- [YAML](yaml.md) — the file format used to write every pipeline definition
- [Docker Compose](../containers/docker-compose.md)
- [Virtual Machines](../cloud/infrastructure/virtual-machines.md)
