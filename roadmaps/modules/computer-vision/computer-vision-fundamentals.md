# Module: Computer Vision Fundamentals

**Category:** Computer Vision · **Typical duration:** 4–5 weeks (15–20 hrs/week) · **Prerequisite modules:** [Deep Learning Foundations](../data-and-ml/deep-learning-foundations.md)

## Goal

Go from a raw image or video stream to a working detection/tracking system, and know which model architecture and deployment target fit a given accuracy/latency budget.

## Core topics

- [ ] Image fundamentals: color spaces, filtering/convolution, classic feature descriptors, augmentation techniques
- [ ] CNN architectures for vision tasks, and why modern detectors moved toward transformer-based and real-time designs
- [ ] Core tasks: classification, object detection, segmentation, [pose estimation](../../../engineering/overviews/ai/computer-vision/pose-estimation.md), multi-object tracking
- [ ] A classic computer-vision library for image [I/O](../../../engineering/concepts/programming/fundamentals/io.md), preprocessing, and classical-CV operations
- [ ] Training/[fine-tuning](../../../engineering/concepts/ai/infrastructure/fine-tuning.md) a detector on a custom dataset: annotation formats, augmentation, transfer learning
- [ ] Evaluation metrics: IoU, mAP, precision/recall at a confidence threshold
- [ ] Real-time and edge deployment basics: frame-rate budgets, model export formats, running inference on constrained hardware
- [ ] Multimodal vision tasks at a conceptual level (vision-language models, [OCR](../../../engineering/concepts/ai/ingestion/ocr.md) as a related but distinct pipeline)

## Resources

- A widely-used real-time object detection framework's official docs and training tutorial
- A classic computer-vision library's own tutorial series for the fundamentals
- A public object-detection benchmark's leaderboard, to compare model families on accuracy vs speed

## Milestone deliverable

A real-time object detection and tracking pipeline on a custom or public dataset, with a short evaluation report (mAP, frames per second on your hardware) and a demo video.

## Related concepts

[YOLO](../../../engineering/concepts/ai/computer-vision/yolo.md), [RT-DETR](../../../engineering/concepts/ai/computer-vision/rt-detr.md), [ByteTrack](../../../engineering/concepts/ai/computer-vision/bytetrack.md), [BoT-SORT](../../../engineering/concepts/ai/computer-vision/bot-sort.md), [SORT](../../../engineering/concepts/ai/computer-vision/sort.md), [MediaPipe](../../../engineering/concepts/ai/computer-vision/mediapipe.md), [OpenPose](../../../engineering/concepts/ai/computer-vision/openpose.md), [Temporal Action Recognition](../../../engineering/concepts/ai/computer-vision/temporal-action-recognition.md)
