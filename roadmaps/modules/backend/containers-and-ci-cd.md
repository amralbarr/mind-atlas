# Module: Containers & CI/CD

**Category:** Backend · **Typical duration:** 1–2 weeks (15–20 hrs/week) · **Prerequisite modules:** [Version Control & CLI](../foundations/version-control-and-cli.md), [APIs & Backend Services](apis-and-services.md)

## Goal

Package a service so it runs the same way on any machine, and automate testing and building it on every push.

## Core topics

- [ ] Dockerfiles: layers, multi-stage builds, image size
- [ ] Compose/orchestration for local multi-service dev (app + database + cache)
- [ ] A CI pipeline: lint, test, build an image on every push
- [ ] Basic image scanning and secrets handling in CI

## Resources

- [Docker](../../../engineering/concepts/containers/docker.md)'s official "Get Started" guide
- Your CI provider's starter-workflow docs (e.g. [GitHub Actions](../../../engineering/concepts/devops/github-actions.md))

## Milestone deliverable

Containerize the milestone project from [APIs & Backend Services](apis-and-services.md) with a multi-service compose file, and add a CI pipeline that lints, tests, and builds the image on every push.

## Related concepts

[CI/CD](../../../engineering/concepts/devops/ci-cd.md), GitHub Actions, [YAML](../../../engineering/concepts/devops/yaml.md)
