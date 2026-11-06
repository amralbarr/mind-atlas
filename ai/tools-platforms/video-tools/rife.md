# RIFE (Real-Time Intermediate Flow Estimation)

**Type:** Open source (MIT) — by Megvii Research

## Category
Video frame interpolation

## AI Capabilities
- Generates new in-between frames from existing ones to raise a video's frame rate (e.g. 24fps → 60/120fps) or produce smooth slow-motion
- Real-time-capable optical-flow-based interpolation, fast enough to run on consumer GPUs
- Self-hosted; "Practical-RIFE" is the actively maintained successor to the original repo, and `rife-ncnn-vulkan` ports let it run on AMD/Intel GPUs, not just NVIDIA

## Related AI Solutions
- [Video Upscaling, Interpolation & Restoration](../../solutions/video/video-enhancement/video-upscaling-interpolation-and-restoration.md)

## Notes
- [FlowFrames](flowframes.md) is the easiest way to run RIFE without the command line.
