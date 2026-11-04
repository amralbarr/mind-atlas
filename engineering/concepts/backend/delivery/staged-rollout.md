# Staged Rollout and Canary Release

Techniques for deploying changes to production incrementally — exposing the new version to a small percentage of real traffic first, observing for errors, then expanding if everything looks healthy. The alternative to deploying to 100% of users at once.

Both reduce blast radius: if the new version has a bug, only a fraction of users are affected before you catch it and roll back.

---

## The Core Problem They Solve

A full deployment is a binary switch: old version → new version, all users at once. If the new version has a bug:

```
Before:  [Old v1] ──── 100% of traffic ────
After:   [New v2] ──── 100% of traffic ────  ← if v2 is broken, 100% of users hit it
```

With staged rollout:

```
Step 1:  [New v2] ──── 5% of traffic ────
         [Old v1] ──── 95% of traffic ────   ← monitor for errors

Step 2:  [New v2] ──── 25% of traffic ────   ← still healthy? expand
         [Old v1] ──── 75% of traffic ────

Step 3:  [New v2] ──── 100% of traffic ────  ← fully rolled out
```

At each step, you observe metrics before proceeding. A regression at 5% is caught before 95% of your users experience it.

---

## Canary Release

A canary release is a staged rollout where the initial slice is very small (1–5%) and held there long enough to accumulate statistically meaningful signal before expanding.

The name comes from "canary in a coal mine" — a small, early signal of danger.

```
Production traffic:
  ┌─────────────────────────────────────────────────────┐
  │  Canary instances (5%)     │  Stable instances (95%) │
  │  New version               │  Previous version        │
  │  Observed closely          │  Serving majority users  │
  └─────────────────────────────────────────────────────┘
```

What you watch during the canary period:
- Error rate (5xx responses)
- Latency percentiles (P95, P99)
- Business metrics (conversion, session length, feature usage)
- Log output for new error patterns
- Downstream service health

If the canary looks healthy after the observation window (minutes to hours, depending on traffic volume), you promote it.

---

## Canary vs Blue/Green

| | Canary | Blue/Green |
|---|---|---|
| Traffic split | Gradual (5% → 25% → 100%) | Instant full switch |
| Old version | Runs concurrently | Kept idle as fallback |
| Rollback | Shift traffic back | Instant switch to old env |
| Cost | Lower — shares infrastructure | Higher — two full environments |
| Risk | Very low | Low (rollback is fast) |
| Complexity | Higher | Moderate |

Blue/Green is appropriate when the change is high-stakes and you want instant rollback capability (payments, auth, critical APIs). Canary is better when you want gradual validation at real traffic before committing.

---

## Feature Flags vs Staged Rollout

Feature flags are a code-level mechanism for staged rollout — the new code is deployed to all instances, but execution is gated by a runtime flag:

```python
if feature_flags.is_enabled("new_rag_pipeline", user_id=user.id):
    response = new_rag_pipeline.query(question)
else:
    response = legacy_pipeline.query(question)
```

The flag is configured to be `True` for 5% of users, then gradually increased.

| Aspect | Infrastructure staged rollout | Feature flags |
|---|---|---|
| New code location | Separate instances | Same instances |
| Traffic routing | Load balancer / [ingress](../../distributed-systems/kubernetes/ingress.md) | Application code |
| Rollback | Re-route traffic | Flip flag to 0% |
| Granularity | User %, geographic, session | Per user, segment, org, role |
| Complexity | Infrastructure | Code + flag management service |

Feature flags give finer-grained control (e.g., enable for specific enterprise tenants before all users) at the cost of flag debt if not cleaned up.

---

## Staged Rollout After UAT

The deployment sequence for a production-ready feature:

```
UAT passes / stakeholder sign-off
        ↓
Deploy to staging (mirror of production)
        ↓
Smoke test in staging
        ↓
Canary release → 5% of production traffic
        ↓
Observe for [observation window]: errors, latency, business metrics
        ↓
Expand → 25% → 50% → 100%   (or roll back if regression detected)
        ↓
Decommission old version / clean up feature flag
```

For AI systems, the observation window also includes output quality monitoring — a degraded [LLM](../../ai/generation/llm.md) response won't show up as a 5xx, but it will show up as a spike in low-relevance scores or increased user abandonment if you're tracking it.

---

## Automated Rollback

Production-grade deployments define rollback triggers automatically:

```yaml
# Kubernetes rollout with automatic rollback example
strategy:
  type: RollingUpdate
  rollingUpdate:
    maxUnavailable: 0
    maxSurge: 1

# If error rate exceeds threshold, revert automatically
# Typically wired through Argo Rollouts or Flagger:
analysis:
  metrics:
    - name: error-rate
      threshold: 5        # percent
      interval: 1m
  successCondition: result < 5
  failureLimit: 3         # failed checks before rollback
```

Without automated rollback, a canary that goes bad requires human intervention — which takes time while real users are affected.

---

## Related

- [UAT](uat.md) — the validation gate that precedes a staged rollout decision
- [Throughput and Latency](../architecture/throughput-and-latency.md) — the P95/P99 metrics you watch during the canary observation window
- [Observability](../observability/opentelemetry.md) — instrumenting error rate and latency to make canary decisions data-driven
