# Zone-Based Context Engine

A zone-based context engine makes a sensing/event system **context-aware** by dividing the physical space it monitors into named zones, and interpreting the same raw event (a person's position, a stationary duration, an entry) differently depending on which zone it happened in. Instead of asking "did something anomalous happen?" in the abstract, it asks "is this behavior normal or dangerous *here*?" — the same underlying design as a software feature flag or permission check that depends on context, applied to physical space instead of application state.

## Why raw detection isn't enough

A person-tracking pipeline (camera and/or [radar](../hardware/mmwave-radar.md)) on its own only produces facts: *a person is at position X, has been stationary for 30 seconds*. Whether that fact matters depends entirely on where X is:

```text
Person stationary for 30s in a waiting area   → Normal
Person stationary for 30s at a closing train door → Suspicious
Person detected inside the restricted track zone  → Critical, regardless of duration
```

Without zone context, a system is forced to either ignore this distinction (missing real danger) or flag everything (drowning operators in false alarms) — see the false-alarm-reduction discussion in [Occlusion Handling in Multi-Object Tracking](occlusion-handling-multi-object-tracking.md) for the related problem of noisy raw detections.

## How it's structured

1. **Define zones** as geometric regions (polygons) in the same coordinate space the fused sensor output already reports positions in — the same coordinate frame established by [camera-radar calibration](camera-radar-calibration.md) if both sensors feed the engine.

   ```text
   ┌────────────────────────────────────┐
   │              PLATFORM               │
   │   [Zone A: Waiting]  [Zone B: Pass.] │
   │   ────────────────────────────────  │
   │           [Zone C: Train Door]       │
   │   ⚠ [Zone D: Restricted / Track] ⚠  │
   └────────────────────────────────────┘
   ```

2. **Attach rules per zone** — a duration threshold, a severity level, or which event types are even relevant there (e.g. "crowd congestion" only matters in the waiting area, not the restricted zone, where *any* presence is already critical).

3. **Combine zone + tracked object + time** to classify severity:

   ```text
   Tracked person position → Zone lookup → Zone rule
             +
        Duration / velocity / other sensor state
             ↓
       Severity: Normal / Attention / Emergency / Critical
   ```

## Relation to geofencing

This is conceptually the same idea as **geofencing** — triggering behavior when a tracked entity enters/exits/lingers in a defined geographic boundary — applied at building/room scale with sensor-derived positions instead of GPS coordinates. The zone polygons, entry/exit/dwell-time logic, and per-zone rule sets are the same underlying pattern either way.

## Related

- [Sensor Fusion](sensor-fusion.md)
- [Camera-Radar Calibration](camera-radar-calibration.md)
- [Occlusion Handling in Multi-Object Tracking](occlusion-handling-multi-object-tracking.md)
- [mmWave Radar](../hardware/mmwave-radar.md)
