# Pose Estimation: YOLO Pose vs. MediaPipe vs. OpenPose

Pose estimation predicts the locations of a person's body keypoints (joints, extremities) from an image — the input that most [temporal action recognition](../../../concepts/ai/computer-vision/temporal-action-recognition.md) pipelines (fall detection, fight detection, exercise-rep counting) are actually built on top of, rather than working from raw pixels directly. [YOLO Pose](../../../concepts/ai/computer-vision/yolo.md#pose-estimation-with-yolo), [MediaPipe](../../../concepts/ai/computer-vision/mediapipe.md), and [OpenPose](../../../concepts/ai/computer-vision/openpose.md) are the three options that come up most often. This page compares them and links out to a dedicated note for each rather than describing them in full here.

## At a glance

| | [YOLO Pose](../../../concepts/ai/computer-vision/yolo.md#pose-estimation-with-yolo) | [MediaPipe](../../../concepts/ai/computer-vision/mediapipe.md) | [OpenPose](../../../concepts/ai/computer-vision/openpose.md) |
|---|---|---|---|
| Multi-person | Yes, natively (same as [YOLO](../../../concepts/ai/computer-vision/yolo.md)'s detection) | One person per detected region (needs an external multi-person loop) | Yes, natively — bottom-up (Part Affinity Fields) |
| Runtime scaling with person count | Grows with number of people (same as detection) | Grows with number of people | Roughly constant, regardless of person count |
| Setup/dependency weight | Light — same `ultralytics` package as detection | Light — pure pip install, CPU-friendly | Heavier — typically a compiled C++ binary/library |
| Keypoints | 17 (COCO-style) | 33 | 18 |
| Best fit | Already running a [YOLO](../../../concepts/ai/computer-vision/yolo.md) detection/tracking pipeline; want pose without adding a second framework | Single person or a handful, prioritizing quick setup and CPU efficiency (mobile/edge prototyping) | Genuinely crowded scenes where per-person cost can't scale linearly |

## Choosing

- **Already using [YOLO](../../../concepts/ai/computer-vision/yolo.md) for detection/tracking?** Use [YOLO](../../../concepts/ai/computer-vision/yolo.md) Pose — same package, same API, no second framework to integrate or keep in sync with the detector.
- **Prototyping quickly, especially on constrained hardware (mobile, Raspberry Pi)?** [MediaPipe](../../../concepts/ai/computer-vision/mediapipe.md) — lightweight, CPU-friendly, minimal setup.
- **Genuinely crowded scenes** (tens of people) where a per-person-cost approach would become the bottleneck? [OpenPose](../../../concepts/ai/computer-vision/openpose.md)'s constant-time bottom-up design is built specifically for this, at the cost of a heavier setup.

Whichever is chosen, the output — a sequence of per-person keypoints over time — is what feeds a [temporal action recognition](../../../concepts/ai/computer-vision/temporal-action-recognition.md) model (RNN/LSTM over the pose sequence) to classify actions like a fall or a fight, rather than relying on a single frame's pose in isolation.

## Related

- [YOLO](../../../concepts/ai/computer-vision/yolo.md)
- [MediaPipe](../../../concepts/ai/computer-vision/mediapipe.md)
- [OpenPose](../../../concepts/ai/computer-vision/openpose.md)
- [Temporal Action Recognition](../../../concepts/ai/computer-vision/temporal-action-recognition.md)
- [Multi-Object Tracking: ByteTrack vs. BoT-SORT vs. SORT](multi-object-tracking.md)
