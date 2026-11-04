# SORT (Simple Online and Realtime Tracking)

SORT is a lightweight multi-object tracking algorithm — the foundational tracking-by-detection approach that [ByteTrack](bytetrack.md) and [BoT-SORT](bot-sort.md) both build on. It combines a **Kalman filter** for motion prediction with the **Hungarian algorithm** for optimal frame-to-frame detection-to-track assignment, using only the current and immediately previous frame's information — no appearance model, no long-term memory.

## How it works

```text
Frame N:   Existing tracks → Kalman filter predicts each track's position in frame N+1
Frame N+1: New detections arrive
                     │
        Cost matrix: IoU distance between predicted boxes and new detections
                     │
        Hungarian algorithm: optimal one-to-one assignment
                     │
        Matched → update track (Kalman filter correction step)
        Unmatched detection → new track
        Unmatched track → mark as lost (deleted after N missed frames)
```

1. **Kalman filter** predicts where each currently-tracked object should be in the next frame, based on its previous position and velocity.
2. An **IoU-based cost matrix** is built between all predicted track positions and all new detections in the current frame.
3. The **Hungarian algorithm** solves this as an optimal assignment problem, finding the matching that minimizes total cost (equivalent to maximizing total IoU overlap) rather than greedily matching one pair at a time.
4. Matched pairs update the corresponding Kalman filter; unmatched detections start new tracks; unmatched tracks are marked lost and eventually deleted.

## Why it matters

SORT's design — using only the current and previous frame, no appearance/ReID model, no deep learning beyond whatever upstream detector produced the boxes — makes it extremely fast (reported around 260 Hz for the tracking step alone, excluding detection), while still achieving tracking accuracy competitive with far heavier trackers of its era. That simplicity is exactly what [ByteTrack](bytetrack.md) and [BoT-SORT](bot-sort.md) extend rather than replace: [ByteTrack](bytetrack.md) adds a low-confidence-detection recovery pass on top of the same IoU/Kalman/Hungarian core, and [BoT-SORT](bot-sort.md) adds camera motion compensation and appearance-based ReID.

## Limitations

Because SORT relies purely on IoU and motion prediction with no appearance information, it's particularly prone to **ID switches** during occlusion — if a person is occluded for more than a few frames, the Kalman filter's prediction can drift enough that the track is lost, or reassigned to the wrong object entirely when the person reappears. This is precisely the gap [BoT-SORT](bot-sort.md)'s ReID matching and [ByteTrack](bytetrack.md)'s low-confidence recovery were designed to close. See [Occlusion Handling in Multi-Object Tracking](../../robotics/occlusion-handling-multi-object-tracking.md).

## Related

- [ByteTrack](bytetrack.md)
- [BoT-SORT](bot-sort.md)
- [Multi-Object Tracking: ByteTrack vs. BoT-SORT vs. SORT](../../../overviews/ai/computer-vision/multi-object-tracking.md)
- [Occlusion Handling in Multi-Object Tracking](../../robotics/occlusion-handling-multi-object-tracking.md)
