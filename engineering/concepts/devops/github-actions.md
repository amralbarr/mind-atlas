# GitHub Actions

## What Is It

GitHub Actions is a [CI/CD](ci-cd.md) platform built directly into GitHub. Instead of setting up a separate CI server, you drop [YAML](yaml.md) files into `.github/workflows/` in your repository and GitHub runs them automatically when events (pushes, pull requests, releases, schedules) occur. GitHub provisions the runner machine, executes your steps, and reports results back as a green/red check on the commit or PR.

It is, concretely, the most common way teams implement a [CI/CD pipeline](ci-cd.md) when their code already lives on GitHub.

## Core Building Blocks

**Workflow**
A [YAML](yaml.md) file inside `.github/workflows/`. One repo can have multiple workflow files (e.g. `ci.yml` runs tests on every push; `deploy.yml` deploys on merge to `main`).

**Trigger (on:)**
The event(s) that start the workflow. Common triggers:
- `push` — any push to a branch
- `pull_request` — PR opened or updated
- `release` — a GitHub release is published
- `schedule` — a cron expression (e.g. nightly health checks)
- `workflow_dispatch` — a manual button in the GitHub UI

**Job**
A named unit of work inside a workflow. Jobs run in parallel by default; you can add `needs: [other-job]` to serialize them. Each job runs on its own fresh runner.

**Step**
A single command or action inside a job. Steps run sequentially within a job and share the same filesystem.

**Action**
A reusable, packaged step published to the GitHub Marketplace (or defined locally). Examples: `actions/checkout@v4` clones your repo; `docker/build-push-action@v5` builds and pushes a [Docker](../containers/docker.md) image. Actions abstract away boilerplate.

**Runner**
The virtual machine that executes a job. GitHub provides hosted runners (Ubuntu, Windows, macOS). You can also register your own self-hosted runner — useful for build machines with GPUs, or for deploying to a private network.

**Secrets**
Encrypted values stored in repository or organization settings. Referenced in [YAML](yaml.md) as `${{ secrets.MY_SECRET }}`. Never visible in logs. Used for [Docker](../containers/docker.md) Hub tokens, [SSH](../protocols/ssh.md) keys, API credentials, etc.

**Artifacts**
Files produced during a workflow (test reports, built binaries, [Docker](../containers/docker.md) tarballs) that you want to persist or pass between jobs. Uploaded with `actions/upload-artifact` and downloaded with `actions/download-artifact`.

## Anatomy of a Workflow File

```yaml
name: CI

on:
  push:
    branches: [main, dev]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest          # GitHub-hosted runner

    steps:
      - name: Checkout code
        uses: actions/checkout@v4   # clones the repo onto the runner

      - name: Set up Node
        uses: actions/setup-node@v4
        with:
          node-version: 20

      - name: Install dependencies
        run: npm ci                 # plain shell command

      - name: Run tests
        run: npm test

  deploy:
    runs-on: ubuntu-latest
    needs: test                     # only runs if 'test' job passes
    if: github.ref == 'refs/heads/main'   # only on main branch

    steps:
      - uses: actions/checkout@v4

      - name: Build and push Docker image
        uses: docker/build-push-action@v5
        with:
          push: true
          tags: myregistry/myapp:latest
        env:
          DOCKER_TOKEN: ${{ secrets.DOCKER_TOKEN }}
```

Reading this top-to-bottom: on every push to `main` or `dev`, run the `test` job. If tests pass and the branch is `main`, also run the `deploy` job.

## Pricing and Limits

- **Public repos**: unlimited free minutes on GitHub-hosted runners.
- **Private repos**: 2,000 free minutes/month on the free plan; billed beyond that.
- **Self-hosted runners**: no per-minute billing; you pay for the machine.

## What Makes It Distinct

| Capability | GitHub Actions | Jenkins |
|---|---|---|
| Setup effort | Zero — [YAML](yaml.md) in repo | Significant — self-hosted server |
| GitHub integration | Native (PR checks, status, secrets) | Plugin-based |
| Community actions | 20,000+ on Marketplace | Plugins, less curated |
| Self-hosting | Optional (runners) | Required |
| Cost | Free for public repos | Server cost only |

## Common Patterns

**Test on every PR** — `on: pull_request` + a job that runs your test suite. The PR is blocked from merging if the check fails (enforce via branch protection rules).

**Build and push a [Docker](../containers/docker.md) image on merge to main** — `on: push` with branch filter + `docker/build-push-action`.

**Deploy to a server via [SSH](../protocols/ssh.md)** — `appleboy/ssh-action` step that SSHes into your VM and runs `docker compose pull && docker compose up -d`.

**Scheduled health check** — `on: schedule` with a cron expression running a smoke test against production.

## Related

- [CI/CD](ci-cd.md)
- [Docker Compose](../containers/docker-compose.md)
