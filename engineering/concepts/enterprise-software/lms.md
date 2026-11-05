# LMS (Learning Management System)

An LMS is a platform for authoring, delivering, and tracking educational or training content and a learner's progress through it — the central system of record for "who was assigned what, who completed it, and how well." It serves two very different audiences under one umbrella term: corporate L&D (compliance training, onboarding, skills development) and formal education (K-12, higher ed, course delivery) — the underlying capabilities (content hosting, enrollment, progress tracking, assessment) are the same, the context and content differ.

## Core Capabilities

| Capability | What it does |
|---|---|
| **Content authoring/hosting** | Store and serve courses — video, slides, documents, interactive modules, quizzes |
| **Enrollment & cohort management** | Assign content to individuals or groups, track who's enrolled in what |
| **Progress tracking & completion records** | Per-learner record of what's been started, finished, or is overdue |
| **Assessments & quizzes** | Graded or ungraded checks for understanding, often gating progression to later content |
| **Certification & compliance tracking** | Record that a specific person completed specific required training by a specific date — the core requirement for regulated-industry compliance training |
| **Reporting/analytics** | Manager- or admin-facing dashboards on completion rates, scores, time spent |

## Content Interoperability Standards

Courses need to move between authoring tools and LMS platforms without being rebuilt from scratch for each one — this is what the following standards exist to guarantee:

| Standard | What it does | Notes |
|---|---|---|
| **SCORM** (Sharable Content Object Reference Model) | Packages a course so it can be imported into any SCORM-compliant LMS and still report completion/score back correctly | The older, most widely supported standard; limited to tracking what happens *inside* a single packaged course session |
| **xAPI** (Experience API, also called "Tin Can API") | Tracks a much broader range of learning activity — including mobile, simulations, and activity that happens outside the LMS entirely — by sending discrete "statements" (actor-verb-object, e.g. "Amr completed Module 3") to a separate Learning Record Store | Better suited to modern blended/informal learning than SCORM's single-session model |
| **LTI** (Learning Tools Interoperability) | Lets an external tool (a simulation, a publisher's content, a third-party quiz engine) launch seamlessly from inside the LMS with the learner's identity and context already passed through | Common integration layer between an LMS and specialized external content providers |

## Traditional vs. Adaptive LMS

A traditional LMS delivers the same fixed content, in the same order, to every learner — progress tracking is passive, measuring completion of a static path. An **adaptive learning platform** instead adjusts the content, sequencing, or difficulty for each individual learner in real time, based on ongoing assessment of their actual mastery, rather than assuming a fixed pace or a single path fits everyone.

[Area9 Rhapsode](https://area9lyceum.com) is a concrete example: it brands itself as a "four-dimensional" adaptive platform — tracking not just topic mastery but also confidence/metacognition, so a learner who answers correctly but with low confidence is treated differently from one who answers correctly and is sure of it, branching each learner's path individually rather than gating purely on right/wrong answers. It ships as a cloud-based, [SCORM](#content-interoperability-standards)/LTI-compatible platform, meaning it can slot into an existing LMS ecosystem as the adaptive-content layer rather than fully replacing the surrounding LMS.

## Popular LMS Platforms

| Platform | Typical use case |
|---|---|
| **Moodle** | Open-source, highly customizable; common in higher education |
| **Canvas** | Education-focused, widely used in universities |
| **Docebo** | Corporate L&D, strong on AI-driven content recommendations |
| **Absorb LMS** | Corporate training and compliance management |
| **Cornerstone** | Enterprise-scale corporate learning and talent management |
| **TalentLMS / iSpring Learn / Litmos** | Small-to-mid-size corporate training |
| **360Learning** | Collaborative, peer-authored corporate training |

These are listed here as landscape context rather than given individual concept files, since none has come up with enough depth of its own to warrant one yet.

## Deployment Context Matters

The same core LMS feature set serves meaningfully different requirements depending on context: a compliance-training deployment cares most about audit-proof completion records and [access control](../security/authorization/access-control-iam.md) over who can mark what as complete; a higher-ed deployment cares more about gradebooks, cohort structure, and academic integrity; a product-embedded learning deployment (training end users on how to use a SaaS product) cares most about low-friction, in-context delivery rather than formal certification. A platform serving multiple customer organizations on shared infrastructure — most commercial LMS vendors — also has to solve the same tenant-data-isolation problem described in [Multi-Tenancy & Tenant Isolation](../backend/architecture/multi-tenancy.md): one customer's learners, courses, and completion records must never be visible to another customer.

## Common Questions

**Is adaptive learning the same thing as personalized learning?**
> "Personalized" is often used loosely to mean any learner-specific customization (e.g. just letting a learner pick their own course order), while "adaptive" specifically implies the system itself is continuously assessing performance and algorithmically adjusting what comes next — a stricter, narrower claim than personalization in general.

**Why do xAPI and SCORM coexist instead of xAPI fully replacing SCORM?**
> SCORM's huge installed base of existing packaged courses and broad LMS support make it the safe default for simple, self-contained course tracking; xAPI is adopted specifically when a deployment needs to track learning activity SCORM can't reach — mobile apps, simulations, real-world performance data — so most mature LMS ecosystems support both rather than one replacing the other outright.

## Related

- [ERP](erp.md) — an organization's HR/HCM module is often the system that triggers and records assignment into this platform for a given employee, rather than duplicating training-delivery logic itself
- [Multi-Tenancy & Tenant Isolation](../backend/architecture/multi-tenancy.md) — the tenant-isolation problem a multi-customer commercial LMS faces is the same one described there
- [Access Control & IAM](../security/authorization/access-control-iam.md) — compliance-training LMS deployments depend on reliable access/role control over who can mark training complete
- [AI Use Case Prioritization](../ai/infrastructure/ai-use-case-prioritization.md) — relevant when evaluating whether to invest in building an adaptive/AI-personalized learning layer versus a traditional fixed-path LMS
