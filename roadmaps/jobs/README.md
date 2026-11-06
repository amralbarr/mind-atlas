# Jobs

Five complete worked examples of the [roadmap system](../README.md): one folder per job, each holding a `job-profile.md` (filled from [../templates/job-profile-template.md](../templates/job-profile-template.md)) and a `roadmap.md` (filled from [../templates/roadmap-template.md](../templates/roadmap-template.md)) that maps that profile's skills to [../modules/](../modules/) and assembles them into phases with milestones, a portfolio, and certifications. Together they show the same module library producing noticeably different roadmap shapes depending on the role:

- [ai-engineer/](ai-engineer/) ([job-profile.md](ai-engineer/job-profile.md) → [roadmap.md](ai-engineer/roadmap.md)) — Senior AI Engineer / Agentic AI Architect: [LLM](../../engineering/concepts/ai/generation/llm.md)/agentic-heavy, enterprise [RAG](../../engineering/concepts/ai/rag/rag.md) and [multi-agent systems](../../engineering/concepts/ai/agents/multi-agent-systems.md)
- [ml-engineer/](ml-engineer/) ([job-profile.md](ml-engineer/job-profile.md) → [roadmap.md](ml-engineer/roadmap.md)) — Machine Learning Engineer: production ML systems, model serving, MLOps
- [data-scientist/](data-scientist/) ([job-profile.md](data-scientist/job-profile.md) → [roadmap.md](data-scientist/roadmap.md)) — Data Scientist: statistics, experimentation, and stakeholder communication, deliberately light on deployment
- [computer-vision-engineer/](computer-vision-engineer/) ([job-profile.md](computer-vision-engineer/job-profile.md) → [roadmap.md](computer-vision-engineer/roadmap.md)) — Computer Vision Engineer: detection/tracking, real-time and edge deployment
- [mlops-engineer/](mlops-engineer/) ([job-profile.md](mlops-engineer/job-profile.md) → [roadmap.md](mlops-engineer/roadmap.md)) — MLOps / ML Platform Engineer: platform/infrastructure-first, light on model theory

## Adding a new job

Create a new subfolder named for the role (kebab-case, e.g. `data-engineer/`), and inside it a `job-profile.md` and a `roadmap.md` following these same two filenames — that's the whole convention, so any job folder is predictable to find and compose from.
