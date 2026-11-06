# Module: ML Monitoring & Observability

**Category:** Platform · **Typical duration:** 2 weeks (15–20 hrs/week) · **Prerequisite modules:** [ML Model Serving & Production Systems](../data-and-ml/ml-model-serving-and-production-systems.md)

## Goal

Know when a model deployed last month has quietly stopped being accurate — before a stakeholder finds out from a bad outcome instead of a dashboard.

## Core topics

- [ ] Data drift vs concept drift, and the practical difference between them
- [ ] Input/feature distribution monitoring; detecting a pipeline bug vs a genuine real-world shift
- [ ] Prediction and outcome monitoring: tracking a model's live accuracy once ground truth arrives (which may be delayed by days or months)
- [ ] Alert design for ML systems: what should page someone vs what belongs on a dashboard only
- [ ] Champion/challenger evaluation in production, and a clean rollback path when a new model underperforms
- [ ] Logging enough context per prediction to debug a bad one after the fact, without storing more sensitive data than necessary

## Resources

- An ML-monitoring tool's own docs on drift detection methodology
- A general observability platform's alerting-design guide, applied to a model's prediction/outcome metrics instead of just system metrics

## Milestone deliverable

Add drift detection and an outcome-tracking dashboard to the serving system from [ML Model Serving & Production Systems](../data-and-ml/ml-model-serving-and-production-systems.md), with at least one alert wired to a real threshold and a documented rollback procedure.

## Related concepts

[Staged Rollout](../../../engineering/concepts/backend/delivery/staged-rollout.md)
