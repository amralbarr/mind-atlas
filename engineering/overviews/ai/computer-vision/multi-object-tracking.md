# Multi-Object Tracking: ByteTrack vs. BoT-SORT vs. SORT

A detector like [YOLO](../../../concepts/ai/computer-vision/yolo.md) finds objects in a single frame but has no concept of identity across frames — a **tracker** is the layer on top that assigns and maintains stable IDs for each object over time. [SORT](../../../concepts/ai/computer-vision/sort.md), [ByteTrack](../../../concepts/ai/computer-vision/bytetrack.md), and [BoT-SORT](../../../concepts/ai/computer-vision/bot-sort.md) are the three most common choices, each extending the one before it. This page compares them and links out to a dedicated note for each rather than describing them in full here.

## At a glance

| | [SORT](../../../concepts/ai/computer-vision/sort.md) | [ByteTrack](../../../concepts/ai/computer-vision/bytetrack.md) | [BoT-SORT](../../../concepts/ai/computer-vision/bot-sort.md) |
|---|---|---|---|
| Core | Kalman filter + Hungarian algorithm, IoU-only | Same core + recovers low-confidence detections | Same core + camera motion compensation + ReID appearance matching |
| Appearance/ReID model | No | No | Yes |
| Handles brief occlusion | Poorly — prone to ID switches | Better — recovers low-confidence (often occluded) detections | Best — appearance matching re-identifies after longer occlusion |
| Handles a moving/panning camera | No compensation | No compensation | Camera motion compensation (CMC) corrects for it |
| Compute cost | Lowest | Low (still no extra model) | Higher (appearance embedding + optical-flow CMC) |
| Speed | Very fast (~260 Hz tracking step alone) | Fast, minimal overhead over [SORT](../../../concepts/ai/computer-vision/sort.md) | Slower than the other two, but still real-time |

## Choosing

- **[SORT](../../../concepts/ai/computer-vision/sort.md)**: when simplicity and raw speed matter most, and occlusion is rare/short (e.g. a sparse scene, well-separated objects).
- **[ByteTrack](../../../concepts/ai/computer-vision/bytetrack.md)**: a strong general-purpose default — meaningfully more robust to brief occlusion than [SORT](../../../concepts/ai/computer-vision/sort.md), at essentially no extra compute cost, since it just changes the association logic rather than adding a model.
- **[BoT-SORT](../../../concepts/ai/computer-vision/bot-sort.md)**: when the camera itself moves (pan/tilt/handheld/drone), or when occlusion is long enough that appearance-based re-identification is needed to avoid ID switches, and the extra compute cost is acceptable.

For a fixed-mount CCTV-style camera with occasional occlusion (people passing in front of each other), [ByteTrack](../../../concepts/ai/computer-vision/bytetrack.md) is usually the practical default; [BoT-SORT](../../../concepts/ai/computer-vision/bot-sort.md) earns its extra cost specifically when camera motion or longer occlusions are expected. See [Occlusion Handling in Multi-Object Tracking](../../../concepts/robotics/occlusion-handling-multi-object-tracking.md) for why occlusion is the central problem all three are, in different ways, trying to solve — and how a second sensing modality like radar can help where all three still fall short.

## Related

- [SORT](../../../concepts/ai/computer-vision/sort.md)
- [ByteTrack](../../../concepts/ai/computer-vision/bytetrack.md)
- [BoT-SORT](../../../concepts/ai/computer-vision/bot-sort.md)
- [Occlusion Handling in Multi-Object Tracking](../../../concepts/robotics/occlusion-handling-multi-object-tracking.md)
- [YOLO](../../../concepts/ai/computer-vision/yolo.md)
