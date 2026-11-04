# User Acceptance Testing (UAT)

The final validation phase before a feature goes to production. Real users — typically business stakeholders, clients, or a defined subset of end users — test the system against real-world scenarios to confirm it solves the problem it was built for.

UAT answers: "Does this actually do what the business needs?" — not "does the code work?" (unit tests) or "do the components integrate?" (integration tests). A system can pass every automated test and still fail UAT because it solves the wrong problem.

---

## Where UAT Fits in the Testing Pyramid

```
                    [UAT]
               ─────────────────
              [E2E / Integration]
         ──────────────────────────────
        [Unit Tests — fast, isolated, many]
```

| Level | Who runs it | What it validates |
|---|---|---|
| Unit | Developer | One function/class in isolation |
| Integration | Developer / CI | Components work together |
| E2E | QA automation | Full user journeys in a test env |
| **UAT** | **Business users / stakeholders** | **Real-world problem is solved** |

---

## What UAT Tests

UAT tests are written from a business perspective, not a technical one.

**Acceptance criteria** are typically written as user stories:

```
As a compliance officer,
I want to export all AI decisions from the last 30 days,
So that I can provide an audit trail for the regulator.
```

Each story has pass/fail acceptance criteria that UAT validates directly:
- Can the compliance officer find the export button?
- Does the export run to completion without error?
- Is the output in the required format (PDF/Excel)?
- Are all decisions in the date range present?
- Does filtering by department work correctly?

---

## UAT Process

```
1. Define acceptance criteria        ← before development starts
       ↓
2. Prepare UAT environment           ← prod-like data, realistic volume
       ↓
3. Write UAT test cases              ← scenario + expected result + pass/fail
       ↓
4. Execute with real users           ← business stakeholders, not developers
       ↓
5. Log defects                       ← distinction: bug vs. misunderstood requirement
       ↓
6. Fix and re-test                   ← only defects, not scope changes
       ↓
7. Formal sign-off                   ← stakeholder approval → release gate
```

The formal sign-off is the gate. UAT does not end when tests pass — it ends when the business approves.

---

## UAT in AI / LLM Systems

AI systems require an adapted UAT because the output is probabilistic, not deterministic. You cannot write a UAT test that expects an exact string from an [LLM](../../ai/generation/llm.md).

Instead, UAT for AI systems validates:

| Concern | How to test |
|---|---|
| Does it answer the right questions? | Give real user queries, evaluate answer quality |
| Does it correctly refuse unanswerable questions? | Test with out-of-scope queries |
| Are citations accurate and relevant? | Business user reviews source documents |
| Is the tone appropriate for the domain? | Compare against internal communication standards |
| Does it handle Arabic / English correctly? | Native speaker review |
| Is latency acceptable to real users? | Time actual sessions, not synthetic benchmarks |

On the AI Agent Platform, UAT was run with editorial staff before launch. The evaluation set included edge-case queries editorial flagged — questions phrased ambiguously, questions spanning multiple departments, and questions that were deliberately unanswerable. Sign-off required the abstention rate on unanswerable queries to exceed 95%.

---

## UAT vs. QA Testing

A common confusion — UAT is not the QA team's job:

| | QA Testing | UAT |
|---|---|---|
| Who | QA engineers | Business users / stakeholders |
| What | Technical correctness | Business problem solved |
| Environment | Test environment | UAT environment (prod-like) |
| Pass criteria | Tests pass | Stakeholder sign-off |
| Runs | Automated + exploratory | Manual, scenario-driven |
| Timing | Throughout development | Final phase before release |

QA catches bugs. UAT catches requirements mismatches. Both are necessary.

---

## UAT Environment Requirements

The UAT environment must be production-like to give valid results:

- Same data shape as production (not synthetic lorem ipsum)
- Realistic data volume (performance problems only appear at scale)
- Same integrations (auth, external APIs, [message queues](../../distributed-systems/messaging/queues.md))
- Same infra constraints (no developer shortcuts — no `DEBUG=True`)
- No direct database access for testers (they use the UI, not [SQL](../../databases/relational/sql.md))

A UAT environment that diverges too much from production produces results that don't transfer.

---

## Acceptance Criteria Format

Well-written acceptance criteria are testable, specific, and measurable:

```
Given [context / precondition]
When [user action]
Then [expected observable outcome]
```

Example (AI assistant):
```
Given a user has uploaded a 50-page policy document
When they ask "what is the approval threshold for capital expenditure?"
Then the system returns the correct threshold from section 4.2
     and cites the specific clause as a reference
     within 5 seconds
```

Vague acceptance criteria ("the system should be fast") are untestable and always fail UAT by ambiguity.

---

## Related

- [LLM Evaluation](../../ai/evaluation/llm-evaluation.md) — metrics for evaluating AI output quality during UAT
- [Throughput and Latency](../architecture/throughput-and-latency.md) — latency SLAs that UAT performance criteria reference
- [Staged Rollout and Canary Release](staged-rollout.md) — what happens after UAT passes: controlled release to production
