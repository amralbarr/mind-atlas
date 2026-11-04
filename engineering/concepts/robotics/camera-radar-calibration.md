# Camera-Radar Extrinsic Calibration

Camera-radar calibration is the process of determining the geometric relationship between a camera and a radar's coordinate systems, so a measurement in one sensor's frame can be transformed into the other's — the prerequisite for [sensor fusion](sensor-fusion.md) to work at all. Without it, there's no way to know that a radar point at `(2.4, 4.1, 1.2)` meters corresponds to pixel `(465, 320)` in the camera's image.

## The coordinate mismatch

A camera reports 2D pixel coordinates `(u, v)`; the underlying 3D position along the ray through that pixel is ambiguous without depth. A radar reports genuine 3D position `(x, y, z)` directly, but has no notion of image pixels at all. Fusing the two requires an explicit transform chain:

```text
Radar coordinate system (x, y, z)
            │
   Extrinsic transform (rotation R, translation t)
            │
   Camera coordinate system (x', y', z')
            │
   Camera intrinsics (focal length, principal point)
            │
   Image plane → pixel (u, v)
```

## Intrinsics vs. extrinsics

| | What it describes | How it's obtained |
|---|---|---|
| **Camera intrinsics** | The camera's own internal geometry — focal length, principal point, lens distortion | Standard camera calibration (e.g. a checkerboard pattern, OpenCV's `calibrateCamera`) |
| **Camera-radar extrinsics** | The rigid-body rotation and translation between the radar's origin and the camera's origin — i.e. where the radar physically sits and how it's oriented relative to the camera | Extrinsic calibration, specific to camera-radar fusion |

## How extrinsic calibration is typically done

1. **Target-based**: place a known reflector (often a corner reflector, which radar sees strongly) at measured positions visible to both the camera and radar, and solve for the rotation/translation that minimizes the reprojection error between the radar's reported position and the corresponding pixel location.
2. **Targetless / feature-based**: use naturally-occurring correspondences (e.g. a walking person, tracked simultaneously by both sensors over time) and solve for the transform that best aligns the two sensors' trajectories — more practical for a fixed installation where placing calibration targets repeatedly isn't convenient.

Because this is a **rigid transform** (the radar and camera are mounted at fixed relative positions), it only needs to be solved once per physical installation — not per frame — but must be redone if either sensor is physically moved or re-mounted.

## Why calibration quality matters so much

Fusion accuracy is bounded by calibration accuracy: even a well-designed [association algorithm](sensor-fusion.md#the-association-problem) can't correctly match a camera detection to a radar track if the projected radar position is systematically offset from where it should land in the image. This is consistently one of the hardest parts of building a camera-radar system — errors here don't fail loudly, they just quietly degrade the accuracy of every downstream fusion decision.

## Related

- [Sensor Fusion](sensor-fusion.md)
- [Sensor Synchronization](sensor-synchronization.md)
- [mmWave Radar](../hardware/mmwave-radar.md)
- [Radar Point Cloud](../hardware/radar-point-cloud.md)
