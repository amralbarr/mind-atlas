# Sensor Synchronization (Timestamp Alignment)

Sensor synchronization is the practice of aligning readings from multiple sensors — each producing data on its own independent clock and frame rate — to the same point in time, so that [sensor fusion](sensor-fusion.md) compares measurements of the *same instant*, not measurements that happen to arrive close together but describe different moments.

## Why it matters

A camera and a radar rarely share a clock or a frame rate out of the box. A camera might deliver frames at 30 FPS; a radar's tracking update rate is often different (and can vary with configuration). If their timestamps aren't reconciled, a fast-moving object can appear to be in two different places at once when its camera detection and its radar position are naively paired:

```text
Camera frame timestamp: 12:00:00.100
Radar frame timestamp:  12:00:00.050
                    ↓
     100ms of unaccounted motion between the two readings
                    ↓
     Camera position at T   paired with   Radar position at T−100ms
                    ↓
          Fusion drifts / associates incorrectly
```

For a person walking at ~1.5 m/s, 100ms of drift is already 15cm of positional error — enough to break a naive nearest-point association, especially with multiple people close together.

## Approaches

| Approach | How it works | Tradeoff |
|---|---|---|
| **Hardware trigger** | A shared signal triggers both sensors' capture simultaneously | Most accurate, requires hardware support on both sensors |
| **Timestamp tagging + interpolation** | Each sensor timestamps its own data on capture (ideally against a shared reference clock, e.g. NTP/PTP-synced); the fusion layer interpolates the slower/offset sensor's readings to match the other's timestamp | Common, software-only, accuracy depends on clock discipline and interpolation quality |
| **Nearest-timestamp matching** | Simply pair each camera frame with whichever radar reading has the closest timestamp | Simplest, adequate when both sensors' rates are similar and objects aren't moving fast relative to the timestamp gap |

## Where this shows up in practice

A radar's tracked-object stream and a camera's detection stream each arrive on their own schedule from independent processes (or independent hardware). Any camera-radar fusion pipeline needs an explicit synchronization step before running [association](sensor-fusion.md#the-association-problem) — either by buffering and interpolating one stream to match the other, or by processing on a shared "tick" that both streams are resampled to. Getting this step right — and not treating "arrived at roughly the same time" as "measured at the same time" — is one of the more overlooked failure points in a camera-radar fusion system, since a synchronization bug degrades fusion accuracy without producing an obvious error.

## Related

- [Sensor Fusion](sensor-fusion.md)
- [Camera-Radar Calibration](camera-radar-calibration.md)
- [mmWave Radar](../hardware/mmwave-radar.md)
