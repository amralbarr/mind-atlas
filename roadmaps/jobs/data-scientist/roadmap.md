# Example: Data Scientist Roadmap, Zero to Hero

A worked example of the [roadmap system](../../README.md), assembled from [modules/](../../modules/) for the profile in [job-profile-data-scientist.md](job-profile.md). Deliberately lighter on backend/deployment modules than the [Machine Learning Engineer](../ml-engineer/roadmap.md) and [AI Engineer](../ai-engineer/roadmap.md) roadmaps — this archetype is graded on analysis and communication, not shipped services.

## How to use this roadmap

- Total: ~22 weeks at 15–20 hours/week.
- **Fast-track rule:** try each phase's milestone first; skip ahead if you can already build it unaided.
- **Build, don't just watch:** every milestone extends the last into one end-to-end analysis portfolio piece.
- **Weekly rhythm:** roughly 50% building/analyzing, 35% studying, 15% writing up findings — the write-up share is higher here than in the engineering-heavy roadmaps, because communicating a finding well is itself the job.

## Phase 0 — [Programming Fundamentals](../../modules/foundations/programming-fundamentals.md) (weeks 1–3)

Goal: write clean code without looking up the basics.

## Phase 1 — [Version Control & CLI](../../modules/foundations/version-control-and-cli.md) (week 4)

Goal: work comfortably in git and the terminal.

## Phase 2 — [Databases & Caching](../../modules/backend/databases-and-caching.md) (weeks 5–6)

Goal: strong [SQL](../../../engineering/concepts/databases/relational/sql.md), since most real analysis starts with a query, not a CSV.

## Phase 3 — [Math for ML](../../modules/data-and-ml/math-for-ml.md) → [Classical Machine Learning](../../modules/data-and-ml/classical-machine-learning.md) (weeks 7–11)

Goal: the statistics and modeling foundation every later analysis leans on.

## Phase 4 — [Data Analysis & Experimentation](../../modules/data-and-ml/data-analysis-and-experimentation.md) (weeks 12–14)

Goal: the core of the role. Milestone: an end-to-end analysis with a properly designed hypothesis/A/B test and a stakeholder-facing report.

## Phase 5 — [Deep Learning Foundations](../../modules/data-and-ml/deep-learning-foundations.md) (weeks 15–17, optional)

Goal: only needed if your target role touches unstructured data (text, images) — skip straight to Phase 6 otherwise.

## Phase 6 — [Domain Specialization](../../modules/career/domain-specialization.md) (weeks 18–19)

Goal: fill in the real business domain's metrics, typical questions, and data quirks.

## Phase 7 — [Soft Skills & Interview Prep](../../modules/career/soft-skills-and-interview-prep.md) (weeks 20–22)

Goal: interview-ready for case-study/analysis interviews, SQL screens, and behavioral rounds.

## Portfolio

| Project | Built in | Requirement it proves |
| --- | --- | --- |
| Data-cleaning CLI | Phase 0 | Programming fundamentals |
| [SQL analytics queries](../../../engineering/concepts/code-samples/sql-analytics-queries/README.md) (cohort/funnel) | Phase 2 | Data-warehouse fluency |
| Classical-ML pipeline with full evaluation | Phase 3 | ML fundamentals |
| End-to-end analysis + A/B test report | Phase 4 | Statistics, experimentation, communication |
| Domain-specific metrics deep dive | Phase 6 | Business/domain fluency |

**Presenting it:** one repo or notebook collection, each analysis with a one-paragraph headline finding before the methodology, and the caveats stated plainly. Use only public or synthetic data.

## Certifications

Rarely decisive for this role — a portfolio of real, well-communicated analyses outweighs a certificate. See [modules/career/portfolio-and-certifications.md](../../modules/career/portfolio-and-certifications.md).

## Sources

See each linked module's own Resources section for current course/tool recommendations.
