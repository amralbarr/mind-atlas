# MediaPipe

MediaPipe is Google's open-source framework for building real-time, on-device perception pipelines — face detection, hand tracking, [pose estimation](../../../overviews/ai/computer-vision/pose-estimation.md), and more — designed to run efficiently on CPUs, including mobile and embedded devices, without necessarily needing a GPU. It's distributed as a Python (and JS/Android/iOS) package and is a common default for prototyping pose/vision features quickly, given how little setup it requires compared to training or wiring up a custom model.

## How it's built

MediaPipe models computation as a **directed acyclic graph (DAG)**, where each node is a *Calculator* — a self-contained processing unit taking input streams and producing output streams. A pose pipeline, for instance, chains a person-detection calculator into a landmark-regression calculator, with built-in tracking optimizations: on frames after the first, if tracking confidence stays high, the (more expensive) detection step is skipped entirely and the previous frame's landmarks seed the next landmark regression directly — a meaningful speedup for video versus re-detecting from scratch every frame.

## MediaPipe Pose

The pose-estimation task (built on Google's **BlazePose** model) detects **33 landmarks** on the human body per person in an image or video frame, output in two coordinate systems:

| Output | Meaning |
|---|---|
| `LANDMARKS` | 2D image-pixel coordinates of each landmark |
| `WORLD_LANDMARKS` | 3D real-world coordinates in meters, origin at the center between the hips |

```python
import mediapipe as mp

pose = mp.solutions.pose.Pose()
results = pose.process(frame_rgb)

if results.pose_landmarks:
    for landmark in results.pose_landmarks.landmark:
        print(landmark.x, landmark.y, landmark.z, landmark.visibility)
```

BlazePose is lightweight by design — it doesn't need much compute, which is part of why MediaPipe is a common first choice for prototyping (e.g. fall detection, exercise-rep counting, gesture recognition) before deciding whether a heavier, more accurate model is warranted.

## MediaPipe Pose vs. alternatives

See [Pose Estimation: YOLO Pose vs. MediaPipe vs. OpenPose](../../../overviews/ai/computer-vision/pose-estimation.md) for the full comparison. In short: MediaPipe Pose is single-person per detected region and CPU-friendly; [YOLO Pose](yolo.md#pose-estimation-with-yolo) integrates naturally with a [YOLO](yolo.md)-based multi-person detection pipeline; [OpenPose](openpose.md) handles multi-person pose in a single pass but is heavier to run.

## Related

- [YOLO](yolo.md) (see the pose-estimation section)
- [OpenPose](openpose.md)
- [Pose Estimation: YOLO Pose vs. MediaPipe vs. OpenPose](../../../overviews/ai/computer-vision/pose-estimation.md)
- [Temporal Action Recognition](temporal-action-recognition.md)
