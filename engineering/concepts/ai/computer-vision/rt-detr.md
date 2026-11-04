# RT-DETR (Real-Time Detection Transformer)

RT-DETR is a real-time object detector built on a **Transformer** architecture (DETR-style), rather than the convolutional-network design [YOLO](yolo.md) and its predecessors use. Its headline claim — from the paper "DETRs Beat YOLOs on Real-Time Object Detection" — is that it matches or beats [YOLO](yolo.md)'s speed/accuracy tradeoff while eliminating a structural weakness earlier Transformer-based detectors and [YOLO](yolo.md) both share different versions of: heavy reliance on, or the overhead of, non-maximum suppression (NMS).

## Why it's notable relative to YOLO

Earlier DETR-family models were end-to-end (no NMS post-processing needed) but too slow for real-time use. [YOLO](yolo.md) is fast but its accuracy and latency are affected by NMS — the post-processing step that filters overlapping duplicate boxes down to one per object, which is both an extra computation step and a source of tuning sensitivity (the NMS IoU threshold). RT-DETR is the first Transformer-based detector fast enough to be genuinely real-time (reported around 74–108 FPS on a T4 GPU depending on backbone) while keeping the end-to-end, NMS-free design — removing that tuning knob and the associated latency entirely.

## How it compares

| | [YOLO](yolo.md) | RT-DETR |
|---|---|---|
| Architecture | Convolutional (CNN) | Transformer (attention-based) |
| Post-processing | NMS required | End-to-end, NMS-free |
| Strength | Extremely fast at small/nano model sizes, huge ecosystem/tooling maturity | Strong accuracy in complex/cluttered scenes via attention; competitive speed at mid-size models |
| Weakness | NMS can hurt accuracy/latency in dense scenes with overlapping objects | Falls behind [YOLO](yolo.md)'s largest variants in outright accuracy; smaller ecosystem |
| Best fit | General real-time detection, edge deployment, mature tooling needs | Scenes with many overlapping/occluded objects where NMS's IoU cutoff would suppress valid overlapping detections (e.g. a dense crowd) |

## Where it might fit in a crowd/person-detection pipeline

Because attention-based detection handles overlapping objects differently than NMS-based detection, RT-DETR is sometimes considered specifically for **crowded-scene** detection — exactly the scenario where NMS is most likely to incorrectly suppress a real, heavily-overlapping detection (e.g. two people standing very close together). It's available directly in the Ultralytics package alongside [YOLO](yolo.md) models, using the same basic API:

```python
from ultralytics import RTDETR

model = RTDETR("rtdetr-l.pt")
results = model("frame.jpg")
```

## Related

- [YOLO](yolo.md)
- [Object Detectors: YOLO vs. RT-DETR](../../../overviews/ai/computer-vision/object-detectors.md)
- [Multi-Object Tracking: ByteTrack vs. BoT-SORT vs. SORT](../../../overviews/ai/computer-vision/multi-object-tracking.md)
