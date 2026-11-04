# Sensor Fusion (Camera + Radar)

Sensor fusion is the practice of combining measurements from multiple, physically different sensors into a single, more reliable picture of the world — rather than trusting either sensor alone, or picking whichever one reports an event first. For a camera + [mmWave radar](../hardware/mmwave-radar.md) system, this means resolving the question: *is the person the camera just detected the same physical object as the track the radar is reporting?*

## Levels of fusion

| Level | What's combined | Tradeoff |
|---|---|---|
| **Data-level (early)** | Raw sensor data before either is interpreted (e.g. [radar point cloud](../hardware/radar-point-cloud.md) projected directly onto raw pixels) | Highest potential accuracy, but very sensitive to calibration/timing error — small misalignment corrupts the fusion |
| **Feature-level (mid)** | Extracted features from each sensor (e.g. detected regions, motion vectors) before final decisions | A middle ground, less common in practice |
| **Object-level (late)** | Each sensor's own independent output — e.g. camera "Person #7 at pixel (420,180), action=aggressive" and radar "Track #3 at (2.4, 4.1, 1.2)m, velocity=2.1m/s" — associated *after* each pipeline has already produced its own detections/tracks | Simpler to build and debug (each sensor pipeline runs independently); what most practical camera-radar systems use, including TI's own reference fusion node |

## The association problem

Object-level fusion's core problem is: given a camera detection and a radar track, decide whether they refer to the same real-world object.

```text
Camera:  Person #7  → bbox [420,180,510,460]
Radar:   Track #3   → x=2.4m, y=4.1m, z=1.2m, velocity=2.1m/s

              ↕  same person?
```

Solving this requires:

1. **[Camera-Radar Calibration](camera-radar-calibration.md)** — a known geometric transform so the radar's 3D position can be projected into the camera's pixel space (or vice versa) for comparison.
2. **[Sensor Synchronization](sensor-synchronization.md)** — both readings need to represent roughly the same instant in time, or a fast-moving person will appear to be in two different places.
3. **Spatial association** — once projected into a common frame, match by proximity (e.g. does the projected radar point fall inside the camera bounding box, or within some distance threshold of its centroid?).
4. **Temporal association** — track the association over multiple frames rather than re-deciding from scratch every frame, so a track doesn't flicker between sensors' momentary disagreements.

## Why object-level fusion, not "whichever sensor says so first"

A weaker design would be: run a camera-only classifier and a radar-only classifier, and alert if *either* fires. This throws away the actual value of having two sensors — each one's weaknesses (a camera's blindness to occlusion/darkness, a radar's inability to tell *what* is happening) simply gets no correction from the other. A fusion layer instead combines *evidence* before making a decision:

```text
Camera Person #7            Radar Track #3
   action=aggressive_motion     velocity=2.1 m/s, closing distance
            └───────────┬───────────┘
                  Fusion Engine
                         │
              spatial + temporal correlation
                         │
                Event Classifier → "possible_fight" (confidence 0.94)
```

This produces stronger, better-substantiated events than either sensor's raw output alone — e.g. "two tracked people moved toward each other at high velocity *and* the camera saw aggressive arm/body motion" is meaningfully stronger evidence than a single video frame classified as "fight."

## Related

- [Camera-Radar Calibration](camera-radar-calibration.md)
- [Sensor Synchronization](sensor-synchronization.md)
- [mmWave Radar](../hardware/mmwave-radar.md)
- [Radar Point Cloud](../hardware/radar-point-cloud.md)
- [Occlusion Handling in Multi-Object Tracking](occlusion-handling-multi-object-tracking.md)
- [Zone-Based Context Engine](zone-based-context-engine.md)
