# YOLO (You Only Look Once)

YOLO is a family of real-time object detection models, maintained today primarily by **Ultralytics**, that predicts bounding boxes and class labels for every object in an image in a single forward pass through the network — the "you only look once" name refers to this, in contrast to older two-stage detectors that first proposed regions and then classified each one separately. It's the default starting point for most real-time object detection work because of its speed/accuracy balance and an unusually polished, batteries-included Python package (`ultralytics`).

## Why it's fast

Older detectors (R-CNN family) ran a separate region-proposal step followed by per-region classification — accurate, but far too slow for real-time video. YOLO instead treats detection as a single regression problem: the whole image goes through one CNN once, and the network directly outputs bounding boxes, objectness scores, and class probabilities for the whole frame at once. This single-pass design is what makes 10–60+ FPS real-time detection practical on commodity hardware, including edge devices.

## Version lineage

| Version | Notes |
|---|---|
| YOLOv3–v7 | Community-driven iterations, several distinct maintainers |
| **YOLOv8** | Ultralytics' unified rewrite — one package/API for detection, segmentation, classification, [pose estimation](../../../overviews/ai/computer-vision/pose-estimation.md), and oriented bounding boxes (OBB); still very widely used and referenced in tutorials/projects |
| YOLO11 | Ultralytics' next generation — higher mAP with fewer parameters than YOLOv8 at comparable model sizes |
| YOLO26 | Latest as of 2026 — adds NMS-free end-to-end inference and edge-deployment optimizations, extends to all detection-family tasks plus depth estimation and open-vocabulary detection |

For new projects, the latest Ultralytics release is generally recommended; YOLOv8 remains extremely common in existing tutorials, papers, and forked repositories, so it's worth recognizing by name even when not the first choice for new work.

## Basic usage (Ultralytics package)

```python
from ultralytics import YOLO

model = YOLO("yolov8n.pt")  # nano variant — fastest, least accurate
results = model("frame.jpg")

for r in results:
    for box in r.boxes:
        print(box.cls, box.conf, box.xyxy)  # class, confidence, bounding box
```

Model size variants (nano/small/medium/large/extra-large) trade accuracy for speed — nano/small are the common choice for real-time or edge deployment (e.g. a [Raspberry Pi + AI HAT+](../../hardware/raspberry-pi-ai-hat.md)), while larger variants are used when accuracy matters more than latency.

## Pose estimation with YOLO

Beyond plain object detection, Ultralytics ships **YOLO Pose** — the same underlying architecture with a pose-estimation head, predicting a fixed set of body keypoints (17, COCO-style) per detected person instead of (or alongside) just a bounding box:

```python
model = YOLO("yolov8n-pose.pt")
results = model("frame.jpg")
keypoints = results[0].keypoints  # per-person keypoint coordinates
```

This is one of several pose-estimation approaches — see [Pose Estimation: YOLO Pose vs. MediaPipe vs. OpenPose](../../../overviews/ai/computer-vision/pose-estimation.md) for how it compares to the alternatives, and [Temporal Action Recognition](temporal-action-recognition.md) for how a sequence of pose keypoints over time becomes an action classification (fall, fight, etc.) rather than a single-frame pose snapshot.

## Where it fits in a detection pipeline

```text
Video frame → YOLO (detection) → bounding boxes + classes
                    │
            Multi-Object Tracker (ByteTrack / BoT-SORT / SORT)
                    │
            Persistent tracked objects (with IDs across frames)
```

YOLO on its own only detects objects *per frame* — it has no notion of identity across frames. Assigning stable IDs over time is a separate job handled by a tracker; see [Multi-Object Tracking: ByteTrack vs. BoT-SORT vs. SORT](../../../overviews/ai/computer-vision/multi-object-tracking.md).

## Related

- [RT-DETR](rt-detr.md) — transformer-based alternative object detector
- [ByteTrack](bytetrack.md) · [BoT-SORT](bot-sort.md) · [SORT](sort.md)
- [MediaPipe](mediapipe.md) · [OpenPose](openpose.md)
- [Temporal Action Recognition](temporal-action-recognition.md)
- [Object Detectors: YOLO vs. RT-DETR](../../../overviews/ai/computer-vision/object-detectors.md)
