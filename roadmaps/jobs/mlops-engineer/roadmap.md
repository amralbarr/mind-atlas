# Example: MLOps / ML Platform Engineer Roadmap, Zero to Hero

A worked example of the [roadmap system](../../README.md), assembled from [modules/](../../modules/) for the profile in [job-profile-mlops-engineer.md](job-profile.md). This archetype is platform/infrastructure-first — it spends far less time on model theory than the [Machine Learning Engineer](../ml-engineer/roadmap.md) roadmap and far more on the systems that keep many models running reliably.

## How to use this roadmap

- Total: ~28 weeks at 15–20 hours/week.
- **Fast-track rule:** try each phase's milestone first; skip ahead if you can already build it unaided.
- **Build, don't just watch:** every milestone extends the last into one real ML platform.
- **Weekly rhythm:** roughly 65% building, 25% studying, 10% writing runbooks/notes.

## Phase 0 — [Programming Fundamentals](../../modules/foundations/programming-fundamentals.md) (weeks 1–3)

Goal: write clean code without looking up the basics.

## Phase 1 — [Version Control & CLI](../../modules/foundations/version-control-and-cli.md) + [APIs & Backend Services](../../modules/backend/apis-and-services.md) (weeks 4–7)

Goal: a real, authenticated backend service — the shape of what you'll operate for other teams.

## Phase 2 — [Databases & Caching](../../modules/backend/databases-and-caching.md) + [Containers & CI/CD](../../modules/backend/containers-and-ci-cd.md) (weeks 8–10)

Goal: a persistence layer and a CI pipeline — table stakes for everything that follows.

## Phase 3 — [System Design Fundamentals](../../modules/backend/system-design-fundamentals.md) (week 11)

Goal: reason about scaling and reliability at the platform level.

## Phase 4 — [Classical Machine Learning](../../modules/data-and-ml/classical-machine-learning.md) (weeks 12–14)

Goal: enough modeling literacy to support data scientists credibly — not to design models yourself.

## Phase 5 — [ML Model Serving & Production Systems](../../modules/data-and-ml/ml-model-serving-and-production-systems.md) (weeks 15–18)

Goal: the core of the role. Milestone: a versioned, canary-deployable model-serving endpoint with a feature-store-style data path.

## Phase 6 — [MLOps & Cloud AI Platforms](../../modules/platform/mlops-and-cloud-ai-platforms.md) (weeks 19–22)

Goal: experiment tracking, a model registry, and [CI/CD](../../../engineering/concepts/devops/ci-cd.md) gated on model quality, on one cloud's managed stack.

## Phase 7 — [ML Monitoring & Observability](../../modules/platform/ml-monitoring-and-observability.md) (weeks 23–24)

Goal: drift detection, outcome tracking, and a real rollback procedure — the platform's actual job.

## Phase 8 — [Security Fundamentals](../../modules/platform/security-fundamentals.md) (weeks 25–26)

Goal: secure a platform multiple teams deploy models onto.

## Phase 9 — [Soft Skills & Interview Prep](../../modules/career/soft-skills-and-interview-prep.md) (weeks 27–28)

Goal: interview-ready for platform [system design](../../../engineering/concepts/backend/architecture/system-design.md), coding, and behavioral rounds.

## Portfolio

| Project | Built in | Requirement it proves |
| --- | --- | --- |
| Data-cleaning CLI | Phase 0 | Programming fundamentals |
| Authenticated API + CI pipeline | Phase 1–2 | Production-ready backend |
| Versioned, canary-deployable model endpoint | Phase 5 | Model serving platform skill |
| Full MLOps stack (registry, CI/CD, cloud deploy) | Phase 6 | MLOps and cloud platforms |
| Drift detection + rollback runbook | Phase 7 | Platform reliability |

**Presenting it:** one repo, an architecture diagram showing the whole platform (not one model), a runbook for "a model just regressed, what do you do." Use only public or synthetic data.

## Certifications

A cloud DevOps/infrastructure certification matched to the target employer's cloud — see [modules/career/portfolio-and-certifications.md](../../modules/career/portfolio-and-certifications.md).

## Sources

See each linked module's own Resources section for current course/tool recommendations.
