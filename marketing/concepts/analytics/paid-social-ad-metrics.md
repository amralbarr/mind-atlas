# Paid Social Ad Metrics (Beyond ROAS)

The dashboard of a paid social platform (Meta, TikTok) exposes metrics most advertisers never look at past spend and ROAS. These diagnose *why* an ad is or isn't working, not just whether it is.

## Hook Rate & Hold Rate

For video ads, these two metrics separate "did the ad grab attention" from "did it keep it":

| Metric | Measures | Typical window |
|---|---|---|
| **Hook Rate** | % of people who kept watching past the opening | First 3 seconds |
| **Hold Rate** | % of people who kept watching into the body of the video | 10-15 seconds in |

A low hook rate means the first frame/line failed — fix the opening, not the offer. A good hook rate with a poor hold rate means the opening worked but the content that followed lost people — the payoff didn't match the promise of the hook.

## CTR & Ad Relevance Ranking

- **CTR (Click-Through Rate)** — clicks ÷ impressions. A high CTR signals the creative and targeting are aligned enough that people engage.
- **Ad relevance/quality ranking** — platforms rank an ad's relevance to its audience *relative to competing advertisers* targeting the same audience, usually bucketed as below-average, average, or above-average. A high CTR with a below-average ranking means the audience is engaging, but competitors are doing it more efficiently for the same audience — a targeting or bid problem, not a creative-quality problem in isolation.

## Frequency & Reach

**Frequency** = average number of times a unique person has seen the ad. This isn't automatically bad — it depends on the campaign's objective:

- **Awareness/branding objective** — a *high* frequency can be the goal (staying top-of-mind), so don't kill a campaign just because frequency climbed.
- **Conversion objective** — rising frequency with flat conversions signals ad fatigue; the audience is saturated and it's time to refresh the creative or expand targeting.

## Why These Beat "Just Watching Sales"

A campaign can look fine on sales alone while quietly degrading — a rising Customer Acquisition Cost hidden behind an still-acceptable [MER](marketing-efficiency-ratio-mer.md), or a falling hold rate that will show up as falling conversions next week. Checking hook rate, hold rate, CTR, and relevance ranking *before* the sales number moves is what turns troubleshooting from reactive to preventive.

## Common Questions

**A campaign has a great CTR but no sales — is the creative bad?**
> Not necessarily. High engagement with no conversion usually points downstream — a weak or missing call-to-action, a broken/slow landing page, or an offer that doesn't match what the ad promised. See [CTA & Creative Testing](../digital-marketing/creative-testing-scaling.md).

**Should a campaign be paused the moment ROAS looks worse than another platform's?**
> Not on a single snapshot — different platforms' algorithms behave differently under budget shifts, and comparing a platform's ROAS in isolation (rather than the blended average across all platforms) can lead to cutting a channel that was actually pulling its weight. Compare against your own historical baseline and the blended total, not a single sibling campaign.

## Related

- [Marketing Efficiency Ratio (MER)](marketing-efficiency-ratio-mer.md)
- [Creative Testing & Scaling](../digital-marketing/creative-testing-scaling.md)
- [A/B Testing](ab-testing.md)
