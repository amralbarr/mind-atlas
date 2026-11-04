# OpenPose

OpenPose, developed by Carnegie Mellon University's Perceptual Computing Lab, is a library for real-time **multi-person** 2D keypoint detection — body, face, hands, and feet — from a single image, and one of the earliest widely-adopted pose-estimation systems. It's written in C++ (OpenCV/Caffe-based), with the reference body model detecting **18 keypoints** (nose, neck, shoulders, elbows, wrists, hips, knees, ankles, eyes, ears).

## What made it notable

Prior multi-person pose approaches typically detected each person first (top-down: detect a person, then run single-person [pose estimation](../../../overviews/ai/computer-vision/pose-estimation.md) on each detected box), which means runtime scales with the number of people in the frame. OpenPose instead uses a **bottom-up** approach — via **Part Affinity Fields (PAFs)**, a representation that encodes both where body parts are *and* how they connect to each other — detecting all keypoints for all people at once and then grouping them into individuals. The practical result is that OpenPose's runtime stays roughly **constant regardless of how many people are in the frame**, unlike top-down approaches (including Mask R-CNN-style [pose estimation](../../../overviews/ai/computer-vision/pose-estimation.md)) whose cost grows linearly with person count — a meaningful advantage for crowded-scene use cases.

## Basic shape of usage

```bash
./build/examples/openpose/openpose.bin --video input.mp4 --write_json output/
```

OpenPose is typically run as a compiled binary/library rather than a lightweight pip-installable package — it's heavier to set up and run than [MediaPipe](mediapipe.md) or [YOLO Pose](yolo.md#pose-estimation-with-yolo), which is the main practical tradeoff against its multi-person bottom-up advantage.

## When it's the right choice

| Scenario | Better fit |
|---|---|
| Crowded scene, many people, need pose for all of them without per-person cost scaling | OpenPose (bottom-up, constant-time) |
| Single person or a handful, prioritizing ease of setup and CPU efficiency | [MediaPipe Pose](mediapipe.md) |
| Already running a [YOLO](yolo.md)-based detection/tracking pipeline and want pose without adding a second framework | [YOLO Pose](yolo.md#pose-estimation-with-yolo) |

See [Pose Estimation: YOLO Pose vs. MediaPipe vs. OpenPose](../../../overviews/ai/computer-vision/pose-estimation.md) for the full comparison, including how each feeds into [temporal action recognition](temporal-action-recognition.md) (e.g. fight/fall detection from a sequence of poses rather than a single frame).

## Related

- [MediaPipe](mediapipe.md)
- [YOLO](yolo.md)
- [Pose Estimation: YOLO Pose vs. MediaPipe vs. OpenPose](../../../overviews/ai/computer-vision/pose-estimation.md)
- [Temporal Action Recognition](temporal-action-recognition.md)
