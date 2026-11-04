# A/B Testing

Showing two (or more) versions of something to different segments of an audience at the same time, and measuring which performs better against a defined metric — the core tool for making [CRO](conversion-rate-optimization.md) decisions based on evidence rather than opinion.

## How It Works

1. Pick **one variable** to change (headline, [CTA](../digital-marketing/call-to-action-cta.md) color, form length) — changing multiple things at once makes it impossible to know which change caused the result.
2. Split traffic randomly between **Control (A)** and **Variant (B)**.
3. Run until reaching **statistical significance** — enough sample size that the observed difference is unlikely to be random chance.
4. Ship the winner; if inconclusive, the test didn't have enough traffic/time or the change genuinely didn't matter.

## Statistical Significance (Why It Matters)

A test can show B "winning" by a wide margin on day one purely by chance with a small sample. Statistical significance (commonly a 95% confidence threshold) is the check against declaring a winner too early. Stopping a test as soon as it looks like a winner ("peeking") is one of the most common ways A/B tests produce false results.

## What Makes a Good Test

| Do | Don't |
|---|---|
| Test one variable at a time | Change multiple elements at once (that's a redesign, not a test) |
| Define the success metric before starting | Pick whichever metric happened to move afterward |
| Run for a full business cycle (e.g. a full week, to cover weekday/weekend behavior) | Stop as soon as a lead appears |
| Test high-traffic pages first | Test low-traffic pages where significance takes months to reach |

## A/B Test vs. Multivariate Test

- **A/B test** — one variable, two (or a few) versions.
- **Multivariate test (MVT)** — multiple variables tested in combination simultaneously (e.g. headline × image × [CTA](../digital-marketing/call-to-action-cta.md)), which requires much more traffic to reach significance on each combination but reveals interaction effects a series of A/B tests would miss.

## Common Questions

**Why did a test show a "winner" that didn't hold up over time?**
> Usually the test was stopped too early (before statistical significance), didn't run long enough to cover a full behavior cycle, or the win was a novelty effect that faded once users got used to the change.

**Can A/B testing be used outside of web pages?**
> Yes — email subject lines, ad creative, pricing, even onboarding flows. The same principle (one variable, randomized split, defined success metric) applies anywhere there's enough volume to reach significance.

## Related

- [Conversion Rate Optimization](conversion-rate-optimization.md)
- [Marketing KPIs & Metrics](marketing-kpis-metrics.md)
- [Creative Testing & Scaling](../digital-marketing/creative-testing-scaling.md)
