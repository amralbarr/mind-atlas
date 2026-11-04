# Temporal Action Recognition

Temporal action recognition is the practice of classifying an action (fighting, falling, walking, dancing) from a **sequence** of observations over time, rather than from a single frame in isolation. It's the distinction between "does this one frame look like a punch?" and "does this sequence of poses, taken together, look like a fight?" — and it matters because many actions are genuinely ambiguous from a single frame but unambiguous across a sequence.

## Why single-frame classification isn't enough

A single video frame of someone with raised, fast-moving arms could be a punch, a wave, a dance move, or a ball throw — the visual pose alone doesn't disambiguate. What actually distinguishes a fight from a similar-looking action is the **pattern over time**:

```text
Frame 1  → normal standing
Frame 2  → arm raised, fast movement
Frame 3  → contact with another person
Frame 4  → the other person recoils/falls
Frame 5  → repeated aggressive movement
```

A classifier looking at any single one of these frames independently would struggle; a model that sees the *sequence* has far more signal to work with, because the temporal pattern (rapid escalation, contact, a reactive fall) is itself part of what defines the action.

## The typical pipeline

```text
Video frames
     │
Pose estimation (per frame)          ← e.g. YOLO Pose, MediaPipe, OpenPose
     │
Multi-object tracking (per person)   ← e.g. ByteTrack, BoT-SORT, SORT
     │
Sequence of poses per tracked person, over a sliding time window
     │
Temporal model (RNN / LSTM / GRU / Temporal CNN / Transformer)
     │
Action classification (e.g. fight / no-fight, fall / no-fall)
```

The pose-estimation and tracking stages reduce each frame to a compact representation (a skeleton's keypoints, per identified person) instead of raw pixels; the temporal model then looks at how that representation changes across a window of frames. Feeding raw video directly into a 3D-CNN/video-transformer is an alternative approach that skips the explicit pose step, but pose-based pipelines are common specifically because keypoints are a much smaller, more structured input than raw pixels, making the temporal model lighter and the behavior easier to interpret/debug.

## Why an RNN (or similar) over the sequence, not per-frame classification

A per-frame classifier run independently on each frame and then "voted" or thresholded is a weaker approximation of the same idea — it discards the *order* and *transition* information between frames, which is often exactly what separates two visually similar actions (e.g. a fast approach-then-recoil pattern that looks like a fight vs. one that's just two people passing closely). A recurrent model (or other sequence model) is explicitly designed to carry state across time steps, letting it learn the escalation/transition pattern itself rather than relying on any single frame to already look unambiguous.

## Where this fits in a fusion system

In a multi-sensor system, temporal action recognition on pose sequences is typically the camera side's contribution to an event decision, combined with a radar's own motion-over-time signal (velocity, closing distance between two tracked people) via [sensor fusion](../../robotics/sensor-fusion.md) — producing stronger evidence than either the camera's action classification or the radar's motion pattern alone. Radar itself is not well-suited to distinguishing *what kind* of action is happening (fighting vs. running vs. playing look similar in raw motion) — it contributes complementary position/velocity evidence, while the actual action classification is primarily a video/pose problem.

## Related

- [YOLO](yolo.md) ([pose estimation](../../../overviews/ai/computer-vision/pose-estimation.md)) · [MediaPipe](mediapipe.md) · [OpenPose](openpose.md)
- [ByteTrack](bytetrack.md) · [BoT-SORT](bot-sort.md) · [SORT](sort.md)
- [Pose Estimation: YOLO Pose vs. MediaPipe vs. OpenPose](../../../overviews/ai/computer-vision/pose-estimation.md)
- [Sensor Fusion](../../robotics/sensor-fusion.md)
