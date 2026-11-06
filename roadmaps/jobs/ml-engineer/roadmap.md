# Example: Machine Learning Engineer Roadmap, Zero to Hero

A worked example of the [roadmap system](../../README.md), assembled from [modules/](../../modules/) for the profile in [job-profile-ml-engineer.md](job-profile.md). Genericized — swap the capstone's use case (recommendations, fraud/risk, forecasting, ranking) for whatever your own target domain actually needs.

## How to use this roadmap

- Total: ~34 weeks at 15–20 hours/week.
- **Fast-track rule:** try each phase's milestone first; skip ahead if you can already build it unaided.
- **Build, don't just watch:** every milestone extends the last into one production-shaped ML system.
- **Weekly rhythm:** roughly 60% building, 30% studying, 10% writing notes.

## Phase 0 — [Programming Fundamentals](../../modules/foundations/programming-fundamentals.md) (weeks 1–3)

Goal: write clean code without looking up the basics.

## Phase 1 — [Version Control & CLI](../../modules/foundations/version-control-and-cli.md) + [APIs & Backend Services](../../modules/backend/apis-and-services.md) (weeks 4–7)

Goal: ship a real authenticated backend service — this becomes the wrapper your model gets served behind later.

## Phase 2 — [Databases & Caching](../../modules/backend/databases-and-caching.md) + [Containers & CI/CD](../../modules/backend/containers-and-ci-cd.md) (weeks 8–9)

Goal: a persistence layer and a CI pipeline for the service skeleton.

## Phase 3 — [Math for ML](../../modules/data-and-ml/math-for-ml.md) → [Classical Machine Learning](../../modules/data-and-ml/classical-machine-learning.md) → [Deep Learning Foundations](../../modules/data-and-ml/deep-learning-foundations.md) (weeks 10–17)

Goal: understand how the models you'll ship actually learn. Milestone: a classical-ML pipeline plus a small neural net trained from scratch.

## Phase 4 — [ML Model Serving & Production Systems](../../modules/data-and-ml/ml-model-serving-and-production-systems.md) (weeks 18–21)

Goal: take a trained model to a versioned, canary-deployable API. Milestone: one of your Phase 3 models served behind an endpoint with a canary rollout path.

## Phase 5 — [System Design Fundamentals](../../modules/backend/system-design-fundamentals.md) (week 22)

Goal: defend the architecture of the system you're building.

## Phase 6 — [MLOps & Cloud AI Platforms](../../modules/platform/mlops-and-cloud-ai-platforms.md) (weeks 23–26)

Goal: experiment tracking, a model registry, and [CI/CD](../../../engineering/concepts/devops/ci-cd.md) gated on model quality, deployed via one cloud's managed ML stack.

## Phase 7 — [ML Monitoring & Observability](../../modules/platform/ml-monitoring-and-observability.md) (weeks 27–28)

Goal: know when a shipped model has gone stale. Milestone: drift detection and an outcome dashboard added to the Phase 4 serving system, with one real alert and a rollback procedure.

## Phase 8 — [Security Fundamentals](../../modules/platform/security-fundamentals.md) (weeks 29–30)

Goal: table-stakes security review of the whole system.

## Phase 9 — [Domain Specialization](../../modules/career/domain-specialization.md) (weeks 31–32)

Goal: fill in the real business use case (recommendations, risk scoring, forecasting — whichever fits your target role) and map it to the system you've built.

## Phase 10 — [Soft Skills & Interview Prep](../../modules/career/soft-skills-and-interview-prep.md) (weeks 33–34)

Goal: interview-ready for ML [system design](../../../engineering/concepts/backend/architecture/system-design.md), coding, and behavioral rounds.

## Portfolio

| Project | Built in | Requirement it proves |
| --- | --- | --- |
| Data-cleaning CLI | Phase 0 | Programming fundamentals |
| Authenticated API skeleton | Phase 1–2 | Production-ready backend |
| Classical ML pipeline + from-scratch neural net | Phase 3 | ML/DL fundamentals |
| Versioned, canary-deployable model API | Phase 4 | Model serving and rollout |
| Full MLOps stack (registry, CI/CD, cloud deploy) | Phase 6 | MLOps and cloud platforms |
| Drift detection + outcome dashboard | Phase 7 | Model monitoring |

**Presenting it:** one repo, an architecture diagram, a results table (model quality metric, p95 latency, rollback time), a short demo. Use only public or synthetic data.

## Certifications

A cloud ML-engineering certification matched to the target employer's cloud — see [modules/career/portfolio-and-certifications.md](../../modules/career/portfolio-and-certifications.md) for the general selection rule.

## Sources

See each linked module's own Resources section for current course/tool recommendations.
