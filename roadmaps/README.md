# Roadmaps

A system for building a custom, zero-to-hero learning roadmap for any job — not one pre-baked path. Most technical roles share large chunks of the same learning curve (programming fundamentals, APIs, databases, cloud). A roadmap for one specific job is a *subset of reusable modules*, composed in dependency order, aimed at a capstone portfolio project that proves every skill the job actually asks for.

## How it works

1. **Capture the job, generically.** Use [templates/job-profile-template.md](templates/job-profile-template.md) to turn a posting into a flat list of required skill categories, seniority, and domain context — with names, companies, and personal fit notes stripped out, since this vault is public. See [jobs/ai-engineer/job-profile.md](jobs/ai-engineer/job-profile.md) for a filled example.
2. **Map skills to modules.** Each required skill category usually maps to one or more files in [modules/](modules/) — see the index and dependency graph in [modules/README.md](modules/README.md). A module no skill maps to doesn't belong in this roadmap; a skill with no matching module means the library needs a new one.
3. **Order by dependency, not by job-description order.** Each module declares its own prerequisite modules. Topologically sort the modules a job needs — this is why "programming fundamentals" is still phase zero of almost every tech roadmap, regardless of job title.
4. **Chain milestones into one capstone.** Every module ends in a milestone deliverable. Pick or design milestones so each one extends the last, so by the final phase they add up to one flagship portfolio project that demonstrates the whole job description, not a pile of disconnected toy exercises.
5. **Write the roadmap.** Use [templates/roadmap-template.md](templates/roadmap-template.md) to assemble the chosen modules into phases with a weekly cadence, a portfolio table, relevant certifications, and an interview-prep closing phase (see [modules/career/soft-skills-and-interview-prep.md](modules/career/soft-skills-and-interview-prep.md)). See [jobs/ai-engineer/roadmap.md](jobs/ai-engineer/roadmap.md) for a complete worked example.

## Adding a new module

A module is reused across many roadmaps, so keep it generic — no company names, no one person's background, no one product's dataset. Give it: a goal, its prerequisite modules, a core-topics checklist, a short resource list (prefer official docs and well-known free courses over any single vendor), a milestone deliverable, and a plain-text "Related concepts" list of vault terms (see "Linking milestones to concepts" below). Add it to the category index and dependency graph in [modules/README.md](modules/README.md).

## Linking milestones to concepts

Module files deliberately do **not** hand-write links into [engineering/concepts/](../engineering/concepts/) — paths drift and get typo'd by hand. Instead, mention the real concept term as plain text (e.g. "[RAG](../engineering/concepts/ai/rag/rag.md)", "[JWT](../engineering/concepts/security/auth/jwt.md)", "[PostgreSQL](../engineering/concepts/databases/relational/postgresql.md)") in the module's prose or its "Related concepts" line, then run the vault's own link sweep from the mind-atlas root to wire it up automatically:

```
python3 runner-script/link_sweep.py --apply --file roadmaps/modules/<category>/<file>.md
```

This scans that one file against the existing vault-wide term index and inserts correct, verified relative links — the same tool [kn-knowledge-agent](../engineering/README.md) uses for the rest of the vault. Run it once per new or edited module file. A term with no matching concept file yet is left as plain text; add the concept file first if it's worth its own note, then re-run the sweep.

## Privacy note

This vault is public. Never paste a real job posting, a company name, interview notes, or anything about a specific person's background/gaps into `roadmaps/`. Genericize first: strip identifying details, keep only the skill list and seniority level. Personal job-hunt material belongs in a private vault instead.

## Contents

- [templates/](templates/) — `job-profile-template.md` (capture a job's required skills) and `roadmap-template.md` (assemble modules into a roadmap)
- [modules/](modules/) — the reusable module library, grouped by category, with a dependency graph
- [jobs/](jobs/) — one subfolder per job (`job-profile.md` + `roadmap.md`), five worked examples
