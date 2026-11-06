# Module: Security Fundamentals

**Category:** Platform · **Typical duration:** 1–2 weeks (15–20 hrs/week) · **Prerequisite modules:** [APIs & Backend Services](../backend/apis-and-services.md)

## Goal

Know the attack surface of a typical web/API system and the standard controls for it — table stakes for any role that touches production data, and mandatory for a regulated-industry job.

## Core topics

- [ ] [Authentication](../../../engineering/concepts/security/auth/authentication.md) vs [authorization](../../../engineering/concepts/security/authorization/authorization.md); sessions, tokens, OAuth flows
- [ ] Common web vulnerabilities and their standard mitigations
- [ ] Secrets management: never in source control, rotation, least-privilege access
- [ ] Input validation and output encoding as a default habit, not an afterthought
- [ ] If relevant to the target role: data-privacy regulation basics (what personal data is, consent, retention) and an AI-specific risk checklist (e.g. [prompt injection](../../../engineering/concepts/security/attacks/prompt-injection.md), data leakage through a model)

## Resources

- A well-known web application security risk list, read in full at least once
- A secrets-management tool's own "why and how" docs

## Milestone deliverable

A short security review of your own portfolio project: one finding per category above (vulnerable or already mitigated), with the fix applied for anything genuinely exploitable.

## Related concepts

Authentication, Authorization, [SQL Injection](../../../engineering/concepts/security/attacks/sql-injection.md), [XSS](../../../engineering/concepts/security/attacks/xss.md), [CSRF](../../../engineering/concepts/security/attacks/csrf.md), Secrets Management
