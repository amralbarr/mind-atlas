# BoT-SORT

BoT-[SORT](sort.md) ("Robust Associations Multi-Pedestrian Tracking") is a multi-object tracking algorithm that extends [SORT](sort.md)-style tracking-by-detection with two significant additions: **camera motion compensation (CMC)** and **re-identification (ReID)** appearance matching, combined with a more accurate Kalman filter state. It was the first tracker to exceed an IDF1 score of 80 on the MOT17 benchmark, and is a common choice when the extra accuracy is worth the additional compute cost over lighter trackers like [ByteTrack](bytetrack.md).

## What it adds over plain motion-based tracking

| Addition | Problem it solves |
|---|---|
| **Camera Motion Compensation (CMC)** | A moving/panning camera makes every object *appear* to move even when standing still, corrupting a pure motion-prediction (Kalman filter) tracker's assumptions | 
| **ReID (appearance) matching** | Pure position/IoU matching alone can't re-identify an object correctly after it's fully occluded and reappears somewhere its motion model didn't predict |
| **Improved Kalman filter state vector** | A more accurate motion model reduces prediction error between frames, tightening the association step overall |

## How camera motion compensation works

CMC estimates the camera's own motion between frames — via keypoint tracking (pyramidal Lucas-Kanade optical flow) and an affine transform fit with RANSAC to reject outliers — and uses that estimate to adjust the Kalman filter's predicted object positions before matching. This keeps a track's predicted bounding box aligned with the current frame's coordinate system even when the *camera* is the thing moving, not just the tracked objects — relevant for PTZ (pan-tilt-zoom) or handheld/drone camera footage, less relevant for a fixed CCTV mount.

## How ReID matching works

Alongside motion, BoT-SORT computes an appearance embedding for each detected object and uses it as a second signal in the association cost: the assignment cost combines IoU distance with a (conditionally masked) cosine distance between appearance [embeddings](../ingestion/embeddings.md), taking whichever signal is more confident. This is what lets BoT-SORT re-match an object to its correct previous track after occlusion that a pure-motion tracker would have lost or misassigned — directly relevant to the occlusion problem described in [Occlusion Handling in Multi-Object Tracking](../../robotics/occlusion-handling-multi-object-tracking.md).

## Tradeoffs vs. lighter trackers

BoT-SORT reports roughly a 15% tracking-accuracy improvement over conventional [SORT](sort.md)-style trackers in crowded scenes, at the cost of extra computation (the appearance embedding model, and CMC's optical-flow/RANSAC step) that [SORT](sort.md) and [ByteTrack](bytetrack.md) don't pay. For a fixed-mount camera in a moderately crowded scene where compute budget is tight (e.g. an edge device), the simpler [ByteTrack](bytetrack.md) is often "good enough"; for a harder scenario — moving camera, longer occlusions, or accuracy being the priority — BoT-SORT's added robustness is usually worth the cost.

## Related

- [SORT](sort.md)
- [ByteTrack](bytetrack.md)
- [Multi-Object Tracking: ByteTrack vs. BoT-SORT vs. SORT](../../../overviews/ai/computer-vision/multi-object-tracking.md)
- [Occlusion Handling in Multi-Object Tracking](../../robotics/occlusion-handling-multi-object-tracking.md)
