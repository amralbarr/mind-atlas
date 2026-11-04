# ByteTrack

ByteTrack is a multi-object tracking (MOT) algorithm that assigns stable IDs to objects across video frames by associating **almost every detection box** a detector produces — not just the high-confidence ones — with existing tracks. It's a common default tracker to pair with [YOLO](yolo.md) or any other per-frame object detector, since it's a lightweight association layer rather than a separate model that needs its own training.

## The problem it solves

Most earlier tracking-by-detection methods discard any detection below a confidence threshold before doing frame-to-frame association — reasonable in principle (low-confidence boxes are often false positives), but it also throws away real, low-confidence detections of objects that are **partially occluded** or in difficult lighting, causing missed objects and fragmented trajectories exactly when tracking continuity matters most (see [Occlusion Handling in Multi-Object Tracking](../../robotics/occlusion-handling-multi-object-tracking.md)).

## How it works (the "BYTE" association)

ByteTrack runs association in two stages per frame, using a Kalman filter to predict each existing track's expected position:

1. **High-confidence matching**: detections above the confidence threshold are matched to existing tracks by IoU (intersection-over-union) overlap with the Kalman filter's predicted boxes, using the Hungarian algorithm for optimal assignment.
2. **Low-confidence recovery**: detections *below* the threshold — the ones a naive tracker would discard — are matched against whatever tracks remain **unmatched** after step 1. A low-confidence box that overlaps well with an unmatched track's predicted position is very likely that same (occluded/blurry) object reappearing, not noise, and gets recovered rather than dropped.

```text
Detections (all confidences)
        │
  ┌─────┴─────┐
High-conf   Low-conf
  │             │
Match to      Match to tracks still
existing      unmatched after
tracks (IoU)  high-conf pass
  │             │
  └─────┬───────┘
   Updated tracks (IDs preserved through brief occlusion/low-confidence frames)
```

The original implementation pairs this with **YOLOX** as the detector, but the BYTE association method is detector-agnostic and commonly used with any detector's output, including [YOLO](yolo.md).

## When to reach for it

ByteTrack's main advantage is reducing missed detections and fragmented tracks caused by transient occlusion or low detection confidence, at a low computational cost (it adds no appearance/re-identification model, just a smarter two-stage IoU association). It's a strong default when a lightweight, fast tracker is enough and the main failure mode being guarded against is *brief* occlusion. For **camera motion** (a moving/panning camera) or scenarios needing stronger re-identification after longer occlusions, see [BoT-SORT](bot-sort.md).

## Related

- [BoT-SORT](bot-sort.md)
- [SORT](sort.md)
- [Multi-Object Tracking: ByteTrack vs. BoT-SORT vs. SORT](../../../overviews/ai/computer-vision/multi-object-tracking.md)
- [YOLO](yolo.md)
- [Occlusion Handling in Multi-Object Tracking](../../robotics/occlusion-handling-multi-object-tracking.md)
