# Radar Point Cloud

A radar point cloud is the per-frame output of the [radar signal processing pipeline](radar-signal-processing-pipeline.md): a sparse set of detected reflection points, each carrying spatial position *and* motion information, rather than the dense grid of pixel intensities a camera produces. It's the fundamental data representation that distinguishes radar sensing from vision, and it's what downstream [tracking](radar-signal-processing-pipeline.md#tracking) and [sensor fusion](../robotics/sensor-fusion.md) logic actually consumes.

## What's in a point

Each point in a radar point cloud typically carries:

| Field | Meaning |
|---|---|
| `x, y, z` | Position relative to the radar, in meters |
| `velocity` (radial) | Instantaneous speed toward/away from the radar (from the Doppler measurement) |
| `SNR` / intensity | Reflection strength — how strong that detection's signature was |
| `range`, `azimuth`, `elevation` | The native polar/spherical coordinates the position was computed from, before conversion to Cartesian |

A single frame's point cloud from a person-tracking radar might contain a few dozen points total — a handful per person, clustered into an object by the pipeline's [clustering stage](radar-signal-processing-pipeline.md#clustering) and then handed to the tracker.

## Point cloud vs. camera pixel data

| | Camera pixel data | Radar point cloud |
|---|---|---|
| Density | Dense — every pixel has a value | Sparse — only actual reflectors produce points |
| What each element carries | Color/intensity | Position (x,y,z) + velocity, directly |
| Velocity | Not directly measured — must be inferred across frames (optical flow, tracking) | Measured per-point, per-frame (Doppler) |
| Identity/appearance | Rich (shape, color, texture) — good for classification | None — a reflection has no visual identity |
| Sensitivity to lighting/occlusion | High | Low |

This is the core reason radar and camera are complementary rather than redundant: a camera's dense pixel grid is what makes it good at *recognizing* things, while a radar point cloud's sparse-but-motion-rich structure is what makes it good at *locating and tracking* things reliably, including through occlusion or darkness. See [mmWave Radar](mmwave-radar.md#why-its-useful-alongside-a-camera) and [Occlusion Handling in Multi-Object Tracking](../robotics/occlusion-handling-multi-object-tracking.md).

## Typical downstream use

```text
Radar Point Cloud (per frame)
        │
   Clustering / association
        │
   Tracked Objects: {track_id, x, y, z, velocity, direction}
        │
   Zone Engine / Sensor Fusion / Event Detection
```

An application rarely works with raw points directly — it consumes the *tracked objects* the pipeline's tracking stage produces from the point cloud stream, since a single frame's point cloud is noisy and only becomes reliable once smoothed and associated across frames.

## Related

- [Radar Signal Processing Pipeline](radar-signal-processing-pipeline.md)
- [mmWave Radar](mmwave-radar.md)
- [Sensor Fusion](../robotics/sensor-fusion.md)
- [Occlusion Handling in Multi-Object Tracking](../robotics/occlusion-handling-multi-object-tracking.md)
