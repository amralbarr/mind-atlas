# NIST AI RMF (AI Risk Management Framework)

The NIST AI Risk Management Framework is a voluntary framework published by the U.S. National Institute of Standards and Technology (NIST AI 100-1, January 2023) for identifying, assessing, and managing the risks an AI system poses across its whole lifecycle — not a certification, not a legal requirement, and not specific to any one type of model. It has become a de facto reference standard that many enterprise AI governance programs and vendor risk questionnaires are built around, independent of whether an organization is legally obligated to follow it.

## The four core functions

The framework is organized around four functions, meant to be applied continuously rather than once at launch:

| Function | What it does |
|---|---|
| **Govern** | Cross-cutting, and sits above the other three — establishes the policies, accountability structures, and organizational culture that make the other three functions repeatable rather than ad hoc |
| **Map** | Documents a specific AI system's context, intended use, and the risks that apply to it |
| **Measure** | Assesses and tracks those mapped risks with concrete metrics and evaluation methods |
| **Manage** | Treats identified risks (mitigate, transfer, accept) and responds to incidents when they occur |

Govern is deliberately drawn as sitting above the other three rather than as a fourth peer step — the idea being that Map/Measure/Manage only work consistently across an organization if Govern has already established who's accountable and what the process is.

## The seven characteristics of trustworthy AI

The framework's **Measure** function is built around assessing an AI system against seven characteristics (detailed in the companion NIST AI 100-1 document):

1. **Valid and reliable**
2. **Safe**
3. **Secure and resilient**
4. **Accountable and transparent**
5. **Explainable and interpretable**
6. **Privacy-enhanced**
7. **Fair, with harmful bias managed**

NIST explicitly treats "accountable and transparent" as cutting across all the others rather than as an independent, separately-scorable property, and notes that these characteristics routinely trade off against each other (e.g. a more explainable model can be a less accurate one) — managing AI risk well means making that trade-off deliberately for a given system's context of use, not maximizing every characteristic at once.

## The Generative AI Profile

Published in July 2024 as a companion document (NIST AI 600-1), the **Generative AI Profile** applies the four core functions specifically to generative AI systems, which introduce risks the original 2023 framework didn't name explicitly. It identifies 12 risks unique to, or substantially worsened by, generative AI, each mapped onto Govern/Map/Measure/Manage with suggested actions:

| Risk | What it covers |
|---|---|
| **CBRN Information or Capabilities** | Generative AI lowering the barrier to chemical, biological, radiological, or nuclear threat information |
| **Confabulation** | What this handbook's own [LLM](../../ai/generation/llm.md) note calls hallucination — fluent, confident, fabricated output presented as fact |
| **Dangerous, Violent, or Hateful Content** | Generated content promoting harm, violence, or hatred |
| **Data Privacy** | Training-data memorization and exposure of sensitive or personal information through model outputs |
| **Environmental Impacts** | The energy and resource cost of training and running generative AI systems |
| **Harmful Bias and Homogenization** | Biased outputs, and the narrowing of information diversity as more content is generated rather than authored |
| **Human-AI Configuration** | Risks from how people interact with and rely on AI — over-trust, automation complacency |
| **Information Security** | New attack surfaces generative AI introduces, including [prompt injection](../attacks/prompt-injection.md) and model manipulation |
| **Intellectual Property** | Training-data provenance, output ownership, and infringement risk |
| **Obscene, Degrading, and/or Abusive Content** | Generation of content in this category |
| **Value Chain and Component Integration** | Risk introduced through third-party models, plugins, and components integrated into a generative AI system |
| **(Mis/Dis)information** | Generation and spread of false or misleading content at scale |

An organization adopting the Generative AI Profile starts from the core AI RMF (Govern/Map/Measure/Manage) and layers the profile's 12 GenAI-specific risks and suggested actions on top — the profile doesn't replace the core framework, it specializes it.

## Where this fits next to OWASP's Top 10 for LLM Applications

NIST AI RMF and the [OWASP Top 10 for LLM Applications](owasp-top-10-llm.md) are complementary rather than overlapping replacements for each other: the OWASP list is a concrete, security-engineering-level checklist of specific technical vulnerabilities ([prompt injection](../attacks/prompt-injection.md), insecure output handling, and so on) that a team builds and tests against during development; the NIST framework is a broader, organizational risk-management process covering governance, accountability, and non-security dimensions (fairness, environmental impact, IP) that a security checklist alone was never meant to cover. A mature enterprise AI governance program typically uses the OWASP list to drive technical testing and the NIST framework to drive the surrounding governance process (who signs off, what gets measured, how incidents are tracked) — treating either one as sufficient on its own leaves a real gap the other was designed to close.

## Why this belongs in a technology recommendation's risk section

A recommendation to adopt a specific model, vendor, or architecture is incomplete without naming what risk a reviewer should expect to see addressed — citing the relevant NIST AI RMF functions (e.g. "Measure: fairness evaluated via a held-out demographic-subgroup test set; Manage: an incident-response path exists for a confabulation complaint") turns a vague "we'll be careful" into a reviewable, falsifiable governance claim, the same discipline [AI Use Case Prioritization](../../ai/infrastructure/ai-use-case-prioritization.md)'s own "Risk" criterion asks for when it says a use case's legal/regulatory implications need to be named explicitly rather than assumed away.

## Related

- [OWASP Top 10 for LLM Applications](owasp-top-10-llm.md) — the complementary, security-engineering-level checklist this framework's governance process sits alongside
- [Prompt Injection](../attacks/prompt-injection.md) — the specific attack class named under the Generative AI Profile's "Information Security" risk category
- [HELM](../../ai/evaluation/helm.md) — a benchmark framework that measures several of the same properties (fairness, robustness, safety) this framework names as governance requirements rather than scored metrics
- [LLM Evaluation](../../ai/evaluation/llm-evaluation.md) — the evaluation discipline the Measure function assumes exists; this framework names *what* to measure, not *how*
- [AI Use Case Prioritization](../../ai/infrastructure/ai-use-case-prioritization.md) — the project-level framework whose "Risk" criterion this framework's Govern/Map/Measure/Manage cycle gives concrete substance to
