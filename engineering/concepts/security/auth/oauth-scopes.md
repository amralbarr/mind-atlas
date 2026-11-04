# OAuth Scopes & Least-Privilege Tokens

A **scope** is a named permission a token can carry — `read`, `write:posts`, `admin` — that narrows what an otherwise-valid, correctly-signed token is allowed to do. Scopes are how a token proves *[authentication](authentication.md)* (who/what this is) without automatically granting full *[authorization](../authorization/authorization.md)* (everything that identity could theoretically do).

## Why Scopes Exist

Without scopes, any valid token for a given identity grants that identity's full permission set — a token minted for one narrow purpose (letting a third-party integration read a calendar) would be just as powerful as the user's own full login session if leaked. Scopes let a token be issued for *exactly* the narrow slice of access a specific integration or session needs, so a leak of that token leaks only that slice.

## Ceiling vs. Default: Two Different Scope Concepts

A common design mistake is having only one "allowed scopes" list per integration/client and using it for two different jobs at once — this creates an ambiguity the moment a request doesn't explicitly specify scopes. The fix is two explicit, related fields:

| Field | Meaning |
|---|---|
| **Ceiling / allowed scopes** | The maximum this integration may *ever* be issued, regardless of what a given request asks for |
| **Default scopes** | What gets issued when a request doesn't explicitly specify scopes |

with the invariant `default ⊆ ceiling`, enforced when the ceiling/default pair is configured, not just hoped for at issue time.

## The Narrowed-Sub-Ceiling Trap

When a system has *nested* ceilings (e.g. an organization-level ceiling and a more specific per-key ceiling under it), "fall back to the default when scopes aren't specified" needs to intersect with **every** applicable ceiling, not just the outermost one:

```text
effectiveAllowed = narrowerCeiling ?? widerCeiling
issuedScopes     = requestedScopes ⊆ effectiveAllowed  (if requested explicitly)
                    OR  defaultScopes ∩ effectiveAllowed  (if scopes were omitted)
```

Falling back to the *wider* default when a narrower ceiling exists would silently hand a deliberately-restricted credential more access than whoever restricted it intended — the exact scope-widening bug this formula exists to prevent. Intersection, not a hard rejection, is usually the right behavior for the omitted-scopes case: a narrower credential should be safe and easy to create without also requiring every caller to remember to pass explicit scopes just because some wider default exists elsewhere in the hierarchy.

## Cost/Risk-Based Scope Separation

Scopes shouldn't only mirror CRUD verbs — a good scope model separates actions by *risk or cost profile*, not just by which database table they touch. An action that's cheap and reversible (editing a text field) and one that's expensive or consumes a metered third-party resource (triggering an AI inference call, sending an SMS) deserve separate scopes even if both are nominally "write" operations, so each can be independently granted, throttled, and billed.

## Real-World Example

A real third-party embeddable-widget design implements exactly this two-level ceiling/default/intersection model for a third-party embeddable widget's token scopes, and separately splits "edit a record" from "run an AI-powered action against it" into distinct scopes specifically so a future per-integration cost quota can throttle the AI-cost-bearing scopes independently of ordinary CRUD.

## Common Questions

**Should a scope list be as fine-grained as possible from day one?**
> Not necessarily — an overly granular scope list is hard for integrators to reason about and slows down adoption. Start with the coarsest split that separates genuinely different risk/cost profiles (read vs. write vs. cost-bearing actions), and split further only once a real integration needs that finer control.

**How is a scope different from a role?**
> A role (e.g. "admin," "editor") is usually a bundle of implied permissions tied to a *person's* standing in a system; a scope is typically attached to a *token* for one session or integration, and is meant to be narrower than "everything this person's role allows" — the same person's role might permit far more than any single token they've issued themselves needs to carry.

## Related

- [JWT](jwt.md)
- [Access Control & IAM](../authorization/access-control-iam.md)
- [Policy-Based Authorization](../../backend/data/policy-based-authorization.md)
