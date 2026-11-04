# Attribution Models

A customer rarely converts from a single touchpoint — they might see a social ad, later click a search ad, then convert from an email. An **attribution model** is the rule used to decide which touchpoint(s) get credit for that conversion, which directly affects which channels look "worth it."

## Common Models

| Model | Credit assignment |
|---|---|
| **Last-click** | 100% to the final touchpoint before conversion |
| **First-click** | 100% to the very first touchpoint |
| **Linear** | Equal credit across every touchpoint |
| **Time-decay** | More credit to touchpoints closer to conversion |
| **Position-based (U-shaped)** | Heavier credit to first and last touch, less to the middle |
| **Data-driven** | Credit assigned algorithmically based on actual observed impact per touchpoint |

## Why the Choice Matters

Last-click is the default in many analytics tools because it's simplest to measure, but it systematically undervalues awareness-stage channels (social, display, content) that start the journey but rarely get the final click. A business relying only on last-click attribution can end up cutting the exact channels that were generating demand in the first place.

## Multi-Touch vs. Single-Touch

- **Single-touch** (first or last-click) is simple but distorts channel value in any journey with more than one touchpoint.
- **Multi-touch** models (linear, time-decay, position-based, data-driven) spread credit more realistically but require more data infrastructure to track a user across channels and devices.

## Practical Limits

Attribution is getting harder, not easier: cross-device journeys, privacy changes (cookie deprecation, iOS tracking restrictions), and "dark social" (sharing via private messages/DMs that can't be tracked) all create gaps no model fully solves. Many teams pair an attribution model with **marketing mix modeling** (statistical modeling of aggregate spend vs. outcomes) to sanity-check what attribution alone can't see.

## Common Questions

**Should a small business bother with multi-touch attribution?**
> Often not worth the infrastructure cost until there are enough channels and enough conversion volume for the extra precision to change a real budget decision — a simpler heuristic (e.g. surveying "how did you hear about us?") can be good enough early on.

**How does attribution relate to CAC?**
> The attribution model directly changes the calculated [CAC](marketing-kpis-metrics.md) per channel — the same spend and conversions can show a very different CAC per channel depending on whether credit is assigned last-click or multi-touch.

## Related

- [Marketing KPIs & Metrics](marketing-kpis-metrics.md)
- [Conversion Rate Optimization](conversion-rate-optimization.md)
- [Customer Journey](../fundamentals/customer-journey.md)
