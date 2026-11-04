# Occlusion Handling in Multi-Object Tracking

Occlusion is when a tracked object is fully or partially hidden from a sensor's view — most commonly a camera's, when one person walks behind another, behind an obstacle, or out of frame. It's one of the hardest practical problems in multi-object tracking, because a tracker has no direct observation to work with during the occluded period, only prediction.

## Why occlusion breaks camera-only tracking

```text
Camera view of a crowd:

   👤
   👤👤
   👤👤👤     ← the person in the middle is no longer fully visible
```

A pure detect-then-track pipeline (see [ByteTrack](../ai/computer-vision/bytetrack.md), [BoT-SORT](../ai/computer-vision/bot-sort.md), [SORT](../ai/computer-vision/sort.md)) depends on the detector producing a bounding box every frame. When a person is occluded:

- The detector may miss them entirely for several frames.
- The tracker has to "coast" on its motion prediction (typically a Kalman filter) without new evidence, and if the occlusion lasts too long, the track is lost.
- When the person reappears, the tracker may fail to re-associate them with their previous track, causing an **ID switch** — the same physical person is now treated as a brand-new track, breaking any duration/behavior logic (e.g. a "stationary for 30 seconds" rule) that depended on continuous identity.

Trackers with re-identification (ReID) features, like [BoT-SORT](../ai/computer-vision/bot-sort.md), are specifically designed to reduce ID switches by matching appearance, not just position, when a track reappears — but appearance-based re-matching still fails under full, extended occlusion.

## Why radar complements camera specifically here

A [mmWave radar](../hardware/mmwave-radar.md) doesn't "see" in the visual sense and isn't nearly as blocked by the same obstacles that block a camera's line of sight the same way — radio waves at these frequencies can reflect off or around obstacles that fully occlude an optical view, and a radar mounted overhead ([like an ODS-antenna sensor](../hardware/ti-iwr6843isk-ods.md)) has a different vantage point than a camera mounted at eye level, so the two sensors are rarely occluded by the *same* obstacle at the *same* time:

```text
Camera: person occluded, detection lost
Radar:  track continues uninterrupted (different vantage point, different modality)
        ↓
  Sensor Fusion keeps the identity/position stable through the occlusion
```

This is one of the concrete, practical payoffs of [sensor fusion](sensor-fusion.md) beyond "two opinions are better than one": radar can bridge exactly the gap where a camera-only system loses track continuity.

## Occlusion at scale (crowded scenes)

Both the difficulty and the value of fusion here scale with crowd density. A radar handles a handful of well-separated people cleanly, but as density increases (tens of people in a small area), radar targets themselves start to merge (multiple people appear as one blob in the [point cloud](../hardware/radar-point-cloud.md)), and camera-side occlusion becomes near-constant — so occlusion handling, ID-switch minimization, and fusion all need to be validated specifically against realistic crowded scenarios, not just the sparse cases they're easy to test with.

## Related

- [Sensor Fusion](sensor-fusion.md)
- [Radar Point Cloud](../hardware/radar-point-cloud.md)
- [ByteTrack](../ai/computer-vision/bytetrack.md)
- [BoT-SORT](../ai/computer-vision/bot-sort.md)
- [SORT](../ai/computer-vision/sort.md)
