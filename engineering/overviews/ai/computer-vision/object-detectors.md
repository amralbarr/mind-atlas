# Object Detectors: YOLO vs. RT-DETR

Real-time object detection today mostly comes down to two architectural families: convolutional single-pass detectors (the [YOLO](../../../concepts/ai/computer-vision/yolo.md) lineage) and Transformer-based end-to-end detectors ([RT-DETR](../../../concepts/ai/computer-vision/rt-detr.md)). This page compares them and links out to a dedicated note for each rather than describing them in full here.

## At a glance

| | [YOLO](../../../concepts/ai/computer-vision/yolo.md) | [RT-DETR](../../../concepts/ai/computer-vision/rt-detr.md) |
|---|---|---|
| Architecture | CNN, single-pass | Transformer, end-to-end |
| Post-processing | NMS (non-maximum suppression) required | NMS-free by design |
| Ecosystem maturity | Very large — tooling, tutorials, pretrained checkpoints, edge-deployment support | Smaller, growing (available in the Ultralytics package too) |
| Strongest at | Small/nano model sizes for edge deployment, general-purpose speed | Dense/overlapping-object scenes, where NMS's IoU threshold would otherwise suppress valid detections |
| Also does pose/segmentation | Yes, natively ([YOLO Pose](../../../concepts/ai/computer-vision/yolo.md#pose-estimation-with-yolo), segmentation, OBB) | Detection-focused |

## Choosing

- **Default choice for most real-time detection work, including edge deployment**: [YOLO](../../../concepts/ai/computer-vision/yolo.md) — its ecosystem maturity (pretrained models, deployment tooling, community support) is hard to beat, and its nano/small variants are specifically tuned for constrained hardware like a [Raspberry Pi + AI HAT+](../../../concepts/hardware/raspberry-pi-ai-hat.md).
- **Consider [RT-DETR](../../../concepts/ai/computer-vision/rt-detr.md) when**: the scene has many overlapping or closely-packed objects (e.g. a dense crowd) where NMS is likely to suppress genuinely separate, overlapping detections — [RT-DETR](../../../concepts/ai/computer-vision/rt-detr.md)'s end-to-end design sidesteps that specific failure mode.
- **Both** integrate with the same downstream [multi-object tracking](multi-object-tracking.md) options ([ByteTrack](../../../concepts/ai/computer-vision/bytetrack.md), [BoT-SORT](../../../concepts/ai/computer-vision/bot-sort.md), [SORT](../../../concepts/ai/computer-vision/sort.md)) — the choice of detector and the choice of tracker are independent decisions.

## Related

- [YOLO](../../../concepts/ai/computer-vision/yolo.md)
- [RT-DETR](../../../concepts/ai/computer-vision/rt-detr.md)
- [Multi-Object Tracking: ByteTrack vs. BoT-SORT vs. SORT](multi-object-tracking.md)
- [Pose Estimation: YOLO Pose vs. MediaPipe vs. OpenPose](pose-estimation.md)
